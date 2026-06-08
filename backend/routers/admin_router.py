"""
Router de administración — CRUD de usuarios (solo para admins).
Permite listar, activar, desactivar y eliminar usuarios.

Administration router — User CRUD (admin only).
Allows listing, activating, deactivating and deleting users.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.auth_middleware import require_admin
from infrastructure.storage.database import get_database
from schemas.user_schema import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["Administración"],
)


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
# GET /admin/users — Listar usuarios
# =====================================================

@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="Listar todos los usuarios",
    description="Retorna la lista de usuarios registrados. Se puede filtrar por status (pending, active, inactive).",
)
async def list_users(
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        description="Filtrar por estado: pending, active, inactive",
        examples=["pending"],
    ),
    admin: dict = Depends(require_admin),
):
    """
    Lista todos los usuarios del sistema.
    Solo accesible por administradores.

    Lists all users in the system.
    Only accessible by administrators.
    """
    db = get_database()
    users_collection = db["users"]

    # Construir filtro de búsqueda
    # Build search filter
    query = {}
    if status_filter:
        valid_statuses = ["pending", "active", "inactive"]
        if status_filter not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Status invalido: '{status_filter}'. Valores permitidos: {valid_statuses}",
            )
        query["status"] = status_filter

    # Buscar usuarios, ordenados por fecha de creación (más recientes primero)
    # Find users, sorted by creation date (newest first)
    cursor = users_collection.find(query).sort("created_at", -1)
    users = await cursor.to_list(length=500)

    logger.info(
        f"Admin {admin['email']} listó usuarios (filtro={status_filter}, total={len(users)})"
    )

    return [_user_doc_to_response(u) for u in users]


# =====================================================
# GET /admin/users/{user_id} — Detalle de usuario
# =====================================================

@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Obtener detalle de un usuario",
    description="Retorna los datos completos de un usuario específico por su ID.",
)
async def get_user(
    user_id: str,
    admin: dict = Depends(require_admin),
):
    """
    Obtiene los datos de un usuario por su ID.
    Solo accesible por administradores.

    Gets user data by ID.
    Only accessible by administrators.
    """
    db = get_database()

    try:
        user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID de usuario invalido.")

    if not user_doc:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return _user_doc_to_response(user_doc)


# =====================================================
# PUT /admin/users/{user_id}/activate — Activar usuario
# =====================================================

@router.put(
    "/users/{user_id}/activate",
    response_model=UserResponse,
    summary="Activar un usuario",
    description="Cambia el estado de un usuario a 'active'. El usuario podrá usar el servicio de extracción.",
)
async def activate_user(
    user_id: str,
    admin: dict = Depends(require_admin),
):
    """
    Activa un usuario (cambia status a 'active').
    - Registra la fecha de activación
    - El usuario podrá hacer login y usar el servicio

    Activates a user (changes status to 'active').
    - Records the activation date
    - The user will be able to login and use the service
    """
    db = get_database()
    users_collection = db["users"]

    # Buscar el usuario
    # Find the user
    try:
        user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID de usuario invalido.")

    if not user_doc:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # No permitir activar al propio admin (ya está activo)
    # Don't allow activating the admin themselves (already active)
    if user_doc.get("status") == "active":
        raise HTTPException(
            status_code=400,
            detail=f"El usuario '{user_doc['email']}' ya está activo.",
        )

    # Actualizar status y fecha de activación
    # Update status and activation date
    now = datetime.now(timezone.utc)
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "status": "active",
                "activated_at": now,
            }
        },
    )

    logger.info(
        f"Admin {admin['email']} activó al usuario {user_doc['email']} (id={user_id})"
    )

    # Retornar usuario actualizado
    # Return updated user
    user_doc["status"] = "active"
    user_doc["activated_at"] = now
    return _user_doc_to_response(user_doc)


# =====================================================
# PUT /admin/users/{user_id}/deactivate — Desactivar usuario
# =====================================================

@router.put(
    "/users/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Desactivar un usuario",
    description="Cambia el estado de un usuario a 'inactive'. El usuario no podrá usar el servicio.",
)
async def deactivate_user(
    user_id: str,
    admin: dict = Depends(require_admin),
):
    """
    Desactiva un usuario (cambia status a 'inactive').
    - El usuario ya no podrá acceder al servicio
    - No se elimina, puede reactivarse después

    Deactivates a user (changes status to 'inactive').
    - The user will no longer be able to access the service
    - Not deleted, can be reactivated later
    """
    db = get_database()
    users_collection = db["users"]

    try:
        user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID de usuario invalido.")

    if not user_doc:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # No permitir que un admin se desactive a sí mismo
    # Don't allow an admin to deactivate themselves
    if str(user_doc["_id"]) == str(admin["_id"]):
        raise HTTPException(
            status_code=400,
            detail="No puedes desactivar tu propia cuenta de administrador.",
        )

    if user_doc.get("status") == "inactive":
        raise HTTPException(
            status_code=400,
            detail=f"El usuario '{user_doc['email']}' ya está inactivo.",
        )

    # Actualizar status
    # Update status
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"status": "inactive"}},
    )

    logger.info(
        f"Admin {admin['email']} desactivó al usuario {user_doc['email']} (id={user_id})"
    )

    user_doc["status"] = "inactive"
    return _user_doc_to_response(user_doc)


# =====================================================
# DELETE /admin/users/{user_id} — Eliminar usuario
# =====================================================

@router.delete(
    "/users/{user_id}",
    summary="Eliminar un usuario",
    description="Elimina permanentemente un usuario del sistema. Esta acción no se puede deshacer.",
)
async def delete_user(
    user_id: str,
    admin: dict = Depends(require_admin),
):
    """
    Elimina un usuario permanentemente de MongoDB.
    - No se puede eliminar a uno mismo
    - No se puede deshacer

    Permanently deletes a user from MongoDB.
    - Cannot delete yourself
    - Cannot be undone
    """
    db = get_database()
    users_collection = db["users"]

    try:
        user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID de usuario invalido.")

    if not user_doc:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # No permitir que un admin se elimine a sí mismo
    # Don't allow an admin to delete themselves
    if str(user_doc["_id"]) == str(admin["_id"]):
        raise HTTPException(
            status_code=400,
            detail="No puedes eliminar tu propia cuenta de administrador.",
        )

    # Eliminar usuario
    # Delete user
    await users_collection.delete_one({"_id": ObjectId(user_id)})

    logger.info(
        f"Admin {admin['email']} eliminó al usuario {user_doc['email']} (id={user_id})"
    )

    return {
        "message": f"Usuario '{user_doc['email']}' eliminado exitosamente.",
        "deleted_id": user_id,
    }
