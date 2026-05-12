"""
Interfaz para exportadores de datos.
Permite exportar a diferentes formatos (Excel, CSV, JSON, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import io


class Exporter(ABC):
    """
    Interfaz abstracta para exportadores de datos.

    Implementaciones específicas (ExcelExporter, CSVExporter, JSONExporter, etc.)
    deben heredar de esta clase.
    """

    @abstractmethod
    def export(
        self,
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None
    ) -> io.BytesIO:
        """
        Exporta los datos al formato específico.

        Args:
            data: Lista de diccionarios con los datos a exportar
            columns: Lista de columnas (opcional, usa todas si no se especifica)

        Returns:
            BytesIO con el contenido exportado

        Raises:
            ValueError: Si los datos no son válidos
        """
        pass

    @abstractmethod
    def get_content_type(self) -> str:
        """
        Retorna el tipo MIME del contenido exportado.

        Returns:
            Tipo MIME (ej: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Retorna la extensión del archivo exportado.

        Returns:
            Extensión del archivo (ej: ".xlsx")
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """
        Retorna el nombre del formato.

        Returns:
            Nombre del formato (ej: "Excel", "CSV", "JSON")
        """
        pass
