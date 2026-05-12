"""
Rate limiter para limitar llamadas a APIs externas.
Previene exceder cuotas de servicio.
"""

import logging
import asyncio
from typing import Optional
from datetime import datetime, timedelta

from config import get_settings
from core.exceptions import AIServiceRateLimitError

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Limitador de tasa de requests.

    Permite un número máximo de requests por ventana de tiempo.
    Usa un algoritmo de ventana deslizante (sliding window).

    Attributes:
        max_requests: Máximo de requests permitidos
        window_seconds: Ventana de tiempo en segundos
        requests: Lista de timestamps de requests
    """

    def __init__(
        self,
        max_requests: Optional[int] = None,
        window_seconds: int = 60
    ):
        """
        Inicializa el rate limiter.

        Args:
            max_requests: Máximo de requests permitidos
            window_seconds: Ventana de tiempo en segundos
        """
        settings = get_settings()

        self.max_requests = max_requests or settings.rate_limit_requests_per_minute
        self.window_seconds = window_seconds

        self.requests = []

        logger.info(
            "Rate limiter inicializado",
            extra={
                "max_requests": self.max_requests,
                "window_seconds": self.window_seconds
            }
        )

    async def acquire(self) -> bool:
        """
        Intenta adquirir un permiso para hacer un request.

        Returns:
            True si se puede hacer el request

        Raises:
            AIServiceRateLimitError: Si excede el rate limit
        """
        now = datetime.now()

        # Eliminar requests antiguos fuera de la ventana
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.requests = [
            req_time for req_time in self.requests
            if req_time > cutoff
        ]

        # Verificar si podemos hacer el request
        if len(self.requests) >= self.max_requests:
            retry_after = self.window_seconds - (now - self.requests[0]).total_seconds()
            logger.warning(
                f"Rate limit excedido",
                extra={
                    "current_requests": len(self.requests),
                    "max_requests": self.max_requests,
                    "retry_after": retry_after
                }
            )
            raise AIServiceRateLimitError(
                message=f"Rate limit excedido. Máximo: {self.max_requests} requests por {self.window_seconds} segundos.",
                retry_after=int(retry_after)
            )

        # Registrar el request
        self.requests.append(now)
        logger.debug(f"Request permitido. Requests actuales: {len(self.requests)}/{self.max_requests}")
        return True

    def get_stats(self) -> dict:
        """
        Retorna estadísticas actuales.

        Returns:
            Diccionario con estadísticas
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        recent_requests = len([
            req_time for req_time in self.requests
            if req_time > cutoff
        ])

        return {
            "current_requests": recent_requests,
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds
        }

    def reset(self) -> None:
        """Resetea el contador de requests."""
        self.requests.clear()
        logger.info("Rate limiter reseteado")


# Instancia global del rate limiter
_rate_limiter_instance: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Retorna la instancia singleton del rate limiter.

    Returns:
        Instancia de RateLimiter
    """
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter()
    return _rate_limiter_instance


class AsyncSemaphoreRateLimiter:
    """
    Rate limiter asíncrono usando semáforos.

    Permite controlar el número de operaciones concurrentes.
    """

    def __init__(self, max_concurrent: int = 5):
        """
        Inicializa el rate limiter asíncrono.

        Args:
            max_concurrent: Máximo de operaciones concurrentes
        """
        settings = get_settings()

        self.max_concurrent = max_concurrent or settings.max_concurrent_ai_requests
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

        logger.info(
            "Async rate limiter inicializado",
            extra={"max_concurrent": self.max_concurrent}
        )

    async def acquire(self):
        """
        Adquiere el semáforo de forma asíncrona.

        Returns:
            Context manager para el semáforo
        """
        return self.semaphore

    async def __aenter__(self):
        """Entra al contexto del semáforo."""
        await self.semaphore.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Sale del contexto del semáforo."""
        self.semaphore.release()

    def get_available_slots(self) -> int:
        """
        Retorna el número de slots disponibles.

        Returns:
            Número de operaciones que pueden iniciarse inmediatamente
        """
        return self.max_concurrent - self.semaphore._value


# Instancia global del rate limiter asíncrono
_async_rate_limiter_instance: Optional[AsyncSemaphoreRateLimiter] = None


def get_async_rate_limiter() -> AsyncSemaphoreRateLimiter:
    """
    Retorna la instancia singleton del rate limiter asíncrono.

    Returns:
        Instancia de AsyncSemaphoreRateLimiter
    """
    global _async_rate_limiter_instance
    if _async_rate_limiter_instance is None:
        _async_rate_limiter_instance = AsyncSemaphoreRateLimiter()
    return _async_rate_limiter_instance
