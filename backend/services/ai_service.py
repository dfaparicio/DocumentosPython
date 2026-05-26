"""
Servicio para conectar con Google Gemini y extraer datos de documentos colombianos.
Migrado al nuevo SDK google-genai (reemplaza google-generativeai deprecado).

Service to connect with Google Gemini and extract data from Colombian documents.
Migrated to the new google-genai SDK (replaces deprecated google-generativeai).
"""

import os
import json
import logging
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv
from google import genai
from google.genai import types

from services.document_prompts import get_prompt, get_all_document_types
from services.api_key_store import get_api_key

# Cargamos las variables de entorno desde el archivo .env
# We load the environment variables from the .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Configuramos la conexión con Gemini usando el nuevo SDK
# We configure the Gemini connection using the new SDK
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def get_client():
    """
    Retorna una instancia del cliente Gemini.
    Lee la API key desde el store (archivo JSON o .env).

    Returns a Gemini client instance.
    Reads the API key from the store (JSON file or .env).
    """
    api_key = get_api_key()
    if not api_key:
        raise ValueError("API key de Gemini no configurada. Configúrala desde la aplicación.")
    return genai.Client(api_key=api_key)


def extract_data_from_image(image_bytes: bytes,
                           document_type: Optional[str] = None,
                           face_type: str = "completo") -> Dict[str, str]:
    """
    Envía una imagen a Gemini y extrae los datos del documento.

    Sends an image to Gemini and extracts the document data.

    Args:
        image_bytes: La imagen del documento en formato bytes
            The document image in bytes format
        document_type: Tipo de documento (ej: "cedula_ciudadania_vieja", "pasaporte")
            Document type (e.g.: "cedula_ciudadania_vieja", "pasaporte")
        face_type: Tipo de cara ("frontal", "trasera", "completo")
            Face type ("frontal" (front), "trasera" (back), "completo" (full))

    Returns:
        Diccionario con los datos extraídos (7 campos mínimos)
        Dictionary with the extracted data (7 minimum fields)
    """
    try:
        client = get_client()

        # Si no se especificó el tipo de documento, lo inferimos
        # If the document type was not specified, we infer it
        if document_type is None:
            from services.face_classifier import get_classifier
            classifier = get_classifier()
            classification = classifier.classify(image_bytes)
            document_type = classification.get("document_type", "otro")

            # Inferimos el tipo de cara si no se especificó
            # We infer the face type if it was not specified
            if face_type == "completo":
                inferred_face = classification.get("face_type", "DESCONOCIDO")
                if inferred_face in ["FRONTAL", "TRASERA"]:
                    face_type = inferred_face.lower()

        # Obtenemos el prompt específico para este tipo de documento y cara
        # We get the specific prompt for this document type and face
        prompt = get_prompt(document_type, face_type)

        # Enviamos la imagen y el prompt a la IA usando el nuevo SDK
        # We send the image and prompt to the AI using the new SDK
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                prompt
            ]
        )

        # Obtenemos el texto de la respuesta
        # We get the response text
        response_text = response.text

        # Parseamos la respuesta
        # We parse the response
        result = _parse_response(response_text)

        # Aseguramos que el tipo de documento esté presente
        # We ensure the document type is present
        if not result.get("tipo_documento"):
            result["tipo_documento"] = _format_document_type(document_type)

        # Aseguramos que todos los campos esperados existan
        # We ensure all expected fields exist
        result = _ensure_required_fields(result)

        return result

    except Exception as e:
        # Si falla la conexión con la IA, devolvemos campos vacíos
        # If the AI connection fails, we return empty fields
        logger.error(f"Error al conectar con Gemini: {e}")
        return _get_empty_result(document_type)


def extract_data_from_two_faces(frontal_image: bytes,
                                trasera_image: bytes,
                                document_type: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Extrae datos de las dos caras de un documento.

    Extracts data from both faces of a document.

    Args:
        frontal_image: Imagen de la cara frontal
            Front face image
        trasera_image: Imagen de la cara trasera
            Back face image
        document_type: Tipo de documento
            Document type

    Returns:
        Tupla (datos_frontal, datos_trasera)
        Tuple (front_data, back_data)
    """
    frontal_data = extract_data_from_image(frontal_image, document_type, "frontal")
    trasera_data = extract_data_from_image(trasera_image, document_type, "trasera")

    return frontal_data, trasera_data


def _parse_response(response_text: str) -> Dict[str, str]:
    """
    Parsea la respuesta de la IA a un diccionario de forma SEGURA.
    Usa json.loads() en vez de eval() para evitar ejecución de código arbitrario.

    Parses the AI response into a dictionary in a SAFE manner.
    Uses json.loads() instead of eval() to prevent arbitrary code execution.
    """
    try:
        # Limpiamos el texto
        # We clean the text
        response_text = response_text.strip()

        # Si la respuesta tiene markdown code blocks, los quitamos
        # If the response has markdown code blocks, we remove them
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Quitar ```json / Remove ```json
        elif response_text.startswith("```"):
            response_text = response_text[3:]  # Quitar ``` / Remove ```

        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Quitar ``` del final / Remove trailing ```

        response_text = response_text.strip()

        # Usamos json.loads en vez de eval() — SEGURO
        # We use json.loads instead of eval() — SAFE
        result = json.loads(response_text)

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON de la IA: {e}")
        logger.error(f"Respuesta recibida: {response_text[:200]}")
        return {}


def _ensure_required_fields(result: Dict[str, str]) -> Dict[str, str]:
    """
    Asegura que todos los campos esperados estén presentes en el resultado.

    Ensures all expected fields are present in the result.
    """
    # Campos obligatorios para todos los documentos
    # Required fields for all documents
    required_fields = [
        "tipo_documento", "numero_documento", "nombres",
        "apellidos", "fecha_nacimiento", "sexo", "nacionalidad"
    ]

    # Campos opcionales
    # Optional fields
    optional_fields = [
        "fecha_expedicion", "fecha_vencimiento", "lugar_expedicion",
        "lugar_nacimiento", "huella_digital", "firma", "codigo_qr",
        "datos_biometricos", "grupo_sanguineo", "tipo_visa"
    ]

    for field in required_fields + optional_fields:
        if field not in result:
            result[field] = ""

    return result


def _format_document_type(document_type: str) -> str:
    """
    Convierte el tipo de documento interno a formato legible.

    Converts the internal document type to a human-readable format.
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


def _get_empty_result(document_type: Optional[str]) -> Dict[str, str]:
    """
    Retorna un resultado vacío cuando falla la extracción.

    Returns an empty result when extraction fails.
    """
    return {
        "tipo_documento": _format_document_type(document_type) if document_type else "",
        "numero_documento": "", "nombres": "", "apellidos": "",
        "fecha_nacimiento": "", "sexo": "", "nacionalidad": "",
        "fecha_expedicion": "", "fecha_vencimiento": "",
        "lugar_expedicion": "", "lugar_nacimiento": "",
        "huella_digital": "", "firma": "", "codigo_qr": "",
        "datos_biometricos": "", "grupo_sanguineo": "", "tipo_visa": ""
    }
