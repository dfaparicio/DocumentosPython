"""
Combinador de datos de múltiples caras del mismo documento.
Combina los datos extraídos de la cara frontal y trasera en un solo registro.

Data combiner for multiple faces of the same document.
Merges extracted data from the front and back faces into a single record.
"""

from typing import Dict, Optional, List


def merge_face_data(frontal_data: Optional[Dict[str, str]],
                    trasera_data: Optional[Dict[str, str]],
                    document_type: str) -> Dict[str, str]:
    """
    Combina los datos de la cara frontal y trasera de un documento.

    Args:
        frontal_data: Datos extraídos de la cara frontal
        trasera_data: Datos extraídos de la cara trasera
        document_type: Tipo de documento

    Returns:
        Diccionario con los datos combinados

    Merge data from the front and back faces of a document.

    Args:
        frontal_data: Extracted data from the front face
        trasera_data: Extracted data from the back face
        document_type: Document type

    Returns:
        Dictionary with the combined data
    """
    # Estructura de datos combinados
    # Combined data structure
    combined = {
        "tipo_documento": "",
        "numero_documento": "",
        "nombres": "",
        "apellidos": "",
        "fecha_nacimiento": "",
        "sexo": "",
        "nacionalidad": "",
        # Campos adicionales que pueden aparecer
        # Additional fields that may appear
        "fecha_expedicion": "",
        "fecha_vencimiento": "",
        "lugar_expedicion": "",
        "lugar_nacimiento": "",
        "huella_digital": "",
        "firma": "",
        "codigo_qr": "",
        "datos_biometricos": "",
        "grupo_sanguineo": "",
        "tipo_visa": ""
    }

    # Si no hay datos de ninguna cara, retornamos el diccionario vacío
    # If there is no data from any face, return the empty dictionary
    if not frontal_data and not trasera_data:
        return combined

    # Procesamos datos de la cara frontal (tienen prioridad para campos principales)
    # Process front face data (has priority for main fields)
    if frontal_data:
        for key, value in frontal_data.items():
            if value:  # Solo si no está vacío / Only if not empty
                combined[key] = value

    # Procesamos datos de la cara trasera (agregan información complementaria)
    # Process back face data (adds complementary information)
    if trasera_data:
        for key, value in trasera_data.items():
            # Solo agregamos si no existe en la frontal
            # Only add if it doesn't exist in the front face
            if value and not combined.get(key):
                combined[key] = value

    # Aseguramos que el tipo de documento esté presente
    # Ensure the document type is present
    if not combined.get("tipo_documento") and document_type:
        combined["tipo_documento"] = _format_document_type(document_type)

    # Validamos consistencia del número de documento
    # Validate consistency of the document number
    if frontal_data and trasera_data:
        front_num = frontal_data.get("numero_documento", "")
        back_num = trasera_data.get("numero_documento", "")

        if front_num and back_num:
            # Normalizar quitando puntos, espacios y guiones antes de comparar
            # Normalize by removing dots, spaces and hyphens before comparing
            front_normalized = front_num.replace(".", "").replace(" ", "").replace("-", "").strip()
            back_normalized = back_num.replace(".", "").replace(" ", "").replace("-", "").strip()

            if front_normalized != back_normalized:
                # Son realmente diferentes — probablemente son documentos distintos
                # They are actually different — probably different documents
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Números de documento no coinciden - "
                    f"Frontal: {front_num}, Trasera: {back_num}"
                )

            # Siempre tomamos el número de la frontal
            # Always take the number from the front face
            combined["numero_documento"] = front_num

    return combined


