# Sistema de Usuarios con MongoDB — Plan por Tasks

## Contexto

Agregar autenticación y gestión de usuarios al sistema de extracción de cédulas.  
**Stack**: MongoDB (con `motor` async) + JWT + FastAPI.  
**Estrategia**: Backend primero, probando cada task con Swagger (`/docs`). Frontend después.

---

## Task 1 — Conexión MongoDB + Modelo User + Registro

> **Objetivo**: Un usuario puede registrarse vía `POST /auth/register` y queda guardado en MongoDB con estado `pending`.

### Archivos

#### [MODIFY] [requirements.txt](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/requirements.txt)
Agregar dependencias:
```
motor==3.7.0            # Driver async de MongoDB
passlib[bcrypt]==1.7.4   # Hash de contraseñas
python-jose[cryptography]==3.5.0  # JWT tokens (se usa en Task 2)
```

#### [MODIFY] [.env](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/.env)
Agregar variables de MongoDB y JWT:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=cedulas_extractor
JWT_SECRET_KEY=tu-clave-secreta-cambiar-en-produccion
ADMIN_EMAIL=admin@sistema.com
ADMIN_PASSWORD=admin123
```

#### [MODIFY] [settings.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/config/settings.py)
Agregar campos: `mongodb_url`, `mongodb_db_name`, `jwt_secret_key`, `jwt_algorithm`, `jwt_expire_minutes`, `admin_email`, `admin_password`

#### [NEW] [database.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/infrastructure/storage/database.py)
- Conexión a MongoDB con `motor.motor_asyncio.AsyncIOMotorClient`
- Función `get_database()` para obtener la instancia de la BD
- Funciones `connect_db()` y `close_db()` para startup/shutdown

#### [NEW] [user_model.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/domain/entities/user_model.py)
Documento MongoDB `users` con campos:
```python
{
    "full_name": str,
    "email": str,          # único
    "hashed_password": str,
    "role": "user" | "admin",
    "status": "pending" | "active" | "inactive",
    "created_at": datetime,
    "activated_at": datetime | None
}
```

#### [NEW] [user_schema.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/schemas/user_schema.py) (sobreescribir el existente de students)
- `UserRegisterRequest`: name, email, password (con validaciones)
- `UserRegisterResponse`: id, name, email, status, created_at
- `UserResponse`: datos completos del usuario sin password

#### [NEW] [auth_router.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/routers/auth_router.py)
- `POST /auth/register` — Valida datos, hashea password, guarda en MongoDB, retorna confirmación

#### [MODIFY] [main.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/main.py)
- Importar y registrar `auth_router`
- Agregar eventos `startup`/`shutdown` para conectar/desconectar MongoDB
- Crear usuario admin por defecto si no existe al iniciar

### Probar en Swagger
1. Abrir `http://localhost:8000/docs`
2. `POST /auth/register` con body `{"full_name": "Juan", "email": "juan@test.com", "password": "123456"}`
3. Verificar respuesta con status `pending`
4. Intentar registrar mismo email → error 409 (duplicado)

---

## Task 2 — Login con JWT

> **Objetivo**: Un usuario activo puede hacer login y recibir un token JWT. Un usuario pendiente recibe error claro.

### Archivos

#### [NEW] [auth_service.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/services/auth_service.py)
- `verify_password(plain, hashed)` — Compara contraseñas
- `create_access_token(data, expires)` — Genera JWT
- `decode_token(token)` — Decodifica y valida JWT

#### [MODIFY] [auth_router.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/routers/auth_router.py)
Agregar endpoints:
- `POST /auth/login` — Valida credenciales, verifica status, retorna JWT
  - Si status=`pending` → error 403 "Cuenta pendiente de activación"
  - Si status=`inactive` → error 403 "Cuenta desactivada"
  - Si status=`active` → retorna `{ access_token, token_type, user }`
- `GET /auth/me` — Retorna datos del usuario autenticado (requiere token)

### Probar en Swagger
1. Intentar login con usuario pendiente → error 403
2. Manualmente cambiar status a `active` en MongoDB Compass
3. Login → recibir token JWT
4. Usar el candadito 🔒 de Swagger para autorizar
5. `GET /auth/me` → ver datos del usuario

---

## Task 3 — Middleware de Autenticación

> **Objetivo**: Dependencies reutilizables para proteger cualquier endpoint.

### Archivos

#### [NEW] [auth_middleware.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/core/auth_middleware.py)
Tres niveles de protección como dependencies de FastAPI:
```python
async def get_current_user(token) -> dict       # Cualquier usuario autenticado
async def require_active_user(user) -> dict     # Solo usuarios con status=active
async def require_admin(user) -> dict           # Solo usuarios con role=admin
```

### Probar en Swagger
1. Llamar endpoint protegido sin token → 401
2. Llamar con token de usuario pendiente → 403
3. Llamar con token de usuario activo → ✅

---

## Task 4 — Panel de Admin (Endpoints)

> **Objetivo**: El admin puede listar, activar, desactivar y eliminar usuarios.

### Archivos

#### [NEW] [admin_router.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/routers/admin_router.py)
Todos protegidos con `require_admin`:
- `GET /admin/users` — Lista usuarios con filtro opcional por status
- `GET /admin/users/{id}` — Detalle de un usuario
- `PUT /admin/users/{id}/activate` — Cambia status a `active`
- `PUT /admin/users/{id}/deactivate` — Cambia status a `inactive`
- `DELETE /admin/users/{id}` — Elimina usuario

#### [MODIFY] [main.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/main.py)
- Registrar `admin_router`

### Probar en Swagger
1. Login como admin → obtener token
2. `GET /admin/users` → ver lista de usuarios
3. `PUT /admin/users/{id}/activate` → activar un usuario pendiente
4. Ese usuario ahora puede hacer login
5. Intentar endpoints de admin con token de usuario normal → 403

---

## Task 5 — Proteger Endpoints Existentes

> **Objetivo**: Los endpoints de extracción y comparación solo funcionan para usuarios activos.

### Archivos

#### [MODIFY] [extract_router.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/routers/extract_router.py)
- Agregar `Depends(require_active_user)` a `POST /extract/`
- Agregar a `GET /extract/progress` y WebSocket

#### [MODIFY] [compare_router.py](file:///c:/Users/USUARIO/sena/DocumentosPython/backend/routers/compare_router.py)
- Agregar `Depends(require_active_user)` a todos los endpoints

### Probar en Swagger
1. Intentar `POST /extract/` sin token → 401
2. Con token de usuario activo → funciona normal
3. Desactivar usuario desde admin → ya no puede extraer

---

## Resumen de Tasks

| Task | Qué se logra | Dependencias |
|------|-------------|--------------|
| **1** | Registro de usuarios en MongoDB | Ninguna |
| **2** | Login + JWT | Task 1 |
| **3** | Middleware de protección | Task 2 |
| **4** | Panel admin (CRUD usuarios) | Task 3 |
| **5** | Proteger endpoints existentes | Task 3 |

> [!IMPORTANT]
> **Requisito previo**: Tener MongoDB instalado y corriendo localmente. Si no lo tienes, necesitarás instalarlo o usar MongoDB Atlas (cloud gratis).

---

## Verificación por Task

Cada task se verifica individualmente en Swagger (`/docs`) antes de pasar a la siguiente. No se toca el frontend hasta completar todas las tasks del backend.
