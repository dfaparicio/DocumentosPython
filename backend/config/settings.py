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
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY", description="API key de Google Gemini")
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

    # Configuración de MongoDB
    # MongoDB configuration
    mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        env="MONGODB_URL",
        description="URL de conexión a MongoDB"
    )
    mongodb_db_name: str = Field(
        default="cedulas_extractor",
        env="MONGODB_DB_NAME",
        description="Nombre de la base de datos MongoDB"
    )

    # Configuración de JWT
    # JWT configuration
    jwt_secret_key: str = Field(
        default="tu-clave-secreta-cambiar-en-produccion",
        env="JWT_SECRET_KEY",
        description="Clave secreta para firmar tokens JWT"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        env="JWT_ALGORITHM",
        description="Algoritmo de firmado JWT"
    )
    jwt_expire_minutes: int = Field(
        default=60,
        env="JWT_EXPIRE_MINUTES",
        description="Minutos de expiración del token JWT"
    )

    # Usuario admin por defecto
    # Default admin user
    admin_email: str = Field(
        default="admin@sistema.com",
        env="ADMIN_EMAIL",
        description="Email del usuario admin por defecto"
    )
    admin_password: str = Field(
        default="admin123",
        env="ADMIN_PASSWORD",
        description="Contraseña del usuario admin por defecto"
    )

    # Configuración SMTP (Gmail)
    # SMTP configuration (Gmail)
    smtp_host: str = Field(
        default="smtp.gmail.com",
        env="SMTP_HOST",
        description="Host del servidor SMTP"
    )
    smtp_port: int = Field(
        default=587,
        env="SMTP_PORT",
        description="Puerto del servidor SMTP"
    )
    smtp_user: str = Field(
        default="",
        env="SMTP_USER",
        description="Email de la cuenta Gmail remitente"
    )
    smtp_password: str = Field(
        default="",
        env="SMTP_PASSWORD",
        description="Contraseña de aplicación Gmail"
    )
    smtp_from_name: str = Field(
        default="Sistema Cédulas",
        env="SMTP_FROM_NAME",
        description="Nombre visible del remitente"
    )

    # Configuración de código de recuperación
    # Reset code configuration
    reset_code_expire_minutes: int = Field(
        default=10,
        env="RESET_CODE_EXPIRE_MINUTES",
        description="Minutos de expiración del código de recuperación"
    )

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
