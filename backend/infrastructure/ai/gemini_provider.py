"""
Implementación del proveedor de IA usando Google Gemini.
Reemplaza ai_service.py, face_classifier.py y mixed_face_detector.py.
"""

import logging
import json
from typing import Dict, Any, Optional

import google.generativeai as genai
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
    Implementación de AIProvider usando Google Gemini.

    Attributes:
        model: Modelo de Gemini
        parser: Parser de respuestas JSON
        settings: Configuración de la aplicación
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Inicializa el proveedor de Gemini.

        Args:
            api_key: API key de Gemini (opcional, usa de config si no se especifica)
            model_name: Nombre del modelo (opcional, usa de config si no se especifica)
            timeout: Timeout en segundos (opcional, usa de config si no se especifica)
        """
        settings = get_settings()

        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model
        self.timeout = timeout or settings.ai_request_timeout

        # Configurar Gemini
        genai.configure(api_key=self.api_key)

        # Crear modelo
        self.model = genai.GenerativeModel(self.model_name)

        # Parser de respuestas
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
        """
        try:
            response = self.model.generate_content(
                [
                    prompt,
                    {"mime_type": "image/png", "data": image_bytes}
                ]
            )
            return response.text
        except genai.types.BlockedPromptException as e:
            logger.error(f"Prompt bloqueado por Gemini: {e}")
            raise AIServiceError("Prompt bloqueado por políticas de seguridad", original_error=e)
        except genai.types.StopCandidateException as e:
            logger.error(f"Candidato detenido por Gemini: {e}")
            raise AIServiceError("Respuesta detenia por el modelo", original_error=e)
        except Exception as e:
            if "timeout" in str(e).lower():
                raise AIServiceTimeoutError(
                    f"Timeout en llamada a IA: {str(e)}",
                    timeout_seconds=self.timeout
                )
            raise AIServiceError(f"Error en llamada a IA: {str(e)}", original_error=e)

    async def classify_image(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None
    ) -> AIClassification:
        """
        Clasifica una imagen de documento.

        Args:
            image_bytes: Imagen en bytes
            prompt: Prompt específico (opcional)

        Returns:
            Resultado de clasificación
        """
        if prompt is None:
            from .prompt_manager import get_prompt_manager
            prompt_manager = get_prompt_manager()
            prompt = prompt_manager.get_prompt(PromptType.CLASSIFICATION)

        try:
            response_text = await self._generate_content(prompt, image_bytes)
            result = self.parser.parse(response_text)

            # Validar campos requeridos
            required_fields = ["face_type", "document_type", "confidence"]
            result = self.parser.ensure_required_fields(
                result,
                required_fields,
                optional_fields=["features"]
            )

            # Validar face_type
            valid_face_types = ["FRONTAL", "TRASERA", "COMPLETO", "MIXTO", "DESCONOCIDO"]
            if result.get("face_type") not in valid_face_types:
                result["face_type"] = "DESCONOCIDO"

            # Validar document_type
            if result.get("document_type") not in DOCUMENT_TYPE_MAPPING:
                result["document_type"] = "otro"

            # Validar confidence
            try:
                confidence = float(result.get("confidence", 0.5))
                result["confidence"] = max(0.0, min(1.0, confidence))
            except (ValueError, TypeError):
                result["confidence"] = 0.5

            # Validar features
            if not isinstance(result.get("features"), dict):
                result["features"] = {
                    "has_photo": False,
                    "has_signature": False,
                    "has_fingerprint": False,
                    "has_number": False
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
        """
        Extrae datos de una imagen de documento.

        Args:
            image_bytes: Imagen en bytes
            document_type: Tipo de documento
            face_type: Tipo de cara (frontal, trasera, completo)
            prompt: Prompt específico (opcional)

        Returns:
            Datos extraídos
        """
        if prompt is None:
            from .prompt_manager import get_prompt_manager
            prompt_manager = get_prompt_manager()
            prompt = prompt_manager.get_extraction_prompt(document_type, face_type)

        try:
            response_text = await self._generate_content(prompt, image_bytes)
            result = self.parser.parse(response_text)

            # Asegurar tipo de documento
            if not result.get("tipo_documento"):
                result["tipo_documento"] = DOCUMENT_TYPE_MAPPING.get(
                    document_type,
                    document_type.replace("_", " ").title()
                )

            # Asegurar campos requeridos y opcionales
            from config import REQUIRED_FIELDS, OPTIONAL_FIELDS
            result = self.parser.ensure_required_fields(
                result,
                REQUIRED_FIELDS,
                OPTIONAL_FIELDS
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
        """
        Extrae datos de dos caras de un documento.

        Args:
            frontal_image: Imagen de la cara frontal
            trasera_image: Imagen de la cara trasera
            document_type: Tipo de documento
            frontal_prompt: Prompt para cara frontal (opcional)
            trasera_prompt: Prompt para cara trasera (opcional)

        Returns:
            Tupla (datos_frontal, datos_trasera)
        """
        # Extraer datos de ambas caras (secuencial para mantener orden)
        frontal_data = await self.extract_data(
            frontal_image,
            document_type,
            "frontal",
            frontal_prompt
        )

        trasera_data = await self.extract_data(
            trasera_image,
            document_type,
            "trasera",
            trasera_prompt
        )

        return frontal_data, trasera_data

    async def detect_mixed_page(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None
    ) -> bool:
        """
        Detecta si una página contiene dos caras (mixta).

        Args:
            image_bytes: Imagen en bytes
            prompt: Prompt específico (opcional)

        Returns:
            True si es mixta, False en caso contrario
        """
        if prompt is None:
            from .prompt_manager import get_prompt_manager
            prompt_manager = get_prompt_manager()
            prompt = prompt_manager.get_prompt(PromptType.MIXED_DETECTION)

        try:
            response_text = await self._generate_content(prompt, image_bytes)
            # Respuesta esperada: "SI" o "NO"
            response_text = response_text.strip().upper()

            is_mixed = response_text == "SI"

            logger.debug(
                f"Detección de página mixta: {is_mixed}",
                extra={"response": response_text}
            )

            return is_mixed

        except AIServiceTimeoutError:
            # Por seguridad, si hay timeout, asumimos que no es mixto
            logger.warning("Timeout en detección de página mixta, asumiendo NO")
            return False
        except AIServiceError:
            # Por seguridad, si hay error, asumimos que no es mixto
            logger.warning("Error en detección de página mixta, asumiendo NO")
            return False

    async def get_split_coordinates(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None
    ) -> Optional[Dict[str, Dict[str, int]]]:
        """
        Obtiene coordenadas para dividir una página mixta.

        Args:
            image_bytes: Imagen en bytes
            prompt: Prompt específico (opcional)

        Returns:
            Coordenadas de división o None si falla
        """
        if prompt is None:
            from .prompt_manager import get_prompt_manager
            prompt_manager = get_prompt_manager()
            prompt = prompt_manager.get_prompt(PromptType.SPLIT_COORDINATES)

        try:
            response_text = await self._generate_content(prompt, image_bytes)
            result = self.parser.parse(response_text)

            # Validar estructura de coordenadas
            if not ("cara_1" in result and "cara_2" in result):
                logger.warning("Respuesta de coordenadas no tiene la estructura esperada")
                return None

            # Validar coordenadas
            for cara in ["cara_1", "cara_2"]:
                coords = result[cara]
                required_keys = ["y_inicio", "y_fin", "x_inicio", "x_fin"]
                if not all(key in coords for key in required_keys):
                    logger.warning(f"Coordenada inválida en {cara}")
                    return None

            logger.debug("Coordenadas de división obtenidas exitosamente")
            return result

        except AIServiceTimeoutError:
            return None
        except AIServiceError:
            return None
        except Exception as e:
            logger.error(f"Error al obtener coordenadas: {e}")
            return None

    def get_model_name(self) -> str:
        """
        Retorna el nombre del modelo de IA.

        Returns:
            Nombre del modelo
        """
        return self.model_name

    def is_available(self) -> bool:
        """
        Verifica si el servicio de IA está disponible.

        Returns:
            True si está disponible
        """
        try:
            # Intentar hacer un request simple
            self.model.generate_content("test")
            return True
        except Exception as e:
            logger.warning(f"Gemini no disponible: {e}")
            return False
