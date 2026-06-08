"""
Modelo de usuario para MongoDB.
Define la estructura del documento en la colección `users`.

User model for MongoDB.
Defines the document structure in the `users` collection.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserModel(BaseModel):
    """
    Representa un documento de usuario en MongoDB.

    Represents a user document in MongoDB.
    """
    full_name: str = Field(..., min_length=2, max_length=100, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Email único del usuario")
    hashed_password: str = Field(..., description="Contraseña hasheada con bcrypt")
    role: str = Field(default="user", description="Rol del usuario: 'user' o 'admin'")
    status: str = Field(default="pending", description="Estado: 'pending', 'active' o 'inactive'")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha de registro")
    activated_at: Optional[datetime] = Field(default=None, description="Fecha de activación")

    class Config:
        # Permite que Pydantic trabaje con ObjectId de MongoDB
        # Allows Pydantic to work with MongoDB ObjectIds
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserInDB(UserModel):
    """
    Modelo de usuario tal como está en la BD, incluye el _id de MongoDB.

    User model as stored in the DB, includes MongoDB _id.
    """
    id: str = Field(alias="_id", description="ID del documento MongoDB")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
