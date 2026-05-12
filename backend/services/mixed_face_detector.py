"""
Detector de caras mixtas en páginas de PDF.
Detecta si una página contiene dos caras del mismo documento.
"""

import os
import google.generativeai as genai
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from services.document_prompts import get_mixed_detection_prompt, get_split_coordinates_prompt
from services.image_splitter import split_image_by_coordinates

# Cargamos las variables de entorno
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class MixedFaceDetector:
    """
    Detecta y maneja páginas que contienen dos caras de un documento.
    """

    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        """
        Inicializa el detector con el modelo de IA.

        Args:
            model_name: Nombre del modelo de Gemini a usar
        """
        self.model = genai.GenerativeModel(model_name)

    def is_mixed(self, image_bytes: bytes) -> bool:
        """
        Determina si una imagen contiene dos caras de un documento.

        Args:
            image_bytes: La imagen en formato bytes

        Returns:
            True si contiene dos caras, False en caso contrario
        """
        try:
            prompt = get_mixed_detection_prompt()

            # Enviamos la imagen y el prompt a la IA
            response = self.model.generate_content(
                [
                    prompt,
                    {"mime_type": "image/png", "data": image_bytes}
                ]
            )

            # Obtenemos el texto de la respuesta
            response_text = response.text.strip().upper()

            # La respuesta debe ser "SI" o "NO"
            return response_text == "SI"

        except Exception as e:
            print(f"Error al detectar caras mixtas: {e}")
            # Por seguridad, si fallamos, asumimos que no es mixto
            return False

    def get_split_coordinates(self, image_bytes: bytes) -> Optional[Dict[str, Dict[str, any]]]:
        """
        Obtiene las coordenadas para dividir una página mixta en dos caras.

        Args:
            image_bytes: La imagen en formato bytes

        Returns:
            Diccionario con coordenadas de cara_1 y cara_2, o None si falla
        """
        try:
            prompt = get_split_coordinates_prompt()

            # Enviamos la imagen y el prompt a la IA
            response = self.model.generate_content(
                [
                    prompt,
                    {"mime_type": "image/png", "data": image_bytes}
                ]
            )

            # Obtenemos el texto de la respuesta
            response_text = response.text

            # Parseamos la respuesta
            coordinates = self._parse_coordinates(response_text)

            return coordinates

        except Exception as e:
            print(f"Error al obtener coordenadas de división: {e}")
            return None

    def _parse_coordinates(self, response_text: str) -> Optional[Dict[str, Dict[str, any]]]:
        """
        Parsea la respuesta de coordenadas a un diccionario.

        Args:
            response_text: Texto de respuesta de la IA

        Returns:
            Diccionario con coordenadas o None si falla
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

            # Validamos que tenga la estructura esperada
            if "cara_1" not in result or "cara_2" not in result:
                print("Respuesta de coordenadas no tiene la estructura esperada")
                return None

            # Validamos las coordenadas
            for cara in ["cara_1", "cara_2"]:
                coords = result[cara]
                required_keys = ["y_inicio", "y_fin", "x_inicio", "x_fin"]
                for key in required_keys:
                    if key not in coords or not isinstance(coords[key], (int, float)):
                        print(f"Coordenada inválida en {cara}: {key}")
                        return None

            return result

        except Exception as e:
            print(f"Error al parsear coordenadas: {e}")
            print(f"Respuesta recibida: {response_text}")
            return None

    def split_mixed_page(self, image_bytes: bytes) -> Optional[Tuple[bytes, bytes]]:
        """
        Divide una página mixta en dos imágenes separadas.

        Args:
            image_bytes: La imagen en formato bytes

        Returns:
            Tupla (cara_1, cara_2) con las dos imágenes, o None si falla
        """
        # Obtenemos las coordenadas de división
        coordinates = self.get_split_coordinates(image_bytes)

        if coordinates is None:
            return None

        # Dividimos la imagen usando las coordenadas
        return split_image_by_coordinates(image_bytes, coordinates)

    def detect_and_split(self, image_bytes: bytes) -> Optional[Tuple[bytes, bytes]]:
        """
        Detecta si una página es mixta y, si lo es, la divide.

        Args:
            image_bytes: La imagen en formato bytes

        Returns:
            Tupla (cara_1, cara_2) si es mixta, None si no lo es o falla
        """
        if not self.is_mixed(image_bytes):
            return None

        return self.split_mixed_page(image_bytes)


# Instancia global del detector para reutilizar
_detector_instance = None


def get_detector() -> MixedFaceDetector:
    """
    Retorna la instancia global del detector (singleton pattern).

    Returns:
        Instancia de MixedFaceDetector
    """
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = MixedFaceDetector()
    return _detector_instance
