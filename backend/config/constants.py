"""
Constantes de la aplicación.
Consolida mapeos y listas que estaban duplicadas en múltiples archivos.
"""

from typing import Dict, List

# Mapeo de tipos de documento interno a formato legible
DOCUMENT_TYPES: Dict[str, str] = {
    "cedula_ciudadania_vieja": "Cédula de Ciudadanía Vieja",
    "cedula_ciudadania_nueva": "Cédula de Ciudadanía Nueva",
    "cedula_digital": "Cédula Digital",
    "tarjeta_identidad": "Tarjeta de Identidad",
    "cedula_extranjeria": "Cédula de Extranjería",
    "pasaporte": "Pasaporte",
    "ppt": "Permiso PPT",
    "otro": "Otro Documento"
}

# Tipos de documento que tienen 2 caras
TWO_FACE_DOCUMENT_TYPES: List[str] = [
    "cedula_ciudadania_vieja",
    "cedula_ciudadania_nueva",
    "cedula_digital",
    "tarjeta_identidad",
    "cedula_extranjeria"
]

# Tipos de documento que tienen 1 sola cara
ONE_FACE_DOCUMENT_TYPES: List[str] = [
    "pasaporte",
    "ppt",
    "otro"
]

# Tipos de cara de documento
FACE_TYPES = ["FRONTAL", "TRASERA", "COMPLETO", "MIXTO", "DESCONOCIDO"]

# Orden de columnas para Excel
EXCEL_COLUMNS: List[str] = [
    "Tipo de Documento",
    "Número de Documento",
    "Nombres",
    "Apellidos",
    "Fecha de Nacimiento",
    "Sexo",
    "Nacionalidad"
]

# Campos obligatorios para todos los documentos
REQUIRED_FIELDS: List[str] = [
    "tipo_documento",
    "numero_documento",
    "nombres",
    "apellidos",
    "fecha_nacimiento",
    "sexo",
    "nacionalidad"
]

# Campos opcionales
OPTIONAL_FIELDS: List[str] = [
    "fecha_expedicion",
    "fecha_vencimiento",
    "lugar_expedicion",
    "lugar_nacimiento",
    "huella_digital",
    "firma",
    "codigo_qr",
    "datos_biometricos",
    "grupo_sanguineo",
    "tipo_visa"
]

# Configuración por defecto para IA
DEFAULT_AI_MODEL = "gemini-1.5-flash"

# Configuración por defecto para conversión de PDF
DEFAULT_DPI = 150

# Límites de concurrencia
MAX_CONCURRENT_AI_REQUESTS = 5
MAX_WORKERS = 4

# Timeout para llamadas a IA (segundos)
AI_REQUEST_TIMEOUT = 30


def is_two_face_document(document_type: str) -> bool:
    """
    Determina si un tipo de documento tiene 2 caras.

    Args:
        document_type: Tipo de documento

    Returns:
        True si tiene 2 caras, False si tiene 1 sola cara
    """
    return document_type in TWO_FACE_DOCUMENT_TYPES


def format_document_type(document_type: str) -> str:
    """
    Convierte el tipo de documento interno a formato legible.

    Args:
        document_type: Tipo de documento interno

    Returns:
        Tipo de documento formateado
    """
    return DOCUMENT_TYPES.get(document_type, document_type.replace("_", " ").title())


def get_all_document_types() -> List[str]:
    """Retorna la lista de todos los tipos de documentos soportados."""
    return list(DOCUMENT_TYPES.keys())
