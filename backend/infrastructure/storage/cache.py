"""
Gestor de caché en memoria con TTL.
Usa cachetools para implementar caché con expiración.
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

    Attributes:
        cache: Caché TTL de cachetools
        ttl_seconds: Tiempo de vida en segundos
        max_size: Tamaño máximo del caché
    """

    def __init__(
        self,
        ttl_seconds: Optional[int] = None,
        max_size: Optional[int] = None
    ):
        """
        Inicializa el gestor de caché.

        Args:
            ttl_seconds: Tiempo de vida en segundos
            max_size: Tamaño máximo del caché
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

        Args:
            key: Clave del valor

        Returns:
            Valor almacenado o None si no existe o expiró
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

        Args:
            key: Clave del valor
            value: Valor a almacenar
        """
        self.cache[key] = value
        logger.debug(f"Valor almacenado en caché: {key}")

    def delete(self, key: str) -> bool:
        """
        Elimina un valor del caché.

        Args:
            key: Clave del valor

        Returns:
            True si se eliminó, False si no existía
        """
        try:
            del self.cache[key]
            logger.debug(f"Valor eliminado del caché: {key}")
            return True
        except KeyError:
            return False

    def clear(self) -> None:
        """Limpia todo el caché."""
        self.cache.clear()
        logger.info("Caché limpiado")

    def get_stats(self) -> dict:
        """
        Retorna estadísticas del caché.

        Returns:
            Diccionario con estadísticas
        """
        return {
            "current_size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }

    def cache_function_result(self, ttl: Optional[int] = None):
        """
        Decorador para cachear resultados de funciones.

        Args:
            ttl: TTL específico para esta función (opcional)

        Returns:
            Decorador
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                # Crear clave desde los argumentos
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

                # Intentar obtener del caché
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value

                # Ejecutar función y cachear resultado
                result = func(*args, **kwargs)
                self.set(key, result)
                return result

            return wrapper
        return decorator


# Instancia global del caché
_cache_instance: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """
    Retorna la instancia singleton del caché.

    Returns:
        Instancia de CacheManager
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance


def clear_cache() -> None:
    """Limpia el caché global."""
    cache = get_cache()
    cache.clear()
