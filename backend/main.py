"""
API REST para extracción de datos de cédulas usando IA.
Punto de entrada principal de la aplicación.

REST API for ID card data extraction using AI.
Main application entry point.
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging al inicio de la aplicación
# Configure logging at application startup
from config import setup_logging
logger = setup_logging()


async def _ensure_default_admin(db):
    """
    Crea el usuario admin por defecto si no existe.
    Creates the default admin user if it doesn't exist.
    """
    from config.settings import get_settings
    settings = get_settings()

    users_collection = db["users"]
    existing_admin = await users_collection.find_one({"email": settings.admin_email})

    if not existing_admin:
        import bcrypt
        hashed_pw = bcrypt.hashpw(
            settings.admin_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        admin_doc = {
            "full_name": "Administrador",
            "email": settings.admin_email,
            "hashed_password": hashed_pw,
            "role": "admin",
            "status": "active",
            "created_at": datetime.utcnow(),
            "activated_at": datetime.utcnow(),
        }
        await users_collection.insert_one(admin_doc)
        logger.info(f"Usuario admin por defecto creado: {settings.admin_email}")
    else:
        logger.info("Usuario admin ya existe, no se crea duplicado.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación:
    - Startup: conecta a MongoDB y crea admin por defecto
    - Shutdown: cierra la conexión a MongoDB

    Handles the application lifecycle:
    - Startup: connects to MongoDB and creates default admin
    - Shutdown: closes MongoDB connection
    """
    # === STARTUP ===
    from infrastructure.storage.database import connect_db, close_db, get_database

    await connect_db()

    # Crear índice único en email para evitar duplicados
    # Create unique index on email to prevent duplicates
    db = get_database()
    await db["users"].create_index("email", unique=True)
    logger.info("Índice único creado en colección 'users' (campo: email)")

    # Crear admin por defecto si no existe
    # Create default admin if it doesn't exist
    await _ensure_default_admin(db)

    yield  # La aplicación está corriendo / The application is running

    # === SHUTDOWN ===
    await close_db()


# Creamos la instancia de la aplicación FastAPI
# Esto es el servidor que recibirá las peticiones
# Create the FastAPI application instance
# This is the server that will handle incoming requests
app = FastAPI(
    title="API de Extracción de Datos de Cédulas",
    description="Extrae nombres, apellidos, número de documento y fecha de nacimiento de PDFs de cédulas usando IA",
    version="1.0.0",
    lifespan=lifespan,
)

import os

ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:9000,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:9000"
).split(",")

# Configuramos CORS para permitir peticiones desde otros dominios
# Esto es útil si vas a conectar un frontend desde otra URL
# Configure CORS to allow requests from other domains
# Useful when connecting a frontend from a different URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Orígenes restringidos por seguridad / Restricted origins for security
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.) / Allow all methods
    allow_headers=["*"],  # Permite todos los headers / Allow all headers
)

# Importamos el router de extracción
# Este archivo contiene el endpoint que procesa los PDFs
# Import the extraction router
# This file contains the endpoint that processes PDFs
from routers.extract_router import router as extract_router

# Incluimos el router en la aplicación
# Esto hace que el endpoint /extract/ esté disponible
# Include the router in the application
# This makes the /extract/ endpoint available
app.include_router(extract_router)

# Router de comparación y reconciliación
# Comparison and reconciliation router
from routers.compare_router import router as compare_router
app.include_router(compare_router)

# Router de autenticación (registro)
# Authentication router (registration)
from routers.auth_router import router as auth_router
app.include_router(auth_router)

# Router de administración (gestión de usuarios)
# Administration router (user management)
from routers.admin_router import router as admin_router
app.include_router(admin_router)
