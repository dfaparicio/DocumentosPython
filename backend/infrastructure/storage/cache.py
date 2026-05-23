"""
Gestor de caché en memoria con TTL.
Usa cachetools para implementar caché con expiración.

In-memory cache manager with TTL.
Uses cachetools to implement cache with expiration.
"""

import logging
from functools import lru_cache
from typing import Any, Optional, Callable
from datetime import timedelta

import cachetools

from config import get_settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gestor de caché en memoria con TTL.
    In-memory cache manager with TTL.

    Attributes:
        cache: Caché TTL de cachetools / cachetools TTL cache
        ttl_seconds: Tiempo de vida en segundos / Time to live in seconds
        max_size: Tamaño máximo del caché / Maximum cache size
    """

    def __init__(
        self,
        ttl_seconds: Optional[int] = None,
        max_size: Optional[int] = None
    ):
        """
        Inicializa el gestor de caché.
        Initializes the cache manager.

        Args:
            ttl_seconds: Tiempo de vida en segundos / Time to live in seconds
            max_size: Tamaño máximo del caché / Maximum cache size
        """
        settings = get_settings()

        self.ttl_seconds = ttl_seconds or settings.cache_ttl_seconds
        self.max_size = max_size or settings.cache_max_size

        self.cache = cachetools.TTLCache(
            maxsize=self.max_size,
            ttl=self.ttl_seconds
        )

        logger.info(
            "Cache inicializado",
            extra={"ttl_seconds": self.ttl_seconds, "max_size": self.max_size}
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché.
        Gets a value from the cache.

        Args:
            key: Clave del valor / Value key

        Returns:
            Valor almacenado o None si no existe o expiró / Stored value or None if it does not exist or has expired
        """
        try:
            value = self.cache.get(key)
            if value is not None:
                logger.debug(f"Cache hit: {key}")
            else:
                logger.debug(f"Cache miss: {key}")
            return value
        except KeyError:
            return None

    def set(self, key: str, value: Any) -> None:
        """
        Almacena un valor en el caché.
        Stores a value in the cache.

        Args:
            key: Clave del valor / Value key
            value: Valor a almacenar / Value to store
        """
        self.cache[key] = value
        logger.debug(f"Valor almacenado en caché: {key}")

    def delete(self, key: str) -> bool:
        """
        Elimina un valor del caché.
        Deletes a value from the cache.

        Args:
            key: Clave del valor / Value key

        Returns:
            True si se eliminó, False si no existía / True if deleted, False if it did not exist
        """
        try:
            del self.cache[key]
            logger.debug(f"Valor eliminado del caché: {key}")
            return True
        except KeyError:
            return False

    def clear(self) -> None:
        """Limpia todo el caché.
        Clears the entire cache."""
        self.cache.clear()
        logger.info("Caché limpiado")

    def get_stats(self) -> dict:
        """
        Retorna estadísticas del caché.
        Returns cache statistics.

        Returns:
            Diccionario con estadísticas / Dictionary with statistics
        """
        return {
            "current_size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }

    def cache_function_result(self, ttl: Optional[int] = None):
        """
        Decorador para cachear resultados de funciones.
        Decorator to cache function results.

        Args:
            ttl: TTL específico para esta función (opcional) / Specific TTL for this function (optional)

        Returns:
            Decorador / Decorator
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                # Crear clave desde los argumentos
                # Create key from arguments
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

                # Intentar obtener del caché
                # Try to get from cache
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value

                # Ejecutar función y cachear resultado
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(key, result)
                return result

            return wrapper
        return decorator


# Instancia global del caché
# Global cache instance
_cache_instance: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """
    Retorna la instancia singleton del caché.
    Returns the singleton instance of the cache.

    Returns:
        Instancia de CacheManager / CacheManager instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance


def clear_cache() -> None:
    """Limpia el caché global.
    Clears the global cache."""
    cache = get_cache()
    cache.clear()
