"""
Interfaz para exportadores de datos.
Permite exportar a diferentes formatos (Excel, CSV, JSON, etc.).

Interface for data exporters.
Allows exporting to different formats (Excel, CSV, JSON, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import io


class Exporter(ABC):
    """
    Interfaz abstracta para exportadores de datos.
    Specific implementations (ExcelExporter, CSVExporter, JSONExporter, etc.)
    deben heredar de esta clase.

    Abstract interface for data exporters.
    Specific implementations (ExcelExporter, CSVExporter, JSONExporter, etc.)
    must inherit from this class.
    """

    @abstractmethod
    def export(
        self,
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None
    ) -> io.BytesIO:
        """
        Exporta los datos al formato específico.
        Exports data to the specific format.

        Args:
            data: Lista de diccionarios con los datos a exportar / List of dictionaries with data to export
            columns: Lista de columnas (opcional, usa todas si no se especifica) / List of columns (optional, uses all if not specified)

        Returns:
            BytesIO con el contenido exportado / BytesIO with the exported content

        Raises:
            ValueError: Si los datos no son válidos / If the data is not valid
        """
        pass

    @abstractmethod
    def get_content_type(self) -> str:
        """
        Retorna el tipo MIME del contenido exportado.
        Returns the MIME type of the exported content.

        Returns:
            Tipo MIME (ej: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") / MIME type (e.g.: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Retorna la extensión del archivo exportado.
        Returns the extension of the exported file.

        Returns:
            Extensión del archivo (ej: ".xlsx") / File extension (e.g.: ".xlsx")
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """
        Retorna el nombre del formato.
        Returns the format name.

        Returns:
            Nombre del formato (ej: "Excel", "CSV", "JSON") / Format name (e.g.: "Excel", "CSV", "JSON")
        """
        pass
