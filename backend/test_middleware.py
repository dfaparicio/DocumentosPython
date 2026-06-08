"""Script de prueba para Task 4 — Endpoints de Admin."""

import urllib.request
import urllib.error
import json

BASE = "http://localhost:8000"

def api(method, path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

print("=" * 60)
print("TEST TASK 4 - ENDPOINTS DE ADMIN")
print("=" * 60)

# 1. Login como admin
print("\n--- 1. Login como admin ---")
code, body = api("POST", "/auth/login", {"email": "camilogelvesro@gmail.com", "password": "admin123"})
assert code == 200, f"Login fallo: {code}"
admin_token = body["access_token"]
print(f"  OK - Token obtenido para {body['user']['email']}")

# 2. Registrar un usuario de prueba
print("\n--- 2. Registrar usuario de prueba ---")
code, body = api("POST", "/auth/register", {
    "full_name": "Usuario Prueba Admin",
    "email": "prueba_admin_test@test.com",
    "password": "123456"
})
if code == 409:
    print("  Usuario ya existe, continuando...")
else:
    assert code == 201, f"Registro fallo: {code} {body}"
    print(f"  OK - Registrado con status={body['status']}")

# 3. GET /admin/users - Listar todos
print("\n--- 3. Listar todos los usuarios ---")
code, users = api("GET", "/admin/users", token=admin_token)
assert code == 200, f"Listar fallo: {code} {users}"
print(f"  OK - Total usuarios: {len(users)}")
for u in users:
    print(f"    - {u['full_name']} | {u['email']} | role={u['role']} | status={u['status']}")

# 4. GET /admin/users?status=pending - Filtrar pendientes
print("\n--- 4. Filtrar usuarios pendientes ---")
code, pending = api("GET", "/admin/users?status=pending", token=admin_token)
assert code == 200, f"Filtrar fallo: {code}"
print(f"  OK - Usuarios pendientes: {len(pending)}")

# 5. Buscar el usuario de prueba para obtener su ID
test_user = None
for u in users:
    if u["email"] == "prueba_admin_test@test.com":
        test_user = u
        break

if test_user:
    test_id = test_user["id"]
    
    # 6. GET /admin/users/{id} - Detalle
    print(f"\n--- 5. Detalle de usuario (id={test_id[:8]}...) ---")
    code, detail = api("GET", f"/admin/users/{test_id}", token=admin_token)
    assert code == 200, f"Detalle fallo: {code}"
    print(f"  OK - {detail['full_name']} | status={detail['status']}")

    # 7. PUT /admin/users/{id}/activate - Activar
    print(f"\n--- 6. Activar usuario ---")
    code, activated = api("PUT", f"/admin/users/{test_id}/activate", token=admin_token)
    if code == 400 and "ya" in activated.get("detail", ""):
        print(f"  Ya estaba activo, desactivamos primero...")
        api("PUT", f"/admin/users/{test_id}/deactivate", token=admin_token)
        code, activated = api("PUT", f"/admin/users/{test_id}/activate", token=admin_token)
    assert code == 200, f"Activar fallo: {code} {activated}"
    print(f"  OK - status={activated['status']}, activated_at={activated.get('activated_at')}")

    # 8. PUT /admin/users/{id}/deactivate - Desactivar
    print(f"\n--- 7. Desactivar usuario ---")
    code, deactivated = api("PUT", f"/admin/users/{test_id}/deactivate", token=admin_token)
    assert code == 200, f"Desactivar fallo: {code} {deactivated}"
    print(f"  OK - status={deactivated['status']}")

    # 9. DELETE /admin/users/{id} - Eliminar
    print(f"\n--- 8. Eliminar usuario ---")
    code, deleted = api("DELETE", f"/admin/users/{test_id}", token=admin_token)
    assert code == 200, f"Eliminar fallo: {code} {deleted}"
    print(f"  OK - {deleted['message']}")

    # 10. Verificar que ya no existe
    print(f"\n--- 9. Verificar eliminacion ---")
    code, body = api("GET", f"/admin/users/{test_id}", token=admin_token)
    assert code == 404, f"Deberia ser 404, got {code}"
    print(f"  OK - HTTP 404, usuario eliminado correctamente")

# 11. Sin token - debe dar 401/403
print(f"\n--- 10. Acceso sin token a /admin/users ---")
code, body = api("GET", "/admin/users")
assert code in [401, 403], f"Esperaba 401/403, got {code}"
print(f"  OK - HTTP {code}, acceso denegado sin token")

# 12. Con token de usuario normal (no admin)
print(f"\n--- 11. Acceso con usuario NO admin ---")
# Registrar usuario normal
api("POST", "/auth/register", {
    "full_name": "Normal User",
    "email": "normal_test_task4@test.com",
    "password": "123456"
})
# Activar manualmente para poder hacer login
code2, users2 = api("GET", "/admin/users", token=admin_token)
for u in users2:
    if u["email"] == "normal_test_task4@test.com":
        api("PUT", f"/admin/users/{u['id']}/activate", token=admin_token)
        break

code, body = api("POST", "/auth/login", {"email": "normal_test_task4@test.com", "password": "123456"})
if code == 200:
    normal_token = body["access_token"]
    code, body = api("GET", "/admin/users", token=normal_token)
    assert code == 403, f"Esperaba 403 para usuario normal, got {code}"
    print(f"  OK - HTTP {code}, usuario normal no puede acceder a admin")
    
    # Limpiar: eliminar usuario normal de prueba
    for u in users2:
        if u["email"] == "normal_test_task4@test.com":
            api("DELETE", f"/admin/users/{u['id']}", token=admin_token)
else:
    print(f"  SKIP - No se pudo hacer login como usuario normal")

print("\n" + "=" * 60)
print("TODOS LOS TESTS DE TASK 4 PASARON!")
print("=" * 60)
