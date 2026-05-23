"""
Paquete de configuración de la aplicación.
Contiene configuraciones centralizadas, logging y constantes.

Application configuration package.
Contains centralized settings, logging, and constants.
"""

from .settings import get_settings, Settings
from .logging_config import setup_logging
from .constants import (
    DOCUMENT_TYPES,
    TWO_FACE_DOCUMENT_TYPES,
    ONE_FACE_DOCUMENT_TYPES,
    EXCEL_COLUMNS,
    DEFAULT_AI_MODEL,
    DEFAULT_DPI,
    MAX_CONCURRENT_AI_REQUESTS,
    MAX_WORKERS,
    AI_REQUEST_TIMEOUT,
    REQUIRED_FIELDS,
    OPTIONAL_FIELDS
)

# Alias para compatibilidad con gemini_provider.py
# Alias for compatibility with gemini_provider.py
DOCUMENT_TYPE_MAPPING = DOCUMENT_TYPES

__all__ = [
    "get_settings",
    "Settings",
    "setup_logging",
    "DOCUMENT_TYPES",
    "DOCUMENT_TYPE_MAPPING",
    "TWO_FACE_DOCUMENT_TYPES",
    "ONE_FACE_DOCUMENT_TYPES",
    "EXCEL_COLUMNS",
    "DEFAULT_AI_MODEL",
    "DEFAULT_DPI",
    "MAX_CONCURRENT_AI_REQUESTS",
    "MAX_WORKERS",
    "AI_REQUEST_TIMEOUT",
    "REQUIRED_FIELDS",
    "OPTIONAL_FIELDS"
]
