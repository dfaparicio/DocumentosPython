"""
Paquete de configuración de la aplicación.
Contiene configuraciones centralizadas, logging y constantes.
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
    AI_REQUEST_TIMEOUT
)

__all__ = [
    "get_settings",
    "Settings",
    "setup_logging",
    "DOCUMENT_TYPES",
    "TWO_FACE_DOCUMENT_TYPES",
    "ONE_FACE_DOCUMENT_TYPES",
    "EXCEL_COLUMNS",
    "DEFAULT_AI_MODEL",
    "DEFAULT_DPI",
    "MAX_CONCURRENT_AI_REQUESTS",
    "MAX_WORKERS",
    "AI_REQUEST_TIMEOUT"
]
