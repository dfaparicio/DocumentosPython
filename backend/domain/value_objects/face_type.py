"""
Value Object para tipo de cara de documento.
Encapsula la lógica relacionada con los tipos de caras.
"""

from dataclasses import dataclass
from typing import List
from enum import Enum


class FaceTypeVO(Enum):
    """Tipos de caras de documentos."""

    FRONTAL = "FRONTAL"
    TRASERA = "TRASERA"
    COMPLETO = "COMPLETO"
    MIXTO = "MIXTO"
    DESCONOCIDO = "DESCONOCIDO"

    @classmethod
    def all_types(cls) -> List["FaceTypeVO"]:
        """Retorna la lista de todos los tipos de cara."""
        return list(cls)

    def is_frontal(self) -> bool:
        """Retorna True si es cara frontal."""
        return self == self.FRONTAL

    def is_trasera(self) -> bool:
        """Retorna True si es cara trasera."""
        return self == self.TRASERA

    def is_completo(self) -> bool:
        """Retorna True si es documento completo (1 cara)."""
        return self == self.COMPLETO

    def is_mixto(self) -> bool:
        """Retorna True si contiene dos caras."""
        return self == self.MIXTO

    def is_unknown(self) -> bool:
        """Retorna True si el tipo es desconocido."""
        return self == self.DESCONOCIDO

    @classmethod
    def from_string(cls, value: str) -> "FaceTypeVO":
        """
        Crea un FaceTypeVO desde un string.

        Args:
            value: String que representa el tipo de cara

        Returns:
            FaceTypeVO correspondiente
        """
        try:
            return cls(value.upper())
        except ValueError:
            return cls.DESCONOCIDO
