"""
Interfaz para proveedores de Inteligencia Artificial.
Permite cambiar entre diferentes proveedores (Gemini, GPT, Claude, etc.) sin modificar el código de negocio.

Interface for Artificial Intelligence providers.
Allows switching between different providers (Gemini, GPT, Claude, etc.) without modifying business code.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class PromptType(Enum):
    """Tipos de prompts para la IA.
    Types of prompts for the AI."""
    CLASSIFICATION = "clasificar_cara"
    EXTRACTION = "extraction"
    MIXED_DETECTION = "detectar_mixto"
    SPLIT_COORDINATES = "coordenadas_division"


@dataclass
class AIClassification:
    """Resultado de clasificación de una imagen por la IA.
    Result of classifying an image by the AI."""

    face_type: str  # FRONTAL, TRASERA, COMPLETO, MIXTO
    document_type: str
    confidence: float
    features: Dict[str, bool]

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario.
        Converts to dictionary."""
        return {
            "face_type": self.face_type,
            "document_type": self.document_type,
            "confidence": self.confidence,
            "features": self.features
        }


@dataclass
class AIExtraction:
    """Resultado de extracción de datos de una imagen por la IA.
    Result of data extraction from an image by the AI."""

    data: Dict[str, str]
    raw_response: str
    prompt_used: str

    def to_dict(self) -> Dict[str, str]:
        """Convierte los datos extraídos a diccionario.
        Converts the extracted data to a dictionary."""
        return self.data.copy()


@dataclass
class AIResponse:
    """Respuesta genérica de la IA.
    Generic AI response."""

    text: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class AIProvider(ABC):
    """
    Interfaz abstracta para proveedores de IA.
    Specific implementations (Gemini, OpenAI, Anthropic, etc.)
    deben heredar de esta clase.

    Abstract interface for AI providers.
    Specific implementations (Gemini, OpenAI, Anthropic, etc.)
    must inherit from this class.
    """

    @abstractmethod
    async def classify_image(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None
    ) -> AIClassification:
        """
        Clasifica una imagen de documento.
        Classifies a document image.

        Args:
            image_bytes: Imagen en bytes / Image in bytes
            prompt: Prompt específico (opcional) / Specific prompt (optional)

        Returns:
            Resultado de clasificación / Classification result

        Raises:
            AIServiceError: Si falla la clasificación / If classification fails
            AIServiceTimeoutError: Si ocurre un timeout / If a timeout occurs
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
        Extracts data from a document image.

        Args:
            image_bytes: Imagen en bytes / Image in bytes
            document_type: Tipo de documento / Document type
            face_type: Tipo de cara (frontal, trasera, completo) / Face type (front, back, complete)
            prompt: Prompt específico (opcional) / Specific prompt (optional)

        Returns:
            Datos extraídos / Extracted data

        Raises:
            AIServiceError: Si falla la extracción / If extraction fails
            AIServiceTimeoutError: Si ocurre un timeout / If a timeout occurs
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
        Extracts data from two faces of a document.

        Args:
            frontal_image: Imagen de la cara frontal / Front face image
            trasera_image: Imagen de la cara trasera / Back face image
            document_type: Tipo de documento / Document type
            frontal_prompt: Prompt para cara frontal (opcional) / Prompt for front face (optional)
            trasera_prompt: Prompt para cara trasera (opcional) / Prompt for back face (optional)

        Returns:
            Tupla (datos_frontal, datos_trasera) / Tuple (front_data, back_data)

        Raises:
            AIServiceError: Si falla la extracción / If extraction fails
            AIServiceTimeoutError: Si ocurre un timeout / If a timeout occurs
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
        Detects if a page contains two faces (mixed).

        Args:
            image_bytes: Imagen en bytes / Image in bytes
            prompt: Prompt específico (opcional) / Specific prompt (optional)

        Returns:
            True si es mixta, False en caso contrario / True if mixed, False otherwise

        Raises:
            AIServiceError: Si falla la detección / If detection fails
            AIServiceTimeoutError: Si ocurre un timeout / If a timeout occurs
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
        Gets coordinates to split a mixed page.

        Args:
            image_bytes: Imagen en bytes / Image in bytes
            prompt: Prompt específico (opcional) / Specific prompt (optional)

        Returns:
            Coordenadas de división o None si falla / Split coordinates or None if it fails

        Raises:
            AIServiceError: Si falla la obtención de coordenadas / If getting coordinates fails
            AIServiceTimeoutError: Si ocurre un timeout / If a timeout occurs
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Retorna el nombre del modelo de IA.
        Returns the name of the AI model.

        Returns:
            Nombre del modelo / Model name
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica si el servicio de IA está disponible.
        Verifies if the AI service is available.

        Returns:
            True si está disponible / True if available
        """
        pass
