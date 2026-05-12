"""
Interfaz para proveedores de Inteligencia Artificial.
Permite cambiar entre diferentes proveedores (Gemini, GPT, Claude, etc.) sin modificar el código de negocio.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class PromptType(Enum):
    """Tipos de prompts para la IA."""
    CLASSIFICATION = "clasificar_cara"
    EXTRACTION = "extraction"
    MIXED_DETECTION = "detectar_mixto"
    SPLIT_COORDINATES = "coordenadas_division"


@dataclass
class AIClassification:
    """Resultado de clasificación de una imagen por la IA."""

    face_type: str  # FRONTAL, TRASERA, COMPLETO, MIXTO
    document_type: str
    confidence: float
    features: Dict[str, bool]

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "face_type": self.face_type,
            "document_type": self.document_type,
            "confidence": self.confidence,
            "features": self.features
        }


@dataclass
class AIExtraction:
    """Resultado de extracción de datos de una imagen por la IA."""

    data: Dict[str, str]
    raw_response: str
    prompt_used: str

    def to_dict(self) -> Dict[str, str]:
        """Convierte los datos extraídos a diccionario."""
        return self.data.copy()


@dataclass
class AIResponse:
    """Respuesta genérica de la IA."""

    text: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class AIProvider(ABC):
    """
    Interfaz abstracta para proveedores de IA.

    Implementaciones específicas (Gemini, OpenAI, Anthropic, etc.)
    deben heredar de esta clase.
    """

    @abstractmethod
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

        Raises:
            AIServiceError: Si falla la clasificación
            AIServiceTimeoutError: Si ocurre un timeout
        """
        pass

    @abstractmethod
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

        Raises:
            AIServiceError: Si falla la extracción
            AIServiceTimeoutError: Si ocurre un timeout
        """
        pass

    @abstractmethod
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

        Raises:
            AIServiceError: Si falla la extracción
            AIServiceTimeoutError: Si ocurre un timeout
        """
        pass

    @abstractmethod
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

        Raises:
            AIServiceError: Si falla la detección
            AIServiceTimeoutError: Si ocurre un timeout
        """
        pass

    @abstractmethod
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

        Raises:
            AIServiceError: Si falla la obtención de coordenadas
            AIServiceTimeoutError: Si ocurre un timeout
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Retorna el nombre del modelo de IA.

        Returns:
            Nombre del modelo
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica si el servicio de IA está disponible.

        Returns:
            True si está disponible
        """
        pass
