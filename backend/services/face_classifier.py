"""
Clasificador de caras de documentos colombianos.
Analiza una imagen y determina el tipo de cara y el tipo de documento.
"""

import os
import google.generativeai as genai
from typing import Dict, Optional
from dotenv import load_dotenv
from services.document_prompts import get_classification_prompt

# Cargamos las variables de entorno
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class FaceClassifier:
    """
    Clasifica el tipo de cara y documento de una imagen.
    """

    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        """
        Inicializa el clasificador con el modelo de IA.

        Args:
            model_name: Nombre del modelo de Gemini a usar
        """
        self.model = genai.GenerativeModel(model_name)

    def classify(self, image_bytes: bytes) -> Dict[str, any]:
        """
        Clasifica una imagen de documento colombiano.

        Args:
            image_bytes: La imagen del documento en formato bytes

        Returns:
            Diccionario con:
            - face_type: "FRONTAL", "TRASERA", "COMPLETO", o "MIXTO"
            - document_type: Tipo de documento específico
            - confidence: Nivel de confianza (0.0 a 1.0)
            - features: Diccionario con características detectadas
        """
        try:
            prompt = get_classification_prompt()

            # Enviamos la imagen y el prompt a la IA
            response = self.model.generate_content(
                [
                    prompt,
                    {"mime_type": "image/png", "data": image_bytes}
                ]
            )

            # Obtenemos el texto de la respuesta
            response_text = response.text

            # Intentamos convertir el texto a un diccionario
            result = self._parse_response(response_text)

            # Validamos y completamos los campos necesarios
            result = self._validate_and_complete(result)

            return result

        except Exception as e:
            # Si falla la clasificación, devolvemos valores por defecto
            print(f"Error al clasificar cara: {e}")
            return self._get_default_result()

    def _parse_response(self, response_text: str) -> Dict[str, any]:
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
            print(f"Error al parsear respuesta de clasificación: {e}")
            print(f"Respuesta recibida: {response_text}")
            return self._get_default_result()

    def _validate_and_complete(self, result: Dict[str, any]) -> Dict[str, any]:
        """
        Valida y completa los campos del resultado.

        Args:
            result: Diccionario a validar

        Returns:
            Diccionario validado y completado
        """
        # Validar face_type
        valid_face_types = ["FRONTAL", "TRASERA", "COMPLETO", "MIXTO", "DESCONOCIDO"]
        if result.get("face_type") not in valid_face_types:
            result["face_type"] = "DESCONOCIDO"

        # Validar document_type
        valid_doc_types = [
            "cedula_ciudadania_vieja",
            "cedula_ciudadania_nueva",
            "cedula_digital",
            "tarjeta_identidad",
            "cedula_extranjeria",
            "pasaporte",
            "ppt",
            "otro"
        ]
        if result.get("document_type") not in valid_doc_types:
            result["document_type"] = "otro"

        # Validar confidence
        if "confidence" not in result or not isinstance(result["confidence"], (int, float)):
            result["confidence"] = 0.5

        # Validar features
        if "features" not in result or not isinstance(result["features"], dict):
            result["features"] = {
                "has_photo": False,
                "has_signature": False,
                "has_fingerprint": False,
                "has_number": False
            }

        return result

    def _get_default_result(self) -> Dict[str, any]:
        """
        Retorna un resultado por defecto cuando falla la clasificación.

        Returns:
            Diccionario con valores por defecto
        """
        return {
            "face_type": "DESCONOCIDO",
            "document_type": "otro",
            "confidence": 0.0,
            "features": {
                "has_photo": False,
                "has_signature": False,
                "has_fingerprint": False,
                "has_number": False
            }
        }

    def is_frontal(self, image_bytes: bytes) -> bool:
        """
        Determina si una imagen es una cara frontal.

        Args:
            image_bytes: La imagen en formato bytes

        Returns:
            True si es frontal, False en caso contrario
        """
        result = self.classify(image_bytes)
        return result["face_type"] == "FRONTAL"

    def is_trasera(self, image_bytes: bytes) -> bool:
        """
        Determina si una imagen es una cara trasera.

        Args:
            image_bytes: La imagen en formato bytes

        Returns:
            True si es trasera, False en caso contrario
        """
        result = self.classify(image_bytes)
        return result["face_type"] == "TRASERA"

    def is_completo(self, image_bytes: bytes) -> bool:
        """
        Determina si una imagen es un documento completo (1 cara).

        Args:
            image_bytes: La imagen en formato bytes

        Returns:
            True si es completo, False en caso contrario
        """
        result = self.classify(image_bytes)
        return result["face_type"] == "COMPLETO"

    def is_mixto(self, image_bytes: bytes) -> bool:
        """
        Determina si una imagen contiene dos caras (mixta).

        Args:
            image_bytes: La imagen en formato bytes

        Returns:
            True si es mixta, False en caso contrario
        """
        result = self.classify(image_bytes)
        return result["face_type"] == "MIXTO"

    def get_document_type(self, image_bytes: bytes) -> str:
        """
        Retorna el tipo de documento de una imagen.

        Args:
            image_bytes: La imagen en formato bytes

        Returns:
            Tipo de documento (ej: "cedula_ciudadania_vieja", "pasaporte", etc.)
        """
        result = self.classify(image_bytes)
        return result["document_type"]

    def is_two_face_document(self, document_type: str) -> bool:
        """
        Determina si un tipo de documento tiene 2 caras.

        Args:
            document_type: Tipo de documento

        Returns:
            True si tiene 2 caras, False si tiene 1 sola cara
        """
        two_face_types = [
            "cedula_ciudadania_vieja",
            "cedula_ciudadania_nueva",
            "cedula_digital",
            "tarjeta_identidad",
            "cedula_extranjeria"
        ]
        return document_type in two_face_types


# Instancia global del clasificador para reutilizar
_classifier_instance = None


def get_classifier() -> FaceClassifier:
    """
    Retorna la instancia global del clasificador (singleton pattern).

    Returns:
        Instancia de FaceClassifier
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = FaceClassifier()
    return _classifier_instance
