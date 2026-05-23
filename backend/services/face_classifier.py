"""
Clasificador de caras de documentos colombianos.
Migrado al nuevo SDK google-genai.

Classifier for Colombian document faces.
Migrated to the new google-genai SDK.
"""

import os
import json
import logging
from typing import Dict, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from services.document_prompts import get_classification_prompt

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class FaceClassifier:
    """Clasifica el tipo de cara y documento de una imagen.
    Classifies the face type and document type of an image."""

    def __init__(self, model_name: str = None):
        """
        Inicializa el clasificador con el cliente de Gemini.

        Args:
            model_name: Nombre del modelo de Gemini a usar

        Initializes the classifier with the Gemini client.

        Args:
            model_name: Name of the Gemini model to use
        """
        self.model_name = model_name or GEMINI_MODEL
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no está configurada en .env")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def classify(self, image_bytes: bytes) -> Dict[str, any]:
        """
        Clasifica una imagen de documento colombiano.

        Args:
            image_bytes: La imagen del documento en formato bytes

        Returns:
            Diccionario con face_type, document_type, confidence, features

        Classifies an image of a Colombian document.

        Args:
            image_bytes: The document image in bytes format

        Returns:
            Dictionary with face_type, document_type, confidence, features
        """
        try:
            prompt = get_classification_prompt()

            # Enviamos la imagen y el prompt usando el nuevo SDK
            # Send the image and prompt using the new SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )

            response_text = response.text
            result = self._parse_response(response_text)
            result = self._validate_and_complete(result)

            return result

        except Exception as e:
            logger.error(f"Error al clasificar cara: {e}")
            return self._get_default_result()

    def _parse_response(self, response_text: str) -> Dict[str, any]:
        """Parsea la respuesta de la IA usando json.loads (seguro).
        Parses the AI response using json.loads (safe)."""
        try:
            response_text = response_text.strip()

            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]

            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # json.loads en vez de eval() — SEGURO
            # json.loads instead of eval() — SAFE
            result = json.loads(response_text)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear respuesta de clasificación: {e}")
            logger.error(f"Respuesta recibida: {response_text[:200]}")
            return self._get_default_result()

    def _validate_and_complete(self, result: Dict[str, any]) -> Dict[str, any]:
        """Valida y completa los campos del resultado.
        Validates and completes the result fields."""
        valid_face_types = ["FRONTAL", "TRASERA", "COMPLETO", "MIXTO", "DESCONOCIDO"]
        if result.get("face_type") not in valid_face_types:
            result["face_type"] = "DESCONOCIDO"

        valid_doc_types = [
            "cedula_ciudadania_vieja", "cedula_ciudadania_nueva",
            "cedula_digital", "tarjeta_identidad", "cedula_extranjeria",
            "pasaporte", "ppt", "otro"
        ]
        if result.get("document_type") not in valid_doc_types:
            result["document_type"] = "otro"

        if "confidence" not in result or not isinstance(result["confidence"], (int, float)):
            result["confidence"] = 0.5

        if "features" not in result or not isinstance(result["features"], dict):
            result["features"] = {
                "has_photo": False, "has_signature": False,
                "has_fingerprint": False, "has_number": False
            }

        return result

    def _get_default_result(self) -> Dict[str, any]:
        """Retorna un resultado por defecto cuando falla la clasificación.
        Returns a default result when classification fails."""
        return {
            "face_type": "DESCONOCIDO",
            "document_type": "otro",
            "confidence": 0.0,
            "features": {
                "has_photo": False, "has_signature": False,
                "has_fingerprint": False, "has_number": False
            }
        }

    def is_two_face_document(self, document_type: str) -> bool:
        """Determina si un tipo de documento tiene 2 caras.
        Determines whether a document type has 2 faces."""
        two_face_types = [
            "cedula_ciudadania_vieja", "cedula_ciudadania_nueva",
            "cedula_digital", "tarjeta_identidad", "cedula_extranjeria"
        ]
        return document_type in two_face_types


# Instancia global del clasificador para reutilizar
# Global classifier instance for reuse
_classifier_instance = None


def get_classifier() -> FaceClassifier:
    """Retorna la instancia global del clasificador (singleton pattern).
    Returns the global classifier instance (singleton pattern)."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = FaceClassifier()
    return _classifier_instance
