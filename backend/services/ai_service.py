"""
Servicio para conectar con Google Gemini y extraer datos de documentos colombianos.
La IA analiza las imágenes y nos devuelve la información que necesitamos.
"""

import os
import google.generativeai as genai
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from services.document_prompts import get_prompt, get_all_document_types
from services.face_classifier import get_classifier

# Cargamos las variables de entorno desde el archivo .env
# Esto lee la API key sin exponerla en el código
load_dotenv()

# Configuramos la conexión con Gemini
# Obtenemos la API key desde las variables de entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# Instancia global del modelo para reutilizar
_model_instance = None
_classifier_instance = None


def get_model():
    """Retorna la instancia del modelo (singleton pattern)."""
    global _model_instance
    if _model_instance is None:
        _model_instance = genai.GenerativeModel("gemini-3-flash-preview")
    return _model_instance


def get_classifier():
    """Retorna la instancia del clasificador (singleton pattern)."""
    global _classifier_instance
    if _classifier_instance is None:
        from services.face_classifier import FaceClassifier
        _classifier_instance = FaceClassifier()
    return _classifier_instance


def extract_data_from_image(image_bytes: bytes,
                           document_type: Optional[str] = None,
                           face_type: str = "completo") -> Dict[str, str]:
    """
    Envía una imagen a Gemini y extrae los datos del documento.

    Args:
        image_bytes: La imagen del documento en formato bytes
        document_type: Tipo de documento (ej: "cedula_ciudadania_vieja", "pasaporte")
        face_type: Tipo de cara ("frontal", "trasera", "completo")

    Returns:
        Diccionario con los datos extraídos (7 campos mínimos)
    """
    try:
        # Si no se especificó el tipo de documento, lo inferimos
        if document_type is None:
            classifier = get_classifier()
            classification = classifier.classify(image_bytes)
            document_type = classification.get("document_type", "otro")

            # Inferimos el tipo de cara si no se especificó
            if face_type == "completo":
                inferred_face = classification.get("face_type", "DESCONOCIDO")
                if inferred_face in ["FRONTAL", "TRASERA"]:
                    face_type = inferred_face.lower()

        # Obtenemos el prompt específico para este tipo de documento y cara
        prompt = get_prompt(document_type, face_type)

        # Creamos el modelo de IA
        model = get_model()

        # Enviamos la imagen y el prompt a la IA
        response = model.generate_content(
            [
                prompt,
                {"mime_type": "image/png", "data": image_bytes}
            ]
        )

        # Obtenemos el texto de la respuesta
        response_text = response.text

        # Parseamos la respuesta
        result = _parse_response(response_text)

        # Aseguramos que el tipo de documento esté presente
        if not result.get("tipo_documento"):
            result["tipo_documento"] = _format_document_type(document_type)

        # Aseguramos que todos los campos esperados existan
        result = _ensure_required_fields(result)

        return result

    except Exception as e:
        # Si falla la conexión con la IA, devolvemos campos vacíos
        print(f"Error al conectar con Gemini: {e}")
        return _get_empty_result(document_type)


def extract_data_from_two_faces(frontal_image: bytes,
                                trasera_image: bytes,
                                document_type: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Extrae datos de las dos caras de un documento.

    Args:
        frontal_image: Imagen de la cara frontal
        trasera_image: Imagen de la cara trasera
        document_type: Tipo de documento

    Returns:
        Tupla (datos_frontal, datos_trasera)
    """
    frontal_data = extract_data_from_image(frontal_image, document_type, "frontal")
    trasera_data = extract_data_from_image(trasera_image, document_type, "trasera")

    return frontal_data, trasera_data


def _parse_response(response_text: str) -> Dict[str, str]:
    """
    Parsea la respuesta de la IA a un diccionario.

    Args:
        response_text: Texto de respuesta de la IA

    Returns:
        Diccionario parseado
    """
    try:
        # Limpiamos el texto
        response_text = response_text.strip()

        # Si la respuesta tiene markdown code blocks, los quitamos
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "")
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "")

        # Convertimos el string JSON a diccionario
        result = eval(response_text)

        return result

    except Exception as e:
        print(f"Error al parsear la respuesta de la IA: {e}")
        print(f"Respuesta recibida: {response_text}")
        return {}


def _ensure_required_fields(result: Dict[str, str]) -> Dict[str, str]:
    """
    Asegura que todos los campos esperados estén presentes en el resultado.

    Args:
        result: Diccionario con los datos parseados

    Returns:
        Diccionario con todos los campos esperados
    """
    # Campos obligatorios para todos los documentos
    required_fields = [
        "tipo_documento",
        "numero_documento",
        "nombres",
        "apellidos",
        "fecha_nacimiento",
        "sexo",
        "nacionalidad"
    ]

    # Campos opcionales
    optional_fields = [
        "fecha_expedicion",
        "fecha_vencimiento",
        "lugar_expedicion",
        "lugar_nacimiento",
        "huella_digital",
        "firma",
        "codigo_qr",
        "datos_biometricos",
        "grupo_sanguineo",
        "tipo_visa"
    ]

    # Aseguramos campos obligatorios
    for field in required_fields:
        if field not in result:
            result[field] = ""

    # Aseguramos campos opcionales
    for field in optional_fields:
        if field not in result:
            result[field] = ""

    return result


def _format_document_type(document_type: str) -> str:
    """
    Convierte el tipo de documento interno a formato legible.

    Args:
        document_type: Tipo de documento interno

    Returns:
        Tipo de documento formateado
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


def _get_empty_result(document_type: Optional[str]) -> Dict[str, str]:
    """
    Retorna un resultado vacío cuando falla la extracción.

    Args:
        document_type: Tipo de documento

    Returns:
        Diccionario con campos vacíos
    """
    return {
        "tipo_documento": _format_document_type(document_type) if document_type else "",
        "numero_documento": "",
        "nombres": "",
        "apellidos": "",
        "fecha_nacimiento": "",
        "sexo": "",
        "nacionalidad": "",
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
