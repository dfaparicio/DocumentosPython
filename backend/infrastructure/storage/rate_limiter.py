"""
Rate limiter para limitar llamadas a APIs externas.
Previene exceder cuotas de servicio.

Rate limiter to limit calls to external APIs.
Prevents exceeding service quotas.
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
    Request rate limiter.

    Permite un número máximo de requests por ventana de tiempo.
    Usa un algoritmo de ventana deslizante (sliding window).
    Allows a maximum number of requests per time window.
    Uses a sliding window algorithm.

    Attributes:
        max_requests: Máximo de requests permitidos / Maximum allowed requests
        window_seconds: Ventana de tiempo en segundos / Time window in seconds
        requests: Lista de timestamps de requests / List of request timestamps
    """

    def __init__(
        self,
        max_requests: Optional[int] = None,
        window_seconds: int = 60
    ):
        """
        Inicializa el rate limiter.
        Initializes the rate limiter.

        Args:
            max_requests: Máximo de requests permitidos / Maximum allowed requests
            window_seconds: Ventana de tiempo en segundos / Time window in seconds
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
        Attempts to acquire a permit to make a request.

        Returns:
            True si se puede hacer el request / True if the request can be made

        Raises:
            AIServiceRateLimitError: Si excede el rate limit / If rate limit is exceeded
        """
        now = datetime.now()

        # Eliminar requests antiguos fuera de la ventana
        # Remove old requests outside the window
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.requests = [
            req_time for req_time in self.requests
            if req_time > cutoff
        ]

        # Verificar si podemos hacer el request
        # Check if we can make the request
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
        # Register the request
        self.requests.append(now)
        logger.debug(f"Request permitido. Requests actuales: {len(self.requests)}/{self.max_requests}")
        return True

    def get_stats(self) -> dict:
        """
        Retorna estadísticas actuales.
        Returns current statistics.

        Returns:
            Diccionario con estadísticas / Dictionary with statistics
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
        """Resetea el contador de requests.
        Resets the request counter."""
        self.requests.clear()
        logger.info("Rate limiter reseteado")


# Instancia global del rate limiter
# Global rate limiter instance
_rate_limiter_instance: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Retorna la instancia singleton del rate limiter.
    Returns the singleton instance of the rate limiter.

    Returns:
        Instancia de RateLimiter / RateLimiter instance
    """
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter()
    return _rate_limiter_instance


class AsyncSemaphoreRateLimiter:
    """
    Rate limiter asíncrono usando semáforos.
    Async rate limiter using semaphores.

    Permite controlar el número de operaciones concurrentes.
    Allows controlling the number of concurrent operations.
    """

    def __init__(self, max_concurrent: int = 5):
        """
        Inicializa el rate limiter asíncrono.
        Initializes the async rate limiter.

        Args:
            max_concurrent: Máximo de operaciones concurrentes / Maximum concurrent operations
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
        Acquires the semaphore asynchronously.

        Returns:
            Context manager para el semáforo / Context manager for the semaphore
        """
        return self.semaphore

    async def __aenter__(self):
        """Entra al contexto del semáforo.
        Enters the semaphore context."""
        await self.semaphore.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Sale del contexto del semáforo.
        Exits the semaphore context."""
        self.semaphore.release()

    def get_available_slots(self) -> int:
        """
        Retorna el número de slots disponibles.
        Returns the number of available slots.

        Returns:
            Número de operaciones que pueden iniciarse inmediatamente / Number of operations that can start immediately
        """
        return self.max_concurrent - self.semaphore._value


# Instancia global del rate limiter asíncrono
# Global async rate limiter instance
_async_rate_limiter_instance: Optional[AsyncSemaphoreRateLimiter] = None


def get_async_rate_limiter() -> AsyncSemaphoreRateLimiter:
    """
    Retorna la instancia singleton del rate limiter asíncrono.
    Returns the singleton instance of the async rate limiter.

    Returns:
        Instancia de AsyncSemaphoreRateLimiter / AsyncSemaphoreRateLimiter instance
    """
    global _async_rate_limiter_instance
    if _async_rate_limiter_instance is None:
        _async_rate_limiter_instance = AsyncSemaphoreRateLimiter()
    return _async_rate_limiter_instance
