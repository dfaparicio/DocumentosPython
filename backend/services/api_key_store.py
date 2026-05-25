"""
Servicio para almacenar la API key de Gemini en un archivo JSON.
Permite configurar la key desde el frontend sin necesidad de .env.

Service for storing the Gemini API key in a JSON file.
Allows configuring the key from the frontend without needing .env.
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Ruta del archivo JSON donde se guarda la key
# Path of the JSON file where the key is stored
_CONFIG_DIR = Path(__file__).parent.parent / "config"
_API_KEY_FILE = _CONFIG_DIR / "api_key.json"


def _ensure_config_dir():
    """Asegura que el directorio config existe.
    Ensures the config directory exists."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def get_api_key() -> Optional[str]:
    """
    Obtiene la API key de Gemini.
    Primero busca en el archivo JSON, luego en .env como fallback.

    Returns:
        La API key o None si no está configurada

    Gets the Gemini API key.
    First checks the JSON file, then .env as fallback.

    Returns:
        The API key or None if not configured
    """
    # Intentar leer del archivo JSON
    # Try to read from the JSON file
    if _API_KEY_FILE.exists():
        try:
            with open(_API_KEY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                key = data.get("gemini_api_key", "").strip()
                if key:
                    return key
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error al leer api_key.json: {e}")

    # Fallback: leer del .env
    # Fallback: read from .env
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key

    return None


def save_api_key(api_key: str) -> None:
    """
    Guarda la API key en el archivo JSON.

    Args:
        api_key: La API key de Gemini

    Saves the API key to the JSON file.

    Args:
        api_key: The Gemini API key
    """
    _ensure_config_dir()

    data = {
        "gemini_api_key": api_key.strip(),
        "updated_at": datetime.now().isoformat()
    }

    with open(_API_KEY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("API key guardada exitosamente")


def delete_api_key() -> bool:
    """
    Elimina el archivo con la API key.

    Returns:
        True si se eliminó, False si no existía

    Deletes the API key file.

    Returns:
        True if deleted, False if it didn't exist
    """
    if _API_KEY_FILE.exists():
        _API_KEY_FILE.unlink()
        logger.info("API key eliminada")
        return True
    return False


def is_configured() -> bool:
    """
    Retorna True si hay una API key configurada.
    Returns True if an API key is configured.
    """
    return get_api_key() is not None


def get_masked_key() -> Optional[str]:
    """
    Retorna la key enmascarada para mostrar en el frontend.
    Ejemplo: "AIza...Kt0"

    Returns:
        La key enmascarada o None si no hay key

    Returns the masked key for display in the frontend.
    Example: "AIza...Kt0"

    Returns:
        The masked key or None if no key
    """
    key = get_api_key()
    if not key:
        return None

    if len(key) <= 8:
        return key[:2] + "..." + key[-2:]

    return key[:4] + "..." + key[-3:]
