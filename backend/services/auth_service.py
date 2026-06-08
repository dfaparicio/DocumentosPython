"""
Servicio de autenticación — JWT y validación de contraseñas.
Proporciona funciones para crear, decodificar tokens y verificar passwords.

Authentication service — JWT and password verification.
Provides functions to create, decode tokens and verify passwords.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
from jose import JWTError, jwt

from config.settings import get_settings

logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara una contraseña en texto plano con su hash.
    Retorna True si coinciden.

    Compares a plain-text password with its hash.
    Returns True if they match.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un token JWT con los datos proporcionados.

    Generates a JWT token with the provided data.

    Args:
        data: Payload del token (ej: {"sub": user_id, "role": "user"})
        expires_delta: Tiempo de expiración personalizado (opcional)
    """
    settings = get_settings()

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica y valida un token JWT.
    Retorna el payload si es válido, o None si expiró o es inválido.

    Decodes and validates a JWT token.
    Returns the payload if valid, or None if expired or invalid.
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        logger.debug(f"Token JWT inválido: {e}")
        return None
