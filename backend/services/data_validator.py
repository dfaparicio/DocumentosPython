"""
Validador de datos extraidos por IA.
Detecta datos obviamente incorrectos y aplica correcciones automaticas.

Validator for AI-extracted data.
Detects obviously incorrect data and applies automatic corrections.
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

VALID_DOCUMENT_TYPES = [
    "Cédula de Ciudadanía",
    "Cédula Digital", "Tarjeta de Identidad", "Cédula de Extranjería",
    "Pasaporte", "Permiso PPT", "Otro Documento"
]

VALID_INTERNAL_DOC_TYPES = [
    "cedula_ciudadania_vieja", "cedula_ciudadania_nueva",
    "cedula_digital", "tarjeta_identidad", "cedula_extranjeria",
    "pasaporte", "ppt", "contraseña", "otro"
]


@dataclass
class ValidationResult:
    is_valid: bool = True
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    cleaned_data: Dict[str, str] = field(default_factory=dict)
    invalid_fields: List[str] = field(default_factory=list)


def validate_extracted_data(data: Dict[str, str], face_type: str, confidence: float = 1.0) -> ValidationResult:
    """
    Valida los campos extraidos por Gemini.
    Retorna resultado con datos corregidos y lista de problemas.

    Validates the fields extracted by Gemini.
    Returns a result with corrected data and a list of issues.
    """
    result = ValidationResult()
    cleaned = data.copy()

    # Validar cada campo
    # Validate each field
    _validate_numero_documento(cleaned, result)
    _validate_fecha(cleaned, "fecha_nacimiento", result)
    _validate_fecha(cleaned, "fecha_expedicion", result, optional=True)
    _validate_fecha(cleaned, "fecha_vencimiento", result, optional=True)
    _validate_sexo(cleaned, result)
    _validate_nombres_apellidos(cleaned, face_type, result)
    _validate_tipo_documento(cleaned, result)

    if confidence < 0.5:
        result.warnings.append(f"Confianza baja: {confidence:.0%}")

    result.cleaned_data = cleaned

    if result.errors:
        result.is_valid = False

    return result


def _validate_numero_documento(data: Dict, result: ValidationResult):
    numero = data.get("numero_documento", "").strip()
    if not numero:
        return

    # Quitar puntos y espacios para contar digitos utiles
    # Remove dots and spaces to count useful digits
    digits_only = re.sub(r'[.\s\-]', '', numero)

    if len(digits_only) < 6:
        result.errors.append(f"numero_documento muy corto: '{numero}' ({len(digits_only)} digitos)")
        result.invalid_fields.append("numero_documento")
        return

    if len(digits_only) > 15:
        result.warnings.append(f"numero_documento inusualmente largo: {len(digits_only)} caracteres")


def _validate_fecha(data: Dict, field_name: str, result: ValidationResult, optional: bool = False):
    fecha = data.get(field_name, "").strip()
    if not fecha:
        if not optional:
            return  # campo vacio ya se detecta como missing_field en otro lado
            # empty field is already detected as missing_field elsewhere
        return

    # Intentar parsear DD/MM/YYYY
    # Try to parse DD/MM/YYYY
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', fecha)
    if not match:
        # Intentar otros formatos comunes que Gemini podria devolver
        # Try other common formats that Gemini might return
        normalized = _try_normalize_fecha(fecha)
        if normalized:
            data[field_name] = normalized
            fecha = normalized
            match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', fecha)
        else:
            result.warnings.append(f"{field_name} formato no reconocido: '{fecha}'")
            return

    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        current_year = datetime.now().year

        if year < 1900 or year > current_year:
            result.warnings.append(f"{field_name} anho fuera de rango: {year}")
        if month < 1 or month > 12:
            result.errors.append(f"{field_name} mes invalido: {month}")
            result.invalid_fields.append(field_name)
        if day < 1 or day > 31:
            result.errors.append(f"{field_name} dia invalido: {day}")
            result.invalid_fields.append(field_name)


def _try_normalize_fecha(fecha: str) -> Optional[str]:
    """Intenta normalizar una fecha a DD/MM/YYYY.
    Tries to normalize a date to DD/MM/YYYY."""
    # YYYY-MM-DD → DD/MM/YYYY
    match = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', fecha)
    if match:
        return f"{match.group(3)}/{match.group(2)}/{match.group(1)}"

    # DD-MM-YYYY → DD/MM/YYYY
    match = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{4})$', fecha)
    if match:
        return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"

    return None


def _validate_sexo(data: Dict, result: ValidationResult):
    sexo = data.get("sexo", "").strip()
    if not sexo:
        return

    sexo_lower = sexo.lower()
    if sexo_lower in ("m", "masculino", "male"):
        data["sexo"] = "M"
    elif sexo_lower in ("f", "femenino", "female"):
        data["sexo"] = "F"
    else:
        result.warnings.append(f"sexo valor no reconocido: '{sexo}'")
        data["sexo"] = ""


def _validate_nombres_apellidos(data: Dict, face_type: str, result: ValidationResult):
    if face_type not in ("FRONTAL", "COMPLETO", "MIXTO"):
        return

    for field_name in ("nombres", "apellidos"):
        value = data.get(field_name, "").strip()
        if not value:
            continue

        # Si contiene muchos digitos, probablemente es basura
        # If it contains many digits, it's probably garbage
        digit_count = sum(c.isdigit() for c in value)
        if digit_count > len(value) * 0.3 and len(value) > 3:
            result.warnings.append(f"{field_name} contiene numeros: '{value}'")


def _normalize_accents(text: str) -> str:
    """Quita acentos para comparacion tolerante.
    Removes accents for tolerant comparison."""
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
    }
    for accented, plain in replacements.items():
        text = text.replace(accented, plain)
    return text


def _validate_tipo_documento(data: Dict, result: ValidationResult):
    tipo = data.get("tipo_documento", "").strip()
    if not tipo:
        return

    tipo_norm = _normalize_accents(tipo.lower())
    known = False
    for valid in VALID_DOCUMENT_TYPES:
        if tipo_norm == _normalize_accents(valid.lower()) or tipo_norm in _normalize_accents(valid.lower()):
            known = True
            break

    if not known:
        result.warnings.append(f"tipo_documento no reconocido: '{tipo}'")
