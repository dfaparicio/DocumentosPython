"""
API REST para extracción de datos de cédulas usando IA
Punto de entrada principal de la aplicación
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging al inicio de la aplicación
from config import setup_logging
logger = setup_logging()

# Creamos la instancia de la aplicación FastAPI
# Esto es el servidor que recibirá las peticiones
app = FastAPI(
    title="API de Extracción de Datos de Cédulas",
    description="Extrae nombres, apellidos, número de documento y fecha de nacimiento de PDFs de cédulas usando IA",
    version="1.0.0"
)

# Configuramos CORS para permitir peticiones desde otros dominios
# Esto es útil si vas a conectar un frontend desde otra URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# Importamos el router de extracción
# Este archivo contiene el endpoint que procesa los PDFs
from routers.extract_router import router as extract_router

# Endpoint de prueba para verificar que el servidor está funcionando
@app.get("/")
async def root():
    """
    Endpoint raíz que muestra un mensaje de bienvenida.
    Útil para verificar que el servidor está levantado correctamente.
    """
    return {
        "mensaje": "API de Extracción de Datos de Cédulas",
        "estado": "funcionando",
        "version": "1.0.0",
        "endpoints": {
            "documentacion": "/docs",
            "extraccion": "/extract/"
        }
    }

# Incluimos el router en la aplicación
# Esto hace que el endpoint /extract/ esté disponible
app.include_router(extract_router)
