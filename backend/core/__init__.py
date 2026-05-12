"""
Paquete central de la aplicación.
Contiene excepciones personalizadas, seguridad e inyección de dependencias.
"""

from .exceptions import (
    DocumentExtractionError,
    AIServiceError,
    AIServiceTimeoutError,
    AIServiceRateLimitError,
    DocumentParsingError,
    PDFParsingError,
    WordParsingError,
    ValidationError,
    InconsistentDocumentError
)

__all__ = [
    "DocumentExtractionError",
    "AIServiceError",
    "AIServiceTimeoutError",
    "AIServiceRateLimitError",
    "DocumentParsingError",
    "PDFParsingError",
    "WordParsingError",
    "ValidationError",
    "InconsistentDocumentError"
]
