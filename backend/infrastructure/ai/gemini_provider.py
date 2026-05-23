"""
Implementación del proveedor de IA usando Google Gemini.
Migrado al nuevo SDK google-genai (reemplaza google-generativeai deprecado).

Implementation of the AI provider using Google Gemini.
Migrated to the new SDK google-genai (replaces deprecated google-generativeai).
"""

import logging
import json
from typing import Dict, Any, Optional

from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import get_settings, DOCUMENT_TYPE_MAPPING
from core.exceptions import AIServiceError, AIServiceTimeoutError
from application.services.interfaces.ai_provider import (
    AIProvider,
    AIClassification,
    AIExtraction,
    PromptType
)
from infrastructure.ai.response_parser import JSONResponseParser, get_parser

logger = logging.getLogger(__name__)


class GeminiAIProvider(AIProvider):
    """
    Implementación de AIProvider usando Google Gemini (SDK google-genai).

    Attributes:
        client: Cliente de Gemini
        model_name: Nombre del modelo
        parser: Parser de respuestas JSON

    Implementation of AIProvider using Google Gemini (google-genai SDK).

    Attributes:
        client: Gemini client
        model_name: Model name
        parser: JSON response parser
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Inicializa el proveedor de Gemini con el nuevo SDK.

        Args:
            api_key: API key de Gemini (opcional, usa de config si no se especifica)
            model_name: Nombre del modelo (opcional, usa de config si no se especifica)
            timeout: Timeout en segundos (opcional, usa de config si no se especifica)

        Initializes the Gemini provider with the new SDK.

        Args:
            api_key: Gemini API key (optional, uses config if not specified)
            model_name: Model name (optional, uses config if not specified)
            timeout: Timeout in seconds (optional, uses config if not specified)
        """
        settings = get_settings()

        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model
        self.timeout = timeout or settings.ai_request_timeout

        # Crear cliente con el nuevo SDK
        # Create client with the new SDK
        self.client = genai.Client(api_key=self.api_key)

        # Parser de respuestas
        # Response parser
        self.parser = get_parser(strict_mode=True)

        logger.info(
            "GeminiAIProvider inicializado",
            extra={
                "model": self.model_name,
                "timeout": self.timeout
            }
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((AIServiceError,)),
        before_sleep=lambda _: logger.warning("Reintentando llamada a IA...")
    )
    async def _generate_content(
        self,
        prompt: str,
        image_bytes: bytes
    ) -> str:
        """
        Genera contenido usando Gemini con reintentos.

        Args:
            prompt: Prompt para enviar
            image_bytes: Imagen en bytes

        Returns:
            Texto de respuesta

        Raises:
            AIServiceError: Si falla después de los reintentos
            AIServiceTimeoutError: Si ocurre un timeout

        Generates content using Gemini with retries.

        Args:
            prompt: Prompt to send
            image_bytes: Image in bytes

        Returns:
            Response text

        Raises:
            AIServiceError: If it fails after retries
            AIServiceTimeoutError: If a timeout occurs
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )
            return response.text
        except Exception as e:
            error_str = str(e).lower()
            if "timeout" in error_str:
                raise AIServiceTimeoutError(
                    f"Timeout en llamada a IA: {str(e)}",
                    timeout_seconds=self.timeout
                )
            if "blocked" in error_str or "safety" in error_str:
                raise AIServiceError("Prompt bloqueado por políticas de seguridad", original_error=e)
            raise AIServiceError(f"Error en llamada a IA: {str(e)}", original_error=e)

    async def classify_image(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None
    ) -> AIClassification:
        """Clasifica una imagen de documento."""
        # Classifies a document image.
        if prompt is None:
            from .prompt_manager import get_prompt_manager
            prompt_manager = get_prompt_manager()
            prompt = prompt_manager.get_prompt(PromptType.CLASSIFICATION)

        try:
            response_text = await self._generate_content(prompt, image_bytes)
            result = self.parser.parse(response_text)

            # Validar campos requeridos
            # Validate required fields
            required_fields = ["face_type", "document_type", "confidence"]
            result = self.parser.ensure_required_fields(
                result, required_fields, optional_fields=["features"]
            )

            # Validar face_type
            # Validate face_type
            valid_face_types = ["FRONTAL", "TRASERA", "COMPLETO", "MIXTO", "DESCONOCIDO"]
            if result.get("face_type") not in valid_face_types:
                result["face_type"] = "DESCONOCIDO"

            # Validar document_type
            # Validate document_type
            if result.get("document_type") not in DOCUMENT_TYPE_MAPPING:
                result["document_type"] = "otro"

            # Validar confidence
            # Validate confidence
            try:
                confidence = float(result.get("confidence", 0.5))
                result["confidence"] = max(0.0, min(1.0, confidence))
            except (ValueError, TypeError):
                result["confidence"] = 0.5

            # Validar features
            # Validate features
            if not isinstance(result.get("features"), dict):
                result["features"] = {
                    "has_photo": False, "has_signature": False,
                    "has_fingerprint": False, "has_number": False
                }

            classification = AIClassification(
                face_type=result["face_type"],
                document_type=result["document_type"],
                confidence=result["confidence"],
                features=result["features"]
            )

            logger.debug(
                "Imagen clasificada",
                extra={
                    "face_type": classification.face_type,
                    "document_type": classification.document_type,
                    "confidence": classification.confidence
                }
            )

            return classification

        except AIServiceTimeoutError:
            raise
        except AIServiceError:
            raise
        except Exception as e:
            logger.error(f"Error al clasificar imagen: {e}", exc_info=True)
            raise AIServiceError(f"Error al clasificar imagen: {str(e)}", original_error=e)

    async def extract_data(
        self,
        image_bytes: bytes,
        document_type: str,
        face_type: str,
        prompt: Optional[str] = None
    ) -> AIExtraction:
        """Extrae datos de una imagen de documento."""
        # Extracts data from a document image.
        if prompt is None:
            from .prompt_manager import get_prompt_manager
            prompt_manager = get_prompt_manager()
            prompt = prompt_manager.get_extraction_prompt(document_type, face_type)

        try:
            response_text = await self._generate_content(prompt, image_bytes)
            result = self.parser.parse(response_text)

            # Asegurar tipo de documento
            # Ensure document type
            if not result.get("tipo_documento"):
                result["tipo_documento"] = DOCUMENT_TYPE_MAPPING.get(
                    document_type,
                    document_type.replace("_", " ").title()
                )

            # Asegurar campos requeridos y opcionales
            # Ensure required and optional fields
            from config import REQUIRED_FIELDS, OPTIONAL_FIELDS
            result = self.parser.ensure_required_fields(
                result, REQUIRED_FIELDS, OPTIONAL_FIELDS
            )

            logger.debug(
                "Datos extraídos",
                extra={
                    "document_type": document_type,
                    "face_type": face_type,
                    "fields": len(result)
                }
            )

            return AIExtraction(
                data=result,
                raw_response=response_text,
                prompt_used=prompt
            )

        except AIServiceTimeoutError:
            raise
        except AIServiceError:
            raise
        except Exception as e:
            logger.error(f"Error al extraer datos: {e}", exc_info=True)
            raise AIServiceError(f"Error al extraer datos: {str(e)}", original_error=e)

    async def extract_data_from_two_faces(
        self,
        frontal_image: bytes,
        trasera_image: bytes,
        document_type: str,
        frontal_prompt: Optional[str] = None,
        trasera_prompt: Optional[str] = None
    ) -> tuple[AIExtraction, AIExtraction]:
        """Extrae datos de dos caras de un documento."""
        # Extracts data from two faces of a document.
        frontal_data = await self.extract_data(
            frontal_image, document_type, "frontal", frontal_prompt
        )
        trasera_data = await self.extract_data(
            trasera_image, document_type, "trasera", trasera_prompt
        )
        return frontal_data, trasera_data

    async def detect_mixed_page(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None
    ) -> bool:
        """Detecta si una página contiene dos caras (mixta)."""
        # Detects whether a page contains two faces (mixed).
        if prompt is None:
            from .prompt_manager import get_prompt_manager
            prompt_manager = get_prompt_manager()
            prompt = prompt_manager.get_prompt(PromptType.MIXED_DETECTION)

        try:
            response_text = await self._generate_content(prompt, image_bytes)
            response_text = response_text.strip().upper()

            is_mixed = response_text == "SI"

            logger.debug(
                f"Detección de página mixta: {is_mixed}",
                extra={"response": response_text}
            )

            return is_mixed

        except (AIServiceTimeoutError, AIServiceError):
            logger.warning("Error en detección de página mixta, asumiendo NO")
            return False

    async def get_split_coordinates(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None
    ) -> Optional[Dict[str, Dict[str, int]]]:
        """Obtiene coordenadas para dividir una página mixta."""
        # Gets coordinates to split a mixed page.
        if prompt is None:
            from .prompt_manager import get_prompt_manager
            prompt_manager = get_prompt_manager()
            prompt = prompt_manager.get_prompt(PromptType.SPLIT_COORDINATES)

        try:
            response_text = await self._generate_content(prompt, image_bytes)
            result = self.parser.parse(response_text)

            if not ("cara_1" in result and "cara_2" in result):
                logger.warning("Respuesta de coordenadas no tiene la estructura esperada")
                return None

            for cara in ["cara_1", "cara_2"]:
                coords = result[cara]
                required_keys = ["y_inicio", "y_fin", "x_inicio", "x_fin"]
                if not all(key in coords for key in required_keys):
                    logger.warning(f"Coordenada inválida en {cara}")
                    return None

            logger.debug("Coordenadas de división obtenidas exitosamente")
            return result

        except (AIServiceTimeoutError, AIServiceError):
            return None
        except Exception as e:
            logger.error(f"Error al obtener coordenadas: {e}")
            return None

    def get_model_name(self) -> str:
        """Retorna el nombre del modelo de IA."""
        # Returns the AI model name.
        return self.model_name

    def is_available(self) -> bool:
        """Verifica si el servicio de IA está disponible."""
        # Verifies if the AI service is available.
        try:
            self.client.models.generate_content(
                model=self.model_name,
                contents="test"
            )
            return True
        except Exception as e:
            logger.warning(f"Gemini no disponible: {e}")
            return False
