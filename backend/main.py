"""
API REST para extracción de datos de cédulas usando IA.
Punto de entrada principal de la aplicación.

REST API for ID card data extraction using AI.
Main application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging al inicio de la aplicación
# Configure logging at application startup
from config import setup_logging
logger = setup_logging()

# Creamos la instancia de la aplicación FastAPI
# Esto es el servidor que recibirá las peticiones
# Create the FastAPI application instance
# This is the server that will handle incoming requests
app = FastAPI(
    title="API de Extracción de Datos de Cédulas",
    description="Extrae nombres, apellidos, número de documento y fecha de nacimiento de PDFs de cédulas usando IA",
    version="1.0.0"
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
