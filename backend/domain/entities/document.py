"""
Entidades del dominio relacionadas con documentos.
Representa un documento con una o dos caras.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class FaceType(Enum):
    """Tipo de cara de un documento."""
    FRONTAL = "FRONTAL"
    TRASERA = "TRASERA"
    COMPLETO = "COMPLETO"
    MIXTO = "MIXTO"
    DESCONOCIDO = "DESCONOCIDO"


class DocumentType(Enum):
    """Tipo de documento colombiano."""
    CEDULA_CIUDADANIA_VIEJA = "cedula_ciudadania_vieja"
    CEDULA_CIUDADANIA_NUEVA = "cedula_ciudadania_nueva"
    CEDULA_DIGITAL = "cedula_digital"
    TARJETA_IDENTIDAD = "tarjeta_identidad"
    CEDULA_EXTRANJERIA = "cedula_extranjeria"
    PASAPORTE = "pasaporte"
    PPT = "ppt"
    OTRO = "otro"


@dataclass
class DocumentFace:
    """
    Representa una cara de un documento.

    Attributes:
        face_type: Tipo de cara (FRONTAL, TRASERA, COMPLETO, MIXTO)
        image_bytes: Imagen de la cara en bytes
        data: Datos extraídos de esta cara
        page_number: Número de página donde se encontró
        confidence: Nivel de confianza de la clasificación (0.0 a 1.0)
        features: Características detectadas
    """

    face_type: FaceType
    image_bytes: bytes
    data: Dict[str, Any] = field(default_factory=dict)
    page_number: int = 0
    confidence: float = 0.5
    features: Dict[str, bool] = field(default_factory=dict)

    def has_photo(self) -> bool:
        """Retorna True si la cara tiene foto."""
        return self.features.get("has_photo", False)

    def has_signature(self) -> bool:
        """Retorna True si la cara tiene firma."""
        return self.features.get("has_signature", False)

    def has_fingerprint(self) -> bool:
        """Retorna True si la cara tiene huella digital."""
        return self.features.get("has_fingerprint", False)

    def has_number(self) -> bool:
        """Retorna True si la cara tiene número de documento."""
        return self.features.get("has_number", False)

    def is_frontal(self) -> bool:
        """Retorna True si es cara frontal."""
        return self.face_type == FaceType.FRONTAL

    def is_trasera(self) -> bool:
        """Retorna True si es cara trasera."""
        return self.face_type == FaceType.TRASERA

    def is_completo(self) -> bool:
        """Retorna True si es documento completo (1 cara)."""
        return self.face_type == FaceType.COMPLETO

    def is_mixto(self) -> bool:
        """Retorna True si contiene dos caras."""
        return self.face_type == FaceType.MIXTO


@dataclass
class Document:
    """
    Representa un documento lógico construido a partir de una o dos caras.

    Attributes:
        document_type: Tipo de documento
        front_face: Cara frontal del documento
        back_face: Cara trasera del documento (opcional)
        is_complete: Indica si el documento está completo
        is_one_face: Indica si es documento de 1 sola cara
        page_number: Número de página donde se encontró
        merged_data: Datos combinados de todas las caras
    """

    document_type: DocumentType
    front_face: Optional[DocumentFace] = None
    back_face: Optional[DocumentFace] = None
    is_complete: bool = False
    is_one_face: bool = False
    page_number: int = -1
    merged_data: Dict[str, Any] = field(default_factory=dict)

    def has_front_face(self) -> bool:
        """Retorna True si tiene cara frontal."""
        return self.front_face is not None

    def has_back_face(self) -> bool:
        """Retorna True si tiene cara trasera."""
        return self.back_face is not None

    def has_both_faces(self) -> bool:
        """Retorna True si tiene ambas caras."""
        return self.has_front_face() and self.has_back_face()

    def is_two_face_document(self) -> bool:
        """
        Determina si este tipo de documento debería tener 2 caras.

        Returns:
            True si es documento de 2 caras
        """
        two_face_types = [
            DocumentType.CEDULA_CIUDADANIA_VIEJA,
            DocumentType.CEDULA_CIUDADANIA_NUEVA,
            DocumentType.CEDULA_DIGITAL,
            DocumentType.TARJETA_IDENTIDAD,
            DocumentType.CEDULA_EXTRANJERIA
        ]
        return self.document_type in two_face_types

    def add_front_face(self, face: DocumentFace):
        """
        Agrega la cara frontal del documento.

        Args:
            face: Cara frontal a agregar
        """
        self.front_face = face
        if self.page_number == -1:
            self.page_number = face.page_number

    def add_back_face(self, face: DocumentFace):
        """
        Agrega la cara trasera del documento.

        Args:
            face: Cara trasera a agregar
        """
        self.back_face = face

    def mark_complete(self):
        """Marca el documento como completo."""
        self.is_complete = True

    def mark_one_face(self):
        """Marca el documento como de una sola cara."""
        self.is_one_face = True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el documento a un diccionario.

        Returns:
            Diccionario con la información del documento
        """
        return {
            "document_type": self.document_type.value,
            "document_type_display": self.document_type.name.replace("_", " ").title(),
            "front_face": self.front_face.image_bytes if self.front_face else None,
            "back_face": self.back_face.image_bytes if self.back_face else None,
            "is_complete": self.is_complete,
            "is_one_face": self.is_one_face,
            "page_number": self.page_number,
            "merged_data": self.merged_data
        }
