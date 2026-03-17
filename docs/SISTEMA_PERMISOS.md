# Sistema de Permisos Centralizado

## Descripción

El dashboard ahora usa un sistema de permisos basado en roles almacenado en SQLite (`permissions.db`), reemplazando las listas hardcodeadas de usuarios administradores.

## Roles Disponibles

| Rol | Permisos |
|-----|----------|
| `admin_full` | ✅ Ver dashboards<br>✅ Ver analytics<br>✅ Editar metas<br>✅ Exportar datos |
| `admin_export` | ✅ Ver dashboards<br>✅ Exportar datos |
| `analytics_viewer` | ✅ Ver dashboards<br>✅ Ver analytics |
| `user_basic` | ✅ Ver dashboards |

## Permisos Definidos

- `view_dashboard`: Acceso a dashboards principales
- `view_analytics`: Acceso a estadísticas de uso del sistema
- `edit_targets`: Modificar metas comerciales
- `export_data`: Exportar datos a Excel

## Usuarios Administradores Actuales

Los siguientes usuarios tienen rol `admin_full` con acceso completo:

1. jonathan.cerda@agrovetmarket.com
2. janet.hueza@agrovetmarket.com
3. juan.portal@agrovetmarket.com
4. amahodoo@agrovetmarket.com
5. miguel.hernandez@agrovetmarket.com
6. juana.lovaton@agrovetmarket.com
7. jimena.delrisco@agrovetmarket.com

## Gestión de Permisos

### Agregar un Usuario

```python
from src.permissions_manager import PermissionsManager

pm = PermissionsManager()
pm.add_user('nuevo.usuario@agrovetmarket.com', role='user_basic')
```

### Modificar Rol de Usuario

```python
pm.update_user_role('usuario@agrovetmarket.com', 'admin_export')
```

### Verificar Permisos

```python
# Verificar si tiene un permiso específico
if pm.has_permission(user_email, 'export_data'):
    # El usuario puede exportar
    pass

# Verificar si es administrador
if pm.is_admin(user_email):
    # El usuario es administrador (admin_full)
    pass
```

### Listar Todos los Usuarios

```python
users = pm.list_all_users()
for user in users:
    print(f"{user['email']} -> {user['role']}")
```

### Remover un Usuario

```python
pm.remove_user('usuario@agrovetmarket.com')
```

## Base de Datos

La base de datos SQLite se crea automáticamente en: `permissions.db`

### Esquema de la Tabla

```sql
CREATE TABLE user_permissions (
    user_email TEXT PRIMARY KEY,
    role TEXT NOT NULL CHECK(role IN ('admin_full', 'admin_export', 'analytics_viewer', 'user_basic')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Ventajas del Sistema

✅ **Centralizado**: Todos los permisos en un solo lugar  
✅ **Flexible**: Agregar/modificar permisos sin tocar código  
✅ **Auditable**: Timestamps de creación y modificación  
✅ **Escalable**: Fácil agregar nuevos roles y permisos  
✅ **Sin Deploys**: Cambios de permisos no requieren redesplegar la app

## Migración Desde Listas Hardcodeadas

La migración se ejecuta automáticamente al iniciar la app por primera vez. Si necesitas re-ejecutarla:

```python
pm = PermissionsManager()

admin_full_list = ['usuario1@...', 'usuario2@...']
admin_export_list = ['usuario3@...']
analytics_list = ['usuario4@...']

pm.migrate_from_lists(admin_full_list, admin_export_list, analytics_list)
```

## Verificación del Sistema

Para verificar que todo funciona correctamente:

```bash
python -c "
from src.permissions_manager import PermissionsManager
pm = PermissionsManager()
print('Usuarios con admin_full:', pm.get_users_with_role('admin_full'))
"
```

## Troubleshooting

### La base de datos no se crea
- Verifica que la app tiene permisos de escritura en el directorio
- Revisa los logs de la aplicación para ver errores

### Un usuario no tiene los permisos esperados
- Verifica que el email esté exactamente igual en la sesión y en la DB
- Usa `list_all_users()` para ver todos los usuarios registrados

### Necesito resetear todos los permisos
```bash
rm permissions.db
python app.py  # Esto recreará la DB con los valores iniciales
```
