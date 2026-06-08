"""
Conexión a MongoDB usando motor (driver async).
Proporciona funciones de startup/shutdown y acceso a la BD.

MongoDB connection using motor (async driver).
Provides startup/shutdown functions and database access.
"""

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config.settings import get_settings

logger = logging.getLogger(__name__)

# Cliente y base de datos como módulo singleton
# Client and database as module-level singletons
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


def get_database() -> AsyncIOMotorDatabase:
    """
    Retorna la instancia de la base de datos MongoDB.
    Debe llamarse después de connect_db().

    Returns the MongoDB database instance.
    Must be called after connect_db().
    """
    if _database is None:
        raise RuntimeError("La base de datos no está conectada. Llama a connect_db() primero.")
    return _database


async def connect_db() -> None:
    """
    Conecta a MongoDB usando motor.
    Se llama al iniciar la aplicación (startup event).

    Connects to MongoDB using motor.
    Called at application startup (startup event).
    """
    global _client, _database

    settings = get_settings()

    logger.info(f"Conectando a MongoDB en {settings.mongodb_url}...")
    _client = AsyncIOMotorClient(settings.mongodb_url)
    _database = _client[settings.mongodb_db_name]

    # Verificar conexión con un ping
    # Verify connection with a ping
    await _client.admin.command("ping")
    logger.info(f"Conexión a MongoDB establecida — BD: {settings.mongodb_db_name}")


async def close_db() -> None:
    """
    Cierra la conexión a MongoDB.
    Se llama al apagar la aplicación (shutdown event).

    Closes the MongoDB connection.
    Called at application shutdown (shutdown event).
    """
    global _client, _database

    if _client is not None:
        _client.close()
        _client = None
        _database = None
        logger.info("Conexión a MongoDB cerrada.")