def merge_one_face_data(data: Optional[Dict[str, str]], document_type: str) -> Dict[str, str]:
    """
    Procesa datos de un documento de una sola cara (ej: pasaporte).

    Args:
        data: Datos extraídos del documento
        document_type: Tipo de documento

    Returns:
        Diccionario con los datos procesados

    Process data from a single-face document (e.g.: passport).

    Args:
        data: Extracted data from the document
        document_type: Document type

    Returns:
        Dictionary with the processed data
    """
    if not data:
        return merge_face_data(None, None, document_type)

    # Para documentos de 1 cara, simplemente retornamos los datos con el formato correcto
    # For single-face documents, simply return the data with the correct format
    combined = data.copy()

    # Aseguramos que el tipo de documento esté presente
    # Ensure the document type is present
    if not combined.get("tipo_documento") and document_type:
        combined["tipo_documento"] = _format_document_type(document_type)

    # Aseguramos que todos los campos esperados existan
    # Ensure all expected fields exist
    expected_fields = [
        "tipo_documento", "numero_documento", "nombres", "apellidos",
        "fecha_nacimiento", "sexo", "nacionalidad", "fecha_expedicion",
        "fecha_vencimiento", "lugar_expedicion", "lugar_nacimiento",
        "huella_digital", "firma", "codigo_qr", "datos_biometricos",
        "grupo_sanguineo", "tipo_visa"
    ]

    for field in expected_fields:
        if field not in combined:
            combined[field] = ""

    return combined


def merge_multiple_documents(frontal_list: List[Dict[str, str]],
                             trasera_list: List[Dict[str, str]],
                             document_type: str) -> List[Dict[str, str]]:
    """
    Combina múltiples pares de datos frontales y traseras.

    Args:
        frontal_list: Lista de datos de caras frontales
        trasera_list: Lista de datos de caras traseras
        document_type: Tipo de documento

    Returns:
        Lista de diccionarios con los datos combinados

    Combine multiple pairs of front and back face data.

    Args:
        frontal_list: List of front face data
        trasera_list: List of back face data
        document_type: Document type

    Returns:
        List of dictionaries with the combined data
    """
    # Si las listas tienen diferente longitud, usamos la menor
    # If the lists have different lengths, use the shorter one
    min_length = min(len(frontal_list), len(trasera_list))

    result = []

    for i in range(min_length):
        merged = merge_face_data(frontal_list[i], trasera_list[i], document_type)
        result.append(merged)

    # Si hay datos extra en una de las listas, los procesamos individualmente
    # If there is extra data in one of the lists, process it individually
    for i in range(min_length, len(frontal_list)):
        merged = merge_one_face_data(frontal_list[i], document_type)
        result.append(merged)

    for i in range(min_length, len(trasera_list)):
        merged = merge_one_face_data(trasera_list[i], document_type)
        result.append(merged)

    return result


def _format_document_type(document_type: str) -> str:
    """
    Convierte el tipo de documento interno a formato legible.

    Args:
        document_type: Tipo de documento interno (ej: "cedula_ciudadania_vieja")

    Returns:
        Tipo de documento formateado (ej: "Cédula de Ciudadanía")

    Convert internal document type to readable format.

    Args:
        document_type: Internal document type (e.g.: "cedula_ciudadania_vieja")

    Returns:
        Formatted document type (e.g.: "Cédula de Ciudadanía")
    """
    type_mapping = {
        "cedula_ciudadania_vieja": "Cédula de Ciudadanía",
        "cedula_ciudadania_nueva": "Cédula de Ciudadanía",
        "cedula_digital": "Cédula Digital",
        "tarjeta_identidad": "Tarjeta de Identidad",
        "cedula_extranjeria": "Cédula de Extranjería",
        "pasaporte": "Pasaporte",
        "ppt": "Permiso PPT",
        "contraseña": "Cédula de Ciudadanía",
        "otro": "Otro Documento"
    }

    return type_mapping.get(document_type, document_type.replace("_", " ").title())


def normalize_empty_values(data: Dict[str, str]) -> Dict[str, str]:
    """
    Normaliza los valores vacíos o nulos a strings vacíos.

    Args:
        data: Diccionario de datos

    Returns:
        Diccionario con valores normalizados

    Normalize empty or null values to empty strings.

    Args:
        data: Data dictionary

    Returns:
        Dictionary with normalized values
    """
    normalized = {}
    for key, value in data.items():
        if value is None or value == "None" or value == "null":
            normalized[key] = ""
        elif isinstance(value, str):
            normalized[key] = value.strip()
        else:
            normalized[key] = str(value).strip()
    return normalized


