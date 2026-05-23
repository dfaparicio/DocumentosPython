"""
Configuración de la aplicación usando pydantic-settings.
Centraliza todas las variables de entorno con validación de tipos.

Application configuration using pydantic-settings.
Centralizes all environment variables with type validation.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación con validación.

    Application configuration with validation.
    """

    # API de Gemini
    # Gemini API
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY", description="API key de Google Gemini")
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        env="GEMINI_MODEL",
        description="Modelo de Gemini a usar"
    )

    # Timeout y límites
    # Timeout and limits
    ai_request_timeout: int = Field(
        default=30,
        env="AI_REQUEST_TIMEOUT",
        description="Timeout en segundos para llamadas a IA"
    )
    max_concurrent_ai_requests: int = Field(
        default=5,
        env="MAX_CONCURRENT_AI_REQUESTS",
        description="Máximo de llamadas concurrentes a IA"
    )
    max_workers: int = Field(
        default=4,
        env="MAX_WORKERS",
        description="Máximo de workers para ThreadPoolExecutor"
    )

    # Configuración de PDF
    # PDF configuration
    default_dpi: int = Field(default=100, env="DEFAULT_DPI", description="DPI para conversión de PDF a imágenes")
    max_pdf_pages: int = Field(default=100, env="MAX_PDF_PAGES", description="Máximo de páginas en PDF")

    # Configuración de archivos
    # File configuration
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB", description="Máximo tamaño de archivo en MB")
    allowed_file_types: list = Field(
        default=["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
        env="ALLOWED_FILE_TYPES",
        description="Tipos de archivo permitidos"
    )

    # Configuración de caché
    # Cache configuration
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS", description="TTL del caché en segundos")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE", description="Tamaño máximo del caché")

    # Configuración de rate limiting
    # Rate limiting configuration
    rate_limit_requests_per_minute: int = Field(
        default=60,
        env="RATE_LIMIT_REQUESTS_PER_MINUTE",
        description="Máximo de requests por minuto"
    )

    # Configuración de logging
    # Logging configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Nivel de logging")
    log_dir: str = Field(default="logs", env="LOG_DIR", description="Directorio de logs")

    # Validar que gemini_api_key no esté vacía
    # Validate that gemini_api_key is not empty
    @validator("gemini_api_key")
    def validate_gemini_api_key(cls, v):
        if not v or v.strip() == "":
            raise ValueError("GEMINI_API_KEY no puede estar vacía")
        return v

    # Validar niveles de logging válidos
    # Validate valid logging levels
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL debe ser uno de: {valid_levels}")
        return v.upper()

    class Config:
        """Configuración de pydantic-settings.

        Pydantic-settings configuration.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia global de configuración
# Global configuration instance
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Retorna la instancia singleton de configuración.

    Returns the singleton configuration instance.

    Args:
        Instancia de Settings
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
