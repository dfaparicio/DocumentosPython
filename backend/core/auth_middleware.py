"""
Middleware de autenticación — Dependencies de FastAPI reutilizables.
Provee 3 niveles de protección para endpoints:
  1. get_current_user    → Cualquier usuario autenticado (token válido)
  2. require_active_user → Solo usuarios con status='active'
  3. require_admin       → Solo usuarios con role='admin'

Authentication middleware — Reusable FastAPI dependencies.
Provides 3 protection levels for endpoints:
  1. get_current_user    → Any authenticated user (valid token)
  2. require_active_user → Only users with status='active'
  3. require_admin       → Only users with role='admin'

Uso / Usage:
    from core.auth_middleware import get_current_user, require_active_user, require_admin

    @router.get("/ruta-protegida")
    async def mi_endpoint(user: dict = Depends(require_active_user)):
        # 'user' contiene el documento completo del usuario desde MongoDB
        return {"message": f"Hola {user['full_name']}"}
"""

import logging
from typing import Dict

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from infrastructure.storage.database import get_database
from services.auth_service import decode_token

logger = logging.getLogger(__name__)

# Esquema de seguridad Bearer — agrega el candadito 🔒 en Swagger
# Bearer security scheme — adds the lock icon 🔒 in Swagger
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    """
    NIVEL 1: Obtiene el usuario autenticado desde el token JWT.
    Valida que el token sea válido y que el usuario exista en MongoDB.
    No verifica el estado (active/pending/inactive).

    LEVEL 1: Gets the authenticated user from the JWT token.
    Validates that the token is valid and the user exists in MongoDB.
    Does NOT check the status (active/pending/inactive).

    Args:
        credentials: Token JWT extraído del header Authorization

    Returns:
        Documento completo del usuario desde MongoDB (dict)

    Raises:
        HTTPException 401: Token inválido, expirado o usuario no encontrado
    """
    # Decodificar y validar el token JWT
    # Decode and validate the JWT token
    payload = decode_token(credentials.credentials)
    if payload is None:
        logger.warning("Intento de acceso con token inválido o expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extraer el ID del usuario del payload
    # Extract the user ID from the payload
    user_id = payload.get("sub")
    if not user_id:
        logger.warning("Token JWT sin campo 'sub'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar al usuario en MongoDB (datos frescos, no del token)
    # Find the user in MongoDB (fresh data, not from the token)
    db = get_database()
    try:
        user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    except Exception:
        logger.warning(f"ID de usuario inválido en token: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user_doc:
        logger.warning(f"Usuario no encontrado en BD para id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado. La cuenta puede haber sido eliminada.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_doc


async def require_active_user(
    user: Dict = Depends(get_current_user),
) -> Dict:
    """
    NIVEL 2: Requiere que el usuario esté activo (status='active').
    Primero valida el token (via get_current_user), luego verifica el estado.

    LEVEL 2: Requires the user to be active (status='active').
    First validates the token (via get_current_user), then checks the status.

    Args:
        user: Documento del usuario (inyectado por get_current_user)

    Returns:
        Documento completo del usuario si está activo

    Raises:
        HTTPException 403: Si el usuario no está activo
    """
    user_status = user.get("status", "pending")

    if user_status == "pending":
        logger.info(f"Acceso denegado — cuenta pendiente: {user['email']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está pendiente de activación. "
                   "Un administrador debe aprobar tu registro.",
        )

    if user_status == "inactive":
        logger.info(f"Acceso denegado — cuenta desactivada: {user['email']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta ha sido desactivada. "
                   "Contacta al administrador para más información.",
        )

    if user_status != "active":
        logger.warning(f"Estado de cuenta desconocido '{user_status}' para: {user['email']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Estado de cuenta no reconocido: {user_status}.",
        )

    return user


async def require_admin(
    user: Dict = Depends(get_current_user),
) -> Dict:
    """
    NIVEL 3: Requiere que el usuario sea administrador (role='admin').
    Primero valida el token (via get_current_user), luego verifica el rol.
    No requiere status='active' por separado porque el admin siempre está activo.

    LEVEL 3: Requires the user to be an administrator (role='admin').
    First validates the token (via get_current_user), then checks the role.
    Does not require status='active' separately because admin is always active.

    Args:
        user: Documento del usuario (inyectado por get_current_user)

    Returns:
        Documento completo del usuario si es admin

    Raises:
        HTTPException 403: Si el usuario no es admin
    """
    if user.get("role") != "admin":
        logger.warning(
            f"Acceso admin denegado para: {user['email']} (role={user.get('role')})"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de administrador.",
        )

    return user
