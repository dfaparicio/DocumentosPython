"""
Schemas de validación para las requests/responses de usuario.
Usa Pydantic para validar los datos que entran y salen de la API.

Validation schemas for user requests/responses.
Uses Pydantic to validate data entering and leaving the API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """
    Datos requeridos para registrar un nuevo usuario.
    Data required to register a new user.
    """
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre completo",
        examples=["Juan Pérez"]
    )
    email: EmailStr = Field(
        ...,
        description="Email del usuario (debe ser único)",
        examples=["juan@test.com"]
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="Contraseña (mínimo 6 caracteres)",
        examples=["123456"]
    )


class UserRegisterResponse(BaseModel):
    """
    Respuesta exitosa al registrar un usuario.
    Successful response when registering a user.
    """
    id: str = Field(..., description="ID del usuario en MongoDB")
    full_name: str = Field(..., description="Nombre completo")
    email: str = Field(..., description="Email del usuario")
    status: str = Field(..., description="Estado de la cuenta", examples=["pending"])
    created_at: datetime = Field(..., description="Fecha de registro")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserResponse(BaseModel):
    """
    Datos completos del usuario (sin la contraseña).
    Full user data (without the password).
    """
    id: str = Field(..., description="ID del usuario en MongoDB")
    full_name: str = Field(..., description="Nombre completo")
    email: str = Field(..., description="Email del usuario")
    role: str = Field(..., description="Rol del usuario")
    status: str = Field(..., description="Estado de la cuenta")
    created_at: datetime = Field(..., description="Fecha de registro")
    activated_at: Optional[datetime] = Field(default=None, description="Fecha de activación")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LoginRequest(BaseModel):
    """
    Datos requeridos para iniciar sesión.
    Data required to log in.
    """
    email: EmailStr = Field(
        ...,
        description="Email del usuario",
        examples=["juan@test.com"]
    )
    password: str = Field(
        ...,
        description="Contraseña del usuario",
        examples=["123456"]
    )


class LoginResponse(BaseModel):
    """
    Respuesta exitosa al hacer login.
    Successful response when logging in.
    """
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user: UserResponse = Field(..., description="Datos del usuario autenticado")


class ForgotPasswordRequest(BaseModel):
    """
    Solicitud para recuperar contraseña olvidada.
    Se envía un código de verificación al email registrado.

    Request to recover forgotten password.
    A verification code is sent to the registered email.
    """
    email: EmailStr = Field(
        ...,
        description="Email de la cuenta a recuperar",
        examples=["juan@test.com"]
    )


class VerifyResetCodeRequest(BaseModel):
    """
    Verificación del código de recuperación y nueva contraseña.

    Verification of the reset code and new password.
    """
    email: EmailStr = Field(
        ...,
        description="Email de la cuenta",
        examples=["juan@test.com"]
    )
    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="Código de 6 dígitos recibido por email",
        examples=["123456"]
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="Nueva contraseña (mínimo 6 caracteres)",
        examples=["nuevaClave123"]
    )


class ChangePasswordRequest(BaseModel):
    """
    Solicitud para cambiar contraseña (usuario autenticado).

    Request to change password (authenticated user).
    """
    current_password: str = Field(
        ...,
        description="Contraseña actual",
        examples=["123456"]
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="Nueva contraseña (mínimo 6 caracteres)",
        examples=["nuevaClave123"]
    )
