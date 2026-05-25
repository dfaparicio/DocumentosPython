"""
Router para gestionar la API key de Gemini desde el frontend.
Endpoints CRUD para configurar, consultar y eliminar la key.

Router for managing the Gemini API key from the frontend.
CRUD endpoints for configuring, querying and deleting the key.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.api_key_store import (
    get_api_key,
    save_api_key,
    delete_api_key,
    is_configured,
    get_masked_key
)

logger = logging.getLogger(__name__)

# Creamos el router
# We create the router
router = APIRouter(prefix="/api/config", tags=["configuración"])


class ApiKeyRequest(BaseModel):
    """Modelo para recibir la API key.
    Model for receiving the API key."""
    api_key: str


class ApiKeyStatusResponse(BaseModel):
    """Modelo para responder el estado de la API key.
    Model for responding with the API key status."""
    configured: bool
    masked: Optional[str] = None


@router.get("/api-key", response_model=ApiKeyStatusResponse)
async def get_api_key_status():
    """
    Retorna si hay API key configurada y su versión enmascarada.
    Nunca retorna la key completa por seguridad.

    Returns whether an API key is configured and its masked version.
    Never returns the full key for security.
    """
    return ApiKeyStatusResponse(
        configured=is_configured(),
        masked=get_masked_key()
    )


@router.put("/api-key")
async def update_api_key(request: ApiKeyRequest):
    """
    Guarda o actualiza la API key de Gemini.

    Args:
        request: Body con { "api_key": "AIza..." }

    Saves or updates the Gemini API key.

    Args:
        request: Body with { "api_key": "AIza..." }
    """
    api_key = request.api_key.strip()

    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="La API key no puede estar vacía"
        )

    if not api_key.startswith("AIza"):
        raise HTTPException(
            status_code=400,
            detail="La API key debe comenzar con 'AIza'"
        )

    try:
        save_api_key(api_key)
        logger.info("API key actualizada desde el frontend")
        return {
            "message": "API key guardada exitosamente",
            "masked": get_masked_key()
        }
    except Exception as e:
        logger.error(f"Error al guardar API key: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al guardar la API key"
        )


@router.delete("/api-key")
async def remove_api_key():
    """
    Elimina la API key guardada.
    Deletes the saved API key.
    """
    deleted = delete_api_key()
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="No hay API key configurada para eliminar"
        )

    logger.info("API key eliminada desde el frontend")
    return {"message": "API key eliminada exitosamente"}
