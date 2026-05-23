"""
Interfaz para parsers de documentos.
Permite agregar soporte para diferentes formatos (PDF, Word, etc.).

Interface for document parsers.
Allows adding support for different formats (PDF, Word, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class ParseResult:
    """Resultado de parsear un documento.
    Result of parsing a document."""

    images: List[bytes]
    total_pages: int
    file_type: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario.
        Converts to dictionary."""
        return {
            "total_pages": self.total_pages,
            "file_type": self.file_type,
            "metadata": self.metadata
        }


class DocumentParser(ABC):
    """
    Interfaz abstracta para parsers de documentos.
    Specific implementations (PDFParser, WordParser, etc.)
    deben heredar de esta clase.

    Abstract interface for document parsers.
    Specific implementations (PDFParser, WordParser, etc.)
    must inherit from this class.
    """

    @abstractmethod
    def parse(
        self,
        file_bytes: bytes,
        filename: Optional[str] = None
    ) -> ParseResult:
        """
        Parsea un documento y extrae las páginas como imágenes.
        Parses a document and extracts pages as images.

        Args:
            file_bytes: Contenido del archivo en bytes / File content in bytes
            filename: Nombre del archivo (opcional) / File name (optional)

        Returns:
            Resultado del parseo con lista de imágenes / Parse result with list of images

        Raises:
            DocumentParsingError: Si falla el parseo / If parsing fails
            PDFParsingError: Si es un error específico de PDF / If it is a PDF-specific error
            WordParsingError: Si es un error específico de Word / If it is a Word-specific error
        """
        pass

    @abstractmethod
    def can_parse(self, filename: str) -> bool:
        """
        Verifica si este parser puede manejar el archivo.
        Verifies if this parser can handle the file.

        Args:
            filename: Nombre del archivo / File name

        Returns:
            True si puede parsear el archivo / True if it can parse the file
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Retorna las extensiones de archivo soportadas.
        Returns the supported file extensions.

        Returns:
            Lista de extensiones (ej: [".pdf", ".docx"]) / List of extensions (e.g.: [".pdf", ".docx"])
        """
        pass

    @abstractmethod
    def get_supported_mime_types(self) -> List[str]:
        """
        Retorna los tipos MIME soportados.
        Returns the supported MIME types.

        Returns:
            Lista de tipos MIME / List of MIME types
        """
        pass
