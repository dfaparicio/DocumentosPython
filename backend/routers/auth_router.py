"""
Router de autenticación — Registro, Login y perfil de usuario.
Endpoints para gestionar cuentas y tokens JWT.

Authentication router — Registration, Login and user profile.
Endpoints for managing accounts and JWT tokens.
"""

import logging
import random
from datetime import datetime, timedelta

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status

from core.auth_middleware import get_current_user, require_active_user
from infrastructure.storage.database import get_database
from schemas.user_schema import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
    UserResponse,
    VerifyResetCodeRequest,
)
from services.auth_service import create_access_token, verify_password
from services.email_service import send_reset_code

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)



def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt.

    Hashes a password using bcrypt.
    """
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def _user_doc_to_response(user_doc: dict) -> UserResponse:
    """
    Convierte un documento de MongoDB a UserResponse.

    Converts a MongoDB document to UserResponse.
    """
    return UserResponse(
        id=str(user_doc["_id"]),
        full_name=user_doc["full_name"],
        email=user_doc["email"],
        role=user_doc["role"],
        status=user_doc["status"],
        created_at=user_doc["created_at"],
        activated_at=user_doc.get("activated_at"),
    )


# =====================================================
# POST /auth/register
# =====================================================

@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Registra un nuevo usuario en el sistema. El usuario queda con estado 'pending' hasta que un admin lo active."
)
async def register(user_data: UserRegisterRequest):
    """
    Registra un nuevo usuario en MongoDB.
    - Valida que el email no exista
    - Hashea la contraseña
    - Guarda con estado 'pending'
    """
    db = get_database()
    users_collection = db["users"]

    # Verificar si el email ya existe
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        logger.warning(f"Intento de registro con email duplicado: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El email '{user_data.email}' ya está registrado."
        )

    # Crear documento del usuario
    # Create user document
    now = datetime.utcnow()
    user_doc = {
        "full_name": user_data.full_name,
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "role": "user",
        "status": "pending",
        "created_at": now,
        "activated_at": None,
    }

    # Insertar en MongoDB
    # Insert into MongoDB
    result = await users_collection.insert_one(user_doc)

    logger.info(f"Usuario registrado: {user_data.email} (id={result.inserted_id})")

    # Retornar respuesta
    # Return response
    return UserRegisterResponse(
        id=str(result.inserted_id),
        full_name=user_data.full_name,
        email=user_data.email,
        status="pending",
        created_at=now,
    )


# =====================================================
# POST /auth/login
# =====================================================

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un token JWT. Todos los usuarios registrados pueden hacer login; el acceso a servicios se controla por estado de cuenta."
)
async def login(login_data: LoginRequest):
    """
    Login de usuario:
    - Busca por email
    - Verifica contraseña
    - Genera JWT y retorna datos del usuario
    - El estado de la cuenta se incluye en el token para controlar acceso a servicios
    """
    db = get_database()
    users_collection = db["users"]

    # Buscar usuario por email
    # Find user by email
    user_doc = await users_collection.find_one({"email": login_data.email})
    if not user_doc:
        logger.warning(f"Intento de login con email no registrado: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos."
        )

    # Verificar contraseña
    # Verify password
    if not verify_password(login_data.password, user_doc["hashed_password"]):
        logger.warning(f"Contraseña incorrecta para: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos."
        )

    # Generar token JWT (incluye status para que el middleware lo valide)
    # Generate JWT token (includes status so middleware can validate it)
    token_data = {
        "sub": str(user_doc["_id"]),
        "email": user_doc["email"],
        "role": user_doc["role"],
        "status": user_doc.get("status", "pending"),
    }
    access_token = create_access_token(token_data)

    logger.info(f"Login exitoso: {login_data.email}")

    # Retornar token y datos del usuario
    # Return token and user data
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=_user_doc_to_response(user_doc),
    )


# =====================================================
# GET /auth/me
# =====================================================

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil del usuario autenticado",
    description="Retorna los datos del usuario actual basado en el token JWT proporcionado."
)
async def get_me(user: dict = Depends(get_current_user)):
    """
    Retorna los datos del usuario autenticado.
    Usa el middleware get_current_user para validar el token.

    Returns the data of the authenticated user.
    Uses the get_current_user middleware to validate the token.
    """
    return _user_doc_to_response(user)


# =====================================================
# POST /auth/forgot-password
# =====================================================

@router.post(
    "/forgot-password",
    summary="Solicitar código de recuperación",
    description="Envía un código de 6 dígitos al email registrado para restablecer la contraseña. "
                "Siempre retorna éxito para no revelar si un email existe o no."
)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Genera y envía un código de recuperación por email.
    - Si el email no existe en el sistema, no envía nada pero retorna éxito (seguridad)
    - Invalida códigos anteriores no usados para ese email
    """
    db = get_database()
    users_collection = db["users"]

    # Buscar usuario — si no existe, retornar éxito sin enviar nada
    user_doc = await users_collection.find_one({"email": request.email})
    if not user_doc:
        logger.info(f"Solicitud de recuperación para email no registrado: {request.email}")
        return {"message": "Si el email está registrado, recibirás un código de verificación."}

    # Generar código de 6 dígitos
    code = f"{random.randint(0, 999999):06d}"

    # Invalidar códigos anteriores no usados para este email
    resets_collection = db["password_resets"]
    await resets_collection.update_many(
        {"email": request.email, "used": False},
        {"$set": {"used": True}}
    )

    # Guardar nuevo código
    now = datetime.utcnow()
    from config.settings import get_settings
    settings = get_settings()
    expires_at = now + timedelta(minutes=settings.reset_code_expire_minutes)

    await resets_collection.insert_one({
        "email": request.email,
        "code": code,
        "created_at": now,
        "expires_at": expires_at,
        "used": False,
    })

    # Enviar email
    sent = send_reset_code(request.email, code, settings.reset_code_expire_minutes)
    if not sent:
        logger.error(f"No se pudo enviar el código de recuperación a {request.email}")
        # No revelamos el error al cliente por seguridad
        # pero sí lo logueamos para diagnóstico del admin

    logger.info(f"Código de recuperación generado para {request.email}")

    return {"message": "Si el email está registrado, recibirás un código de verificación."}


