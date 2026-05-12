"""
Value Objects del dominio.
Contiene objetos de valor que representan conceptos importantes en el dominio.
"""

from .document_type import DocumentTypeVO
from .face_type import FaceTypeVO
from .extraction_data import ExtractionData

__all__ = [
    "DocumentTypeVO",
    "FaceTypeVO",
    "ExtractionData"
]
