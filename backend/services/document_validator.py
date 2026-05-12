"""
Validador de consistencia de documentos.
Valida que las caras de un documento sean consistentes entre sí.
"""

from typing import Dict, List, Optional, Tuple
import re


class ValidationError:
    """Representa un error de validación encontrado."""

    def __init__(self, field: str, message: str, severity: str = "warning"):
        """
        Inicializa un error de validación.

        Args:
            field: Campo donde ocurrió el error
            message: Mensaje descriptivo del error
            severity: Severidad del error ("error", "warning", "info")
        """
        self.field = field
        self.message = message
        self.severity = severity

    def to_dict(self) -> Dict[str, str]:
        """Convierte el error a un diccionario."""
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity
        }


class ValidationResult:
    """Resultado de la validación de un documento."""

    def __init__(self):
        """Inicializa el resultado de validación."""
        self.is_valid: bool = True
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def add_error(self, field: str, message: str):
        """Agrega un error al resultado."""
        self.is_valid = False
        self.errors.append(ValidationError(field, message, "error"))

    def add_warning(self, field: str, message: str):
        """Agrega una advertencia al resultado."""
        self.warnings.append(ValidationError(field, message, "warning"))

    def to_dict(self) -> Dict[str, any]:
        """Convierte el resultado a un diccionario."""
        return {
            "is_valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings]
        }