# =====================================================
# POST /auth/verify-reset-code
# =====================================================

@router.post(
    "/verify-reset-code",
    summary="Verificar código y restablecer contraseña",
    description="Verifica el código de recuperación y establece la nueva contraseña."
)
async def verify_reset_code(request: VerifyResetCodeRequest):
    """
    Verifica el código de recuperación:
    - Busca código válido (no usado, no expirado) para el email
    - Si es válido: actualiza la contraseña y marca el código como usado
    """
    db = get_database()
    resets_collection = db["password_resets"]
    now = datetime.utcnow()

    # Buscar código válido
    reset_doc = await resets_collection.find_one({
        "email": request.email,
        "code": request.code,
        "used": False,
        "expires_at": {"$gt": now},
    })

    if not reset_doc:
        logger.warning(f"Código de recuperación inválido o expirado para {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido o expirado. Solicita uno nuevo."
        )

    # Actualizar contraseña del usuario
    users_collection = db["users"]
    new_hashed_password = hash_password(request.new_password)

    result = await users_collection.update_one(
        {"email": request.email},
        {"$set": {"hashed_password": new_hashed_password}}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la contraseña."
        )

    # Marcar código como usado
    await resets_collection.update_one(
        {"_id": reset_doc["_id"]},
        {"$set": {"used": True}}
    )

    logger.info(f"Contraseña restablecida exitosamente para {request.email}")

    return {"message": "Contraseña actualizada correctamente."}


# =====================================================
# POST /auth/change-password
# =====================================================

@router.post(
    "/change-password",
    summary="Cambiar contraseña",
    description="Cambia la contraseña del usuario autenticado. Requiere la contraseña actual y la nueva."
)
async def change_password(
    request: ChangePasswordRequest,
    user: dict = Depends(require_active_user),
):
    """
    Cambia la contraseña del usuario autenticado:
    - Verifica que la contraseña actual sea correcta
    - Actualiza con la nueva contraseña hasheada
    """
    # Verificar contraseña actual
    if not verify_password(request.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta."
        )

    # Verificar que la nueva no sea igual a la actual
    if verify_password(request.new_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe ser diferente a la actual."
        )

    # Actualizar contraseña
    db = get_database()
    users_collection = db["users"]
    new_hashed_password = hash_password(request.new_password)

    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": new_hashed_password}}
    )

    logger.info(f"Contraseña cambiada para {user['email']}")

    return {"message": "Contraseña cambiada correctamente."}

