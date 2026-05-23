"""
Value Object para tipo de cara de documento.
Encapsula la lógica relacionada con los tipos de caras.

Value Object for document face type.
Encapsulates the logic related to face types.
"""

from dataclasses import dataclass
from typing import List
from enum import Enum


class FaceTypeVO(Enum):
    """Tipos de caras de documentos.
    Document face types."""

    FRONTAL = "FRONTAL"
    TRASERA = "TRASERA"
    COMPLETO = "COMPLETO"
    MIXTO = "MIXTO"
    DESCONOCIDO = "DESCONOCIDO"

    @classmethod
    def all_types(cls) -> List["FaceTypeVO"]:
        """Retorna la lista de todos los tipos de cara.
        Returns the list of all face types."""
        return list(cls)

    def is_frontal(self) -> bool:
        """Retorna True si es cara frontal.
        Returns True if it is the front face."""
        return self == self.FRONTAL

    def is_trasera(self) -> bool:
        """Retorna True si es cara trasera.
        Returns True if it is the back face."""
        return self == self.TRASERA

    def is_completo(self) -> bool:
        """Retorna True si es documento completo (1 cara).
        Returns True if it is a complete document (1 face)."""
        return self == self.COMPLETO

    def is_mixto(self) -> bool:
        """Retorna True si contiene dos caras.
        Returns True if it contains two faces."""
        return self == self.MIXTO

    def is_unknown(self) -> bool:
        """Retorna True si el tipo es desconocido.
        Returns True if the type is unknown."""
        return self == self.DESCONOCIDO

    @classmethod
    def from_string(cls, value: str) -> "FaceTypeVO":
        """
        Crea un FaceTypeVO desde un string.
        Creates a FaceTypeVO from a string.

        Args:
            value: String que representa el tipo de cara / String representing the face type

        Returns:
            FaceTypeVO correspondiente / Corresponding FaceTypeVO
        """
        try:
            return cls(value.upper())
        except ValueError:
            return cls.DESCONOCIDO
