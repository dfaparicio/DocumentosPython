"""
Paquete central de la aplicación.
Contiene excepciones personalizadas, seguridad e inyección de dependencias.

Central package of the application.
Contains custom exceptions, security, and dependency injection.
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
