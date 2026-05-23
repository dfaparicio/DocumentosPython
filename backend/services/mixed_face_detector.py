"""
Detector de caras mixtas en páginas de PDF.
Migrado al nuevo SDK google-genai + detección heurística para reducir llamadas API.

Detector for mixed faces in PDF pages.
Migrated to the new google-genai SDK + heuristic detection to reduce API calls.
"""

import os
import io
import json
import logging
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types
from services.document_prompts import get_mixed_detection_prompt, get_split_coordinates_prompt
from services.image_splitter import split_image_by_coordinates

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def is_likely_mixed_heuristic(image_bytes: bytes) -> bool:
    """
    Detección heurística RÁPIDA de páginas mixtas sin usar IA.
    Analiza el ratio de la imagen para determinar si probablemente
    contiene dos documentos apilados.

    Args:
        image_bytes: La imagen en formato bytes

    Returns:
        True si probablemente contiene dos caras

    FAST heuristic detection of mixed pages without using AI.
    Analyzes the image ratio to determine if it likely
    contains two stacked documents.

    Args:
        image_bytes: The image in bytes format

    Returns:
        True if it likely contains two faces
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size

        # Si la imagen es mucho más alta que ancha (ratio > 1.8),
        # probablemente tiene dos documentos apilados verticalmente
        # If the image is much taller than wide (ratio > 1.8),
        # it probably has two vertically stacked documents
        ratio = height / width if width > 0 else 0
        is_tall = ratio > 1.8

        if is_tall:
            logger.debug(f"Heurística: imagen alta ({width}x{height}, ratio={ratio:.2f}), probable mixta")

        return is_tall

    except Exception as e:
        logger.warning(f"Error en heurística de detección mixta: {e}")
        return False


class MixedFaceDetector:
    """Detecta y maneja páginas que contienen dos caras de un documento.
    Detects and handles pages that contain two faces of a document."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or GEMINI_MODEL
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no está configurada en .env")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def is_mixed(self, image_bytes: bytes) -> bool:
        """
        Determina si una imagen contiene dos caras de un documento.
        Primero usa heurística rápida, luego confirma con IA solo si es necesario.

        Determines if an image contains two faces of a document.
        First uses fast heuristics, then confirms with AI only if necessary.
        """
        # Paso 1: Heurística rápida (sin IA)
        # Step 1: Fast heuristics (no AI)
        if not is_likely_mixed_heuristic(image_bytes):
            return False

        # Paso 2: Si la heurística dice que puede ser mixta, confirmamos con IA
        # Step 2: If heuristics say it might be mixed, confirm with AI
        try:
            prompt = get_mixed_detection_prompt()

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )

            response_text = response.text.strip().upper()
            return response_text == "SI"

        except Exception as e:
            logger.error(f"Error al detectar caras mixtas: {e}")
            return False

    def get_split_coordinates(self, image_bytes: bytes) -> Optional[Dict[str, Dict[str, any]]]:
        """Obtiene las coordenadas para dividir una página mixta en dos caras.
        Gets the coordinates to split a mixed page into two faces."""
        try:
            prompt = get_split_coordinates_prompt()

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )

            response_text = response.text
            coordinates = self._parse_coordinates(response_text)
            return coordinates

        except Exception as e:
            logger.error(f"Error al obtener coordenadas de división: {e}")
            return None

    def _parse_coordinates(self, response_text: str) -> Optional[Dict[str, Dict[str, any]]]:
        """Parsea la respuesta de coordenadas usando json.loads (seguro).
        Parses the coordinates response using json.loads (safe)."""
        try:
            response_text = response_text.strip()

            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]

            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # json.loads en vez de eval()
            # json.loads instead of eval()
            result = json.loads(response_text)

            if "cara_1" not in result or "cara_2" not in result:
                logger.warning("Respuesta de coordenadas no tiene la estructura esperada")
                return None

            for cara in ["cara_1", "cara_2"]:
                coords = result[cara]
                required_keys = ["y_inicio", "y_fin", "x_inicio", "x_fin"]
                for key in required_keys:
                    if key not in coords or not isinstance(coords[key], (int, float)):
                        logger.warning(f"Coordenada inválida en {cara}: {key}")
                        return None

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear coordenadas: {e}")
            return None

    def split_mixed_page(self, image_bytes: bytes) -> Optional[Tuple[bytes, bytes]]:
        """Divide una página mixta en dos imágenes separadas.
        Splits a mixed page into two separate images."""
        coordinates = self.get_split_coordinates(image_bytes)

        if coordinates is None:
            # Fallback: dividir por la mitad
            # Fallback: split in half
            try:
                img = Image.open(io.BytesIO(image_bytes))
                width, height = img.size
                mid = height // 2

                # Parte superior
                # Top part
                top = img.crop((0, 0, width, mid))
                top_bytes = io.BytesIO()
                top.save(top_bytes, format='JPEG', quality=85)
                top_bytes = top_bytes.getvalue()

                # Parte inferior
                # Bottom part
                bottom = img.crop((0, mid, width, height))
                bottom_bytes = io.BytesIO()
                bottom.save(bottom_bytes, format='JPEG', quality=85)
                bottom_bytes = bottom_bytes.getvalue()

                return (top_bytes, bottom_bytes)
            except Exception as e:
                logger.error(f"Error al dividir por mitad: {e}")
                return None

        return split_image_by_coordinates(image_bytes, coordinates)

    def detect_and_split(self, image_bytes: bytes) -> Optional[Tuple[bytes, bytes]]:
        """Detecta si una página es mixta y, si lo es, la divide.
        Detects if a page is mixed and, if so, splits it."""
        if not self.is_mixed(image_bytes):
            return None
        return self.split_mixed_page(image_bytes)


# Instancia global del detector para reutilizar
# Global detector instance for reuse
_detector_instance = None


def get_detector() -> MixedFaceDetector:
    """Retorna la instancia global del detector (singleton pattern).
    Returns the global detector instance (singleton pattern)."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = MixedFaceDetector()
    return _detector_instance