class DocumentValidator:
    """
    Validador de documentos colombianos.
    """

    def __init__(self):
        """Inicializa el validador de documentos."""
        # Patrón para validar números de documento colombianos
        self.doc_number_pattern = re.compile(r'^[\dA-Za-z-]+$')

        # Patrones para validar fechas
        self.date_pattern_ddmmyyyy = re.compile(r'^\d{2}/\d{2}/\d{4}$')
        self.date_pattern_yyyymmdd = re.compile(r'^\d{4}-\d{2}-\d{2}$')

        # Valores válidos para sexo
        self.valid_sexo_values = ["M", "F", "Masculino", "Femenino", ""]

    def validate_document_consistency(self,
                                      frontal_data: Optional[Dict[str, str]],
                                      trasera_data: Optional[Dict[str, str]],
                                      document_type: str) -> ValidationResult:
        """
        Valida la consistencia entre las caras frontal y trasera de un documento.

        Args:
            frontal_data: Datos de la cara frontal
            trasera_data: Datos de la cara trasera
            document_type: Tipo de documento

        Returns:
            ValidationResult con los errores y advertencias encontrados
        """
        result = ValidationResult()

        # Si no hay datos de ninguna cara, no podemos validar
        if not frontal_data and not trasera_data:
            result.add_error("general", "No hay datos para validar")
            return result

        # Validamos consistencia del número de documento
        if frontal_data and trasera_data:
            self._validate_document_number_consistency(frontal_data, trasera_data, result)

        # Validamos consistencia del tipo de documento
        if frontal_data and trasera_data:
            self._validate_document_type_consistency(frontal_data, trasera_data, result)

        # Validamos los datos individuales
        if frontal_data:
            self._validate_single_face_data(frontal_data, document_type, result, "frontal")

        if trasera_data:
            self._validate_single_face_data(trasera_data, document_type, result, "trasera")

        return result

    def validate_single_document(self,
                                 data: Optional[Dict[str, str]],
                                 document_type: str) -> ValidationResult:
        """
        Valida un documento de una sola cara (ej: pasaporte).

        Args:
            data: Datos del documento
            document_type: Tipo de documento

        Returns:
            ValidationResult con los errores y advertencias encontrados
        """
        result = ValidationResult()

        if not data:
            result.add_error("general", "No hay datos para validar")
            return result

        self._validate_single_face_data(data, document_type, result, "unico")

        return result

    def _validate_document_number_consistency(self,
                                             frontal_data: Dict[str, str],
                                             trasera_data: Dict[str, str],
                                             result: ValidationResult):
        """
        Valida que el número de documento sea consistente entre caras.

        Args:
            frontal_data: Datos de la cara frontal
            trasera_data: Datos de la cara trasera
            result: ValidationResult para agregar errores
        """
        front_num = frontal_data.get("numero_documento", "").strip()
        back_num = trasera_data.get("numero_documento", "").strip()

        if front_num and back_num:
            # Limpiamos los números de espacios y guiones para comparar
            front_num_clean = front_num.replace(" ", "").replace("-", "")
            back_num_clean = back_num.replace(" ", "").replace("-", "")

            if front_num_clean and back_num_clean and front_num_clean != back_num_clean:
                result.add_error(
                    "numero_documento",
                    f"Los números de documento no coinciden: Frontal='{front_num}', Trasera='{back_num}'"
                )
        elif front_num and not back_num:
            result.add_warning("numero_documento", "Número de documento no encontrado en la cara trasera")
        elif not front_num and back_num:
            result.add_warning("numero_documento", "Número de documento no encontrado en la cara frontal")

    def _validate_document_type_consistency(self,
                                           frontal_data: Dict[str, str],
                                           trasera_data: Dict[str, str],
                                           result: ValidationResult):
        """
        Valida que el tipo de documento sea consistente entre caras.

        Args:
            frontal_data: Datos de la cara frontal
            trasera_data: Datos de la cara trasera
            result: ValidationResult para agregar errores
        """
        front_type = frontal_data.get("tipo_documento", "").strip()
        back_type = trasera_data.get("tipo_documento", "").strip()

        if front_type and back_type:
            if front_type != back_type:
                result.add_warning(
                    "tipo_documento",
                    f"Los tipos de documento difieren: Frontal='{front_type}', Trasera='{back_type}'"
                )

    def _validate_single_face_data(self,
                                   data: Dict[str, str],
                                   document_type: str,
                                   result: ValidationResult,
                                   face_label: str):
        """
        Valida los datos de una sola cara.

        Args:
            data: Datos de la cara
            document_type: Tipo de documento
            result: ValidationResult para agregar errores
            face_label: Etiqueta de la cara (para mensajes de error)
        """
        # Validar número de documento
        self._validate_document_number(data, result)

        # Validar nombres y apellidos
        self._validate_names(data, result)

        # Validar fecha de nacimiento
        self._validate_date(data, "fecha_nacimiento", result)

        # Validar sexo
        self._validate_sexo(data, result)

        # Validaciones específicas por tipo de documento
        if document_type == "cedula_extranjeria":
            self._validate_date(data, "fecha_vencimiento", result)
            self._validate_date(data, "fecha_expedicion", result)

        elif document_type == "pasaporte":
            self._validate_date(data, "fecha_vencimiento", result)
            self._validate_date(data, "fecha_expedicion", result)

    def _validate_document_number(self, data: Dict[str, str], result: ValidationResult):
        """
        Valida el formato del número de documento.

        Args:
            data: Datos del documento
            result: ValidationResult para agregar errores
        """
        doc_num = data.get("numero_documento", "").strip()

        if not doc_num:
            result.add_error("numero_documento", "Número de documento no encontrado")
        elif len(doc_num) < 5:
            result.add_error("numero_documento", f"Número de documento muy corto: '{doc_num}'")
        elif not self.doc_number_pattern.match(doc_num):
            result.add_error("numero_documento", f"Número de documento con caracteres inválidos: '{doc_num}'")

    def _validate_names(self, data: Dict[str, str], result: ValidationResult):
        """
        Valida los nombres y apellidos.

        Args:
            data: Datos del documento
            result: ValidationResult para agregar errores
        """
        nombres = data.get("nombres", "").strip()
        apellidos = data.get("apellidos", "").strip()

        if not nombres:
            result.add_warning("nombres", "Nombres no encontrados")

        if not apellidos:
            result.add_warning("apellidos", "Apellidos no encontrados")

    def _validate_date(self, data: Dict[str, str], field_name: str, result: ValidationResult):
        """
        Valida el formato de una fecha.

        Args:
            data: Datos del documento
            field_name: Nombre del campo de fecha
            result: ValidationResult para agregar errores
        """
        date_str = data.get(field_name, "").strip()

        if not date_str:
            return  # Campo opcional

        # Validamos que tenga un formato reconocido
        if not (self.date_pattern_ddmmyyyy.match(date_str) or
                self.date_pattern_yyyymmdd.match(date_str)):
            result.add_warning(field_name, f"Formato de fecha no reconocido: '{date_str}'")

    def _validate_sexo(self, data: Dict[str, str], result: ValidationResult):
        """
        Valida el campo sexo.

        Args:
            data: Datos del documento
            result: ValidationResult para agregar errores
        """
        sexo = data.get("sexo", "").strip()

        if sexo and sexo not in self.valid_sexo_values:
            result.add_warning("sexo", f"Valor de sexo no reconocido: '{sexo}'")

    def is_two_face_document(self, document_type: str) -> bool:
        """
        Determina si un tipo de documento tiene 2 caras.

        Args:
            document_type: Tipo de documento

        Returns:
            True si tiene 2 caras, False si tiene 1 sola cara
        """
        two_face_types = [
            "cedula_ciudadania_vieja",
            "cedula_ciudadania_nueva",
            "cedula_digital",
            "tarjeta_identidad",
            "cedula_extranjeria"
        ]
        return document_type in two_face_types


# Instancia global del validador para reutilizar
_validator_instance = None


def get_validator() -> DocumentValidator:
    """
    Retorna la instancia global del validador (singleton pattern).

    Returns:
        Instancia de DocumentValidator
    """
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = DocumentValidator()
    return _validator_instance


def validate_and_merge(frontal_data: Optional[Dict[str, str]],
                      trasera_data: Optional[Dict[str, str]],
                      document_type: str,
                      validator: Optional[DocumentValidator] = None) -> Tuple[Dict[str, str], ValidationResult]:
    """
    Valida y combina los datos de un documento.

    Args:
        frontal_data: Datos de la cara frontal
        trasera_data: Datos de la cara trasera
        document_type: Tipo de documento
        validator: Instancia del validador (opcional)

    Returns:
        Tupla (datos_combinados, resultado_validacion)
    """
    if validator is None:
        validator = get_validator()

    # Validamos consistencia
    validation_result = validator.validate_document_consistency(
        frontal_data, trasera_data, document_type
    )

    # Combinamos los datos
    from services.data_merger import merge_face_data
    combined_data = merge_face_data(frontal_data, trasera_data, document_type)

    return combined_data, validation_result
