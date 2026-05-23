"""
Value Object para tipo de documento.
Encapsula la lógica relacionada con los tipos de documentos colombianos.

Value Object for document type.
Encapsulates the logic related to Colombian document types.
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class DocumentTypeVO(Enum):
    """Tipos de documentos colombianos soportados.
    Supported Colombian document types."""

    CEDULA_CIUDADANIA_VIEJA = "cedula_ciudadania_vieja"
    CEDULA_CIUDADANIA_NUEVA = "cedula_ciudadania_nueva"
    CEDULA_DIGITAL = "cedula_digital"
    TARJETA_IDENTIDAD = "tarjeta_identidad"
    CEDULA_EXTRANJERIA = "cedula_extranjeria"
    PASAPORTE = "pasaporte"
    PPT = "ppt"
    OTRO = "otro"

    @classmethod
    def two_face_types(cls) -> List["DocumentTypeVO"]:
        """Retorna la lista de tipos de documento que tienen 2 caras.
        Returns the list of document types that have 2 faces."""
        return [
            cls.CEDULA_CIUDADANIA_VIEJA,
            cls.CEDULA_CIUDADANIA_NUEVA,
            cls.CEDULA_DIGITAL,
            cls.TARJETA_IDENTIDAD,
            cls.CEDULA_EXTRANJERIA
        ]

    @classmethod
    def one_face_types(cls) -> List["DocumentTypeVO"]:
        """Retorna la lista de tipos de documento que tienen 1 sola cara.
        Returns the list of document types that have only 1 face."""
        return [
            cls.PASAPORTE,
            cls.PPT,
            cls.OTRO
        ]

    @classmethod
    def all_types(cls) -> List["DocumentTypeVO"]:
        """Retorna la lista de todos los tipos de documentos soportados.
        Returns the list of all supported document types."""
        return list(cls)

    def is_two_face(self) -> bool:
        """Retorna True si este tipo de documento tiene 2 caras.
        Returns True if this document type has 2 faces."""
        return self in self.two_face_types()

    def is_one_face(self) -> bool:
        """Retorna True si este tipo de documento tiene 1 sola cara.
        Returns True if this document type has only 1 face."""
        return self in self.one_face_types()

    def to_display_name(self) -> str:
        """
        Convierte el tipo de documento a un formato legible.
        Converts the document type to a readable format.

        Returns:
            Nombre legible del tipo de documento / Readable name of the document type
        """
        display_names = {
            self.CEDULA_CIUDADANIA_VIEJA: "Cédula de Ciudadanía Vieja",
            self.CEDULA_CIUDADANIA_NUEVA: "Cédula de Ciudadanía Nueva",
            self.CEDULA_DIGITAL: "Cédula Digital",
            self.TARJETA_IDENTIDAD: "Tarjeta de Identidad",
            self.CEDULA_EXTRANJERIA: "Cédula de Extranjería",
            self.PASAPORTE: "Pasaporte",
            self.PPT: "Permiso PPT",
            self.OTRO: "Otro Documento"
        }
        return display_names.get(self, self.value.replace("_", " ").title())

    @classmethod
    def from_string(cls, value: str) -> "DocumentTypeVO":
        """
        Crea un DocumentTypeVO desde un string.
        Creates a DocumentTypeVO from a string.

        Args:
            value: String que representa el tipo de documento / String representing the document type

        Returns:
            DocumentTypeVO correspondiente / Corresponding DocumentTypeVO

        Raises:
            ValueError: Si el string no corresponde a ningún tipo / If the string does not match any type
        """
        try:
            return cls(value)
        except ValueError:
            # Intentar buscar por nombre parcial
            # Try to search by partial name
            for doc_type in cls:
                if doc_type.value == value.lower():
                    return doc_type
            raise ValueError(f"Tipo de documento desconocido: {value}")


# Mapeo de tipos de documento a nombre legible (compatibilidad con código existente)
# Mapping of document types to readable names (compatibility with existing code)
DOCUMENT_TYPE_MAPPING = {
    doc_type.value: doc_type.to_display_name()
    for doc_type in DocumentTypeVO.all_types()
}

TWO_FACE_DOCUMENT_TYPES = [doc_type.value for doc_type in DocumentTypeVO.two_face_types()]
ONE_FACE_DOCUMENT_TYPES = [doc_type.value for doc_type in DocumentTypeVO.one_face_types()]
