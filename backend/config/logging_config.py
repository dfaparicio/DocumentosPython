"""
Configuración de logging profesional con rotación de archivos.
Reemplaza los 32 print() del código original.

Professional logging configuration with file rotation.
Replaces the 32 print() calls from the original code.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from .settings import get_settings


def setup_logging(
    log_level: Optional[str] = None,
    log_dir: Optional[str] = None
) -> logging.Logger:
    """
    Configura logging con rotación y múltiples handlers.

    Sets up logging with rotation and multiple handlers.

    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directorio donde guardar los logs
            Directory where logs are saved

    Returns:
        Logger configurado
        Configured logger
    """
    settings = get_settings()

    # Usar valores de configuración si no se especifican
    # Use configuration values if not specified
    log_level = log_level or settings.log_level
    log_dir = log_dir or settings.log_dir

    # Crear directorio de logs
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True, parents=True)

    # Obtener nivel de logging
    # Get logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configurar logger raíz
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Evitar duplicar handlers si ya están configurados
    # Avoid duplicating handlers if already configured
    if logger.handlers:
        return logger

    # Formateador
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para consola
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para archivo general (con rotación diaria)
    # General file handler (with daily rotation)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_path / "app.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para errores separado (solo ERROR y CRITICAL)
    # Separate error handler (ERROR and CRITICAL only)
    error_handler = logging.handlers.TimedRotatingFileHandler(
        log_path / "errors.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # Log inicial
    # Initial log
    logger.info("Logging configurado exitosamente", extra={
        "log_level": log_level,
        "log_dir": str(log_path.absolute())
    })

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Retorna un logger para un módulo específico.

    Returns a logger for a specific module.

    Args:
        name: Nombre del módulo (usualmente __name__)
            Module name (usually __name__)

    Returns:
        Logger configurado
        Configured logger
    """
    return logging.getLogger(name)