def clean_merged_data(data: Dict[str, str]) -> Dict[str, str]:
    """
    Limpia y normaliza los datos combinados finales.

    Args:
        data: Diccionario de datos combinados

    Returns:
        Diccionario con datos limpios y normalizados

    Clean and normalize final combined data.

    Args:
        data: Combined data dictionary

    Returns:
        Dictionary with clean and normalized data
    """
    # Primero normalizamos valores vacíos
    # First normalize empty values
    cleaned = normalize_empty_values(data)

    # Limpieza específica por campo
    # Field-specific cleanup
    if cleaned.get("numero_documento"):
        # Limpiamos el número de documento de espacios y guiones extras
        # Clean document number from extra spaces and hyphens
        cleaned["numero_documento"] = cleaned["numero_documento"].replace(" ", "").replace("-", "")

    if cleaned.get("fecha_nacimiento"):
        # Intentamos normalizar el formato de fecha
        # Try to normalize the date format
        cleaned["fecha_nacimiento"] = _normalize_date(cleaned["fecha_nacimiento"])

    if cleaned.get("fecha_expedicion"):
        cleaned["fecha_expedicion"] = _normalize_date(cleaned["fecha_expedicion"])

    if cleaned.get("fecha_vencimiento"):
        cleaned["fecha_vencimiento"] = _normalize_date(cleaned["fecha_vencimiento"])

    return cleaned


def _normalize_date(date_str: str) -> str:
    """
    Normaliza el formato de una fecha.

    Args:
        date_str: Fecha en cualquier formato

    Returns:
        Fecha en formato DD/MM/YYYY o string original si no se puede normalizar

    Normalize the format of a date.

    Args:
        date_str: Date in any format

    Returns:
        Date in DD/MM/YYYY format or original string if it cannot be normalized
    """
    if not date_str:
        return ""

    date_str = date_str.strip()

    # Si ya está en formato DD/MM/YYYY, retornamos
    # If already in DD/MM/YYYY format, return as-is
    if "/" in date_str and len(date_str.split("/")) == 3:
        return date_str

    # Si está en formato YYYY-MM-DD, convertimos a DD/MM/YYYY
    # If in YYYY-MM-DD format, convert to DD/MM/YYYY
    if "-" in date_str and len(date_str.split("-")) == 3:
        parts = date_str.split("-")
        if len(parts[0]) == 4:  # Formato YYYY-MM-DD / YYYY-MM-DD format
            return f"{parts[2]}/{parts[1]}/{parts[0]}"

    # Si está en formato DD-MM-YYYY, convertimos a DD/MM/YYYY
    # If in DD-MM-YYYY format, convert to DD/MM/YYYY
    if "-" in date_str and len(date_str.split("-")) == 3:
        parts = date_str.split("-")
        if len(parts[2]) == 4:  # Formato DD-MM-YYYY / DD-MM-YYYY format
            return f"{parts[0]}/{parts[1]}/{parts[2]}"

    # No podemos normalizar, retornamos el original
    # Cannot normalize, return the original
    return date_str


def get_excel_row_data(data: Dict[str, str]) -> List[str]:
    """
    Convierte los datos combinados al formato de fila para Excel.

    Args:
        data: Diccionario con los datos combinados

    Returns:
        Lista con los datos en el orden correcto para el Excel:
        [Tipo de Documento, Número de Documento, Nombres, Apellidos,
         Fecha de Nacimiento, Sexo, Nacionalidad]

    Convert combined data to Excel row format.

    Args:
        data: Dictionary with the combined data

    Returns:
        List with data in the correct order for Excel:
        [Document Type, Document Number, Names, Surnames,
         Date of Birth, Sex, Nationality]
    """
    return [
        data.get("tipo_documento", ""),
        data.get("numero_documento", ""),
        data.get("nombres", ""),
        data.get("apellidos", ""),
        data.get("fecha_nacimiento", ""),
        data.get("sexo", ""),
        data.get("nacionalidad", "")
    ]
