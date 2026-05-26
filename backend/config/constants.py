"""
Constantes de la aplicación.
Consolida mapeos y listas que estaban duplicadas en múltiples archivos.

Application constants.
Consolidates mappings and lists that were duplicated across multiple files.
"""

from typing import Dict, List

# Mapeo de tipos de documento interno a formato legible
# Mapping of internal document types to readable format
DOCUMENT_TYPES: Dict[str, str] = {
    "cedula_ciudadania_vieja": "Cédula de Ciudadanía",
    "cedula_ciudadania_nueva": "Cédula de Ciudadanía",
    "cedula_digital": "Cédula Digital",
    "tarjeta_identidad": "Tarjeta de Identidad",
    "cedula_extranjeria": "Cédula de Extranjería",
    "pasaporte": "Pasaporte",
    "ppt": "Permiso PPT",
    "contraseña": "Cédula de Ciudadanía",
    "otro": "Otro Documento"
}

# Tipos de documento que tienen 2 caras
# Document types that have 2 faces (sides)
TWO_FACE_DOCUMENT_TYPES: List[str] = [
    "cedula_ciudadania_vieja",
    "cedula_ciudadania_nueva",
    "cedula_digital",
    "tarjeta_identidad",
    "cedula_extranjeria"
]

# Tipos de documento que tienen 1 sola cara
# Document types that have only 1 face (side)
ONE_FACE_DOCUMENT_TYPES: List[str] = [
    "pasaporte",
    "ppt",
    "otro"
]

# Tipos de cara de documento
# Document face types
FACE_TYPES = ["FRONTAL", "TRASERA", "COMPLETO", "MIXTO", "DESCONOCIDO"]

# Orden de columnas para Excel
# Column order for Excel
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
# Required fields for all documents
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
# Optional fields
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
# Default AI configuration
DEFAULT_AI_MODEL = "gemini-2.5-flash"

# Configuración por defecto para conversión de PDF
# Default configuration for PDF conversion
DEFAULT_DPI = 100

# Límites de concurrencia
# Concurrency limits
MAX_CONCURRENT_AI_REQUESTS = 5
MAX_WORKERS = 4

# Timeout para llamadas a IA (segundos)
# Timeout for AI calls (seconds)
AI_REQUEST_TIMEOUT = 30


def is_two_face_document(document_type: str) -> bool:
    """
    Determina si un tipo de documento tiene 2 caras.

    Determines whether a document type has 2 faces (sides).

    Args:
        document_type: Tipo de documento
            Document type

    Returns:
        True si tiene 2 caras, False si tiene 1 sola cara
        True if it has 2 faces, False if it has only 1 face
    """
    return document_type in TWO_FACE_DOCUMENT_TYPES


def format_document_type(document_type: str) -> str:
    """
    Convierte el tipo de documento interno a formato legible.

    Converts the internal document type to readable format.

    Args:
        document_type: Tipo de documento interno
            Internal document type

    Returns:
        Tipo de documento formateado
        Formatted document type
    """
    return DOCUMENT_TYPES.get(document_type, document_type.replace("_", " ").title())


def get_all_document_types() -> List[str]:
    """Retorna la lista de todos los tipos de documentos soportados.

    Returns the list of all supported document types.
    """
    return list(DOCUMENT_TYPES.keys())
