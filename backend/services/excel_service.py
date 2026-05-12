"""
Servicio para crear archivos Excel con los datos extraídos de documentos colombianos.
Usamos pandas para organizar los datos y openpyxl para generar el Excel.
"""

import pandas as pd
import io
from typing import List, Dict

# Orden de columnas según especificación
EXCEL_COLUMNS = [
    "Tipo de Documento",
    "Número de Documento",
    "Nombres",
    "Apellidos",
    "Fecha de Nacimiento",
    "Sexo",
    "Nacionalidad"
]


def create_excel_with_data(data_list: List[Dict[str, str]]) -> io.BytesIO:
    """
    Crea un archivo Excel con los datos extraídos de documentos colombianos.

    Args:
        data_list: Lista de diccionarios, cada uno con los datos de un documento

    Returns:
        El archivo Excel en memoria (para enviarlo como respuesta de la API)
    """

    try:
        # Convertimos la lista de diccionarios a una lista de listas con el orden correcto
        formatted_data = []
        for item in data_list:
            formatted_data.append([
                item.get("tipo_documento", ""),
                item.get("numero_documento", ""),
                item.get("nombres", ""),
                item.get("apellidos", ""),
                item.get("fecha_nacimiento", ""),
                item.get("sexo", ""),
                item.get("nacionalidad", "")
            ])

        # Creamos un DataFrame de pandas
        # El DataFrame es como una tabla organizada de datos
        df = pd.DataFrame(formatted_data, columns=EXCEL_COLUMNS)

        # Creamos un buffer en memoria para guardar el Excel
        # No guardamos archivo en disco, todo está en memoria
        excel_buffer = io.BytesIO()

        # Escribimos el DataFrame en el buffer como archivo Excel
        # Usamos openpyxl como motor porque es el estándar para .xlsx
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Documentos")

        # Volvemos al inicio del buffer
        # Esto es necesario porque después de escribir, el puntero queda al final
        excel_buffer.seek(0)

        return excel_buffer

    except Exception as e:
        # Si algo falla al crear el Excel, devolvemos un Excel vacío con encabezados
        print(f"Error al crear el Excel: {e}")

        # Creamos un Excel vacío con solo los encabezados
        df = pd.DataFrame(columns=EXCEL_COLUMNS)
        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Documentos")

        excel_buffer.seek(0)
        return excel_buffer


def create_excel_with_merged_documents(documents: List[Dict[str, str]]) -> io.BytesIO:
    """
    Crea un archivo Excel con los datos de documentos combinados.

    Args:
        documents: Lista de diccionarios con los datos combinados de documentos

    Returns:
        El archivo Excel en memoria
    """
    return create_excel_with_data(documents)


def get_excel_columns() -> List[str]:
    """
    Retorna la lista de columnas del Excel.

    Returns:
        Lista de nombres de columnas en orden
    """
    return EXCEL_COLUMNS.copy()


def validate_data_for_excel(data: Dict[str, str]) -> bool:
    """
    Valida que los datos tengan el formato correcto para el Excel.

    Args:
        data: Diccionario con los datos del documento

    Returns:
        True si los datos son válidos, False en caso contrario
    """
    # Validamos que al menos tenga número de documento
    if not data.get("numero_documento"):
        return False

    # Validamos que el tipo de documento esté presente
    if not data.get("tipo_documento"):
        return False

    return True

