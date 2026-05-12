"""
Combinador de datos de múltiples caras del mismo documento.
Combina los datos extraídos de la cara frontal y trasera en un solo registro.
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
    """
    # Estructura de datos combinados
    combined = {
        "tipo_documento": "",
        "numero_documento": "",
        "nombres": "",
        "apellidos": "",
        "fecha_nacimiento": "",
        "sexo": "",
        "nacionalidad": "",
        # Campos adicionales que pueden aparecer
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
    if not frontal_data and not trasera_data:
        return combined

    # Procesamos datos de la cara frontal (tienen prioridad para campos principales)
    if frontal_data:
        for key, value in frontal_data.items():
            if value:  # Solo si no está vacío
                combined[key] = value

    # Procesamos datos de la cara trasera (agregan información complementaria)
    if trasera_data:
        for key, value in trasera_data.items():
            # Solo agregamos si no existe en la frontal
            if value and not combined.get(key):
                combined[key] = value

    # Aseguramos que el tipo de documento esté presente
    if not combined.get("tipo_documento") and document_type:
        combined["tipo_documento"] = _format_document_type(document_type)

    # Validamos consistencia del número de documento
    if frontal_data and trasera_data:
        front_num = frontal_data.get("numero_documento", "")
        back_num = trasera_data.get("numero_documento", "")

        if front_num and back_num and front_num != back_num:
            # Los números no coinciden, tomamos el de la frontal con advertencia
            print(f"Advertencia: Números de documento no coinciden - Frontal: {front_num}, Trasera: {back_num}")
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
    """
    if not data:
        return merge_face_data(None, None, document_type)

    # Para documentos de 1 cara, simplemente retornamos los datos con el formato correcto
    combined = data.copy()

    # Aseguramos que el tipo de documento esté presente
    if not combined.get("tipo_documento") and document_type:
        combined["tipo_documento"] = _format_document_type(document_type)

    # Aseguramos que todos los campos esperados existan
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
    """
    # Si las listas tienen diferente longitud, usamos la menor
    min_length = min(len(frontal_list), len(trasera_list))

    result = []

    for i in range(min_length):
        merged = merge_face_data(frontal_list[i], trasera_list[i], document_type)
        result.append(merged)

    # Si hay datos extra en una de las listas, los procesamos individualmente
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
        Tipo de documento formateado (ej: "Cédula de Ciudadanía Vieja")
    """
    type_mapping = {
        "cedula_ciudadania_vieja": "Cédula de Ciudadanía Vieja",
        "cedula_ciudadania_nueva": "Cédula de Ciudadanía Nueva",
        "cedula_digital": "Cédula Digital",
        "tarjeta_identidad": "Tarjeta de Identidad",
        "cedula_extranjeria": "Cédula de Extranjería",
        "pasaporte": "Pasaporte",
        "ppt": "Permiso PPT",
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
    """
    # Primero normalizamos valores vacíos
    cleaned = normalize_empty_values(data)

    # Limpieza específica por campo
    if cleaned.get("numero_documento"):
        # Limpiamos el número de documento de espacios y guiones extras
        cleaned["numero_documento"] = cleaned["numero_documento"].replace(" ", "").replace("-", "")

    if cleaned.get("fecha_nacimiento"):
        # Intentamos normalizar el formato de fecha
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
    """
    if not date_str:
        return ""

    date_str = date_str.strip()

    # Si ya está en formato DD/MM/YYYY, retornamos
    if "/" in date_str and len(date_str.split("/")) == 3:
        return date_str

    # Si está en formato YYYY-MM-DD, convertimos a DD/MM/YYYY
    if "-" in date_str and len(date_str.split("-")) == 3:
        parts = date_str.split("-")
        if len(parts[0]) == 4:  # Formato YYYY-MM-DD
            return f"{parts[2]}/{parts[1]}/{parts[0]}"

    # Si está en formato DD-MM-YYYY, convertimos a DD/MM/YYYY
    if "-" in date_str and len(date_str.split("-")) == 3:
        parts = date_str.split("-")
        if len(parts[2]) == 4:  # Formato DD-MM-YYYY
            return f"{parts[0]}/{parts[1]}/{parts[2]}"

    # No podemos normalizar, retornamos el original
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
