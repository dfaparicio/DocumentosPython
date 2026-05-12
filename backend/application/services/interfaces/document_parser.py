"""
Interfaz para parsers de documentos.
Permite agregar soporte para diferentes formatos (PDF, Word, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class ParseResult:
    """Resultado de parsear un documento."""

    images: List[bytes]
    total_pages: int
    file_type: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "total_pages": self.total_pages,
            "file_type": self.file_type,
            "metadata": self.metadata
        }


class DocumentParser(ABC):
    """
    Interfaz abstracta para parsers de documentos.

    Implementaciones específicas (PDFParser, WordParser, etc.)
    deben heredar de esta clase.
    """

    @abstractmethod
    def parse(
        self,
        file_bytes: bytes,
        filename: Optional[str] = None
    ) -> ParseResult:
        """
        Parsea un documento y extrae las páginas como imágenes.

        Args:
            file_bytes: Contenido del archivo en bytes
            filename: Nombre del archivo (opcional)

        Returns:
            Resultado del parseo con lista de imágenes

        Raises:
            DocumentParsingError: Si falla el parseo
            PDFParsingError: Si es un error específico de PDF
            WordParsingError: Si es un error específico de Word
        """
        pass

    @abstractmethod
    def can_parse(self, filename: str) -> bool:
        """
        Verifica si este parser puede manejar el archivo.

        Args:
            filename: Nombre del archivo

        Returns:
            True si puede parsear el archivo
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Retorna las extensiones de archivo soportadas.

        Returns:
            Lista de extensiones (ej: [".pdf", ".docx"])
        """
        pass

    @abstractmethod
    def get_supported_mime_types(self) -> List[str]:
        """
        Retorna los tipos MIME soportados.

        Returns:
            Lista de tipos MIME
        """
        pass
