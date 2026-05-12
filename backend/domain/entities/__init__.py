"""
Entidades del dominio.
Contiene objetos centrales de la lógica de negocio.
"""

from .document import Document, DocumentFace
from .validation_result import ValidationError, ValidationResult

__all__ = [
    "Document",
    "DocumentFace",
    "ValidationError",
    "ValidationResult"
]
