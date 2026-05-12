"""
Factorías para inyección de dependencias.
Usa @lru_cache para crear singletons de servicios.
"""

import logging
from functools import lru_cache
from typing import Optional

from config import get_settings
from application.services.interfaces.ai_provider import AIProvider
from infrastructure.ai.gemini_provider import GeminiAIProvider
from infrastructure.ai.prompt_manager import get_prompt_manager
from infrastructure.storage.cache import CacheManager, get_cache
from infrastructure.storage.rate_limiter import RateLimiter, get_rate_limiter, AsyncSemaphoreRateLimiter, get_async_rate_limiter

logger = logging.getLogger(__name__)


@lru_cache()
def get_ai_provider() -> AIProvider:
    """
    Retorna la instancia singleton del proveedor de IA.

    Returns:
        Instancia de AIProvider
    """
    settings = get_settings()
    provider = GeminiAIProvider(
        api_key=settings.gemini_api_key,
        model_name=settings.gemini_model,
        timeout=settings.ai_request_timeout
    )
    logger.info(f"AIProvider inicializado: {provider.get_model_name()}")
    return provider


@lru_cache()
def get_cache_manager() -> CacheManager:
    """
    Retorna la instancia singleton del gestor de caché.

    Returns:
        Instancia de CacheManager
    """
    return get_cache()


@lru_cache()
def get_rate_limiter() -> RateLimiter:
    """
    Retorna la instancia singleton del rate limiter.

    Returns:
        Instancia de RateLimiter
    """
    return get_rate_limiter()


@lru_cache()
def get_async_rate_limiter() -> AsyncSemaphoreRateLimiter:
    """
    Retorna la instancia singleton del rate limiter asíncrono.

    Returns:
        Instancia de AsyncSemaphoreRateLimiter
    """
    return get_async_rate_limiter()


def reset_singletons() -> None:
    """Limpia todas las instancias singleton (útil para testing)."""
    get_ai_provider.cache_clear()
    get_cache_manager.cache_clear()
    get_rate_limiter.cache_clear()
    get_async_rate_limiter.cache_clear()
    logger.info("Singletons reseteados")
