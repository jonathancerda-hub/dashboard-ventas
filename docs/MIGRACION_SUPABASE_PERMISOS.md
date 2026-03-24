# Guía de Migración: SQLite → Supabase para Permisos
## Dashboard Ventas - Sistema de Administración de Usuarios

> 📅 **Fecha**: 24 de marzo de 2026  
> 🎯 **Objetivo**: Migrar sistema de permisos a Supabase para producción en Render.com  
> ⏱️ **Tiempo estimado**: 30-45 minutos

---

## 📋 Índice

1. [Por Qué Migrar](#1-por-qué-migrar)
2. [Pasos de Migración](#2-pasos-de-migración)
3. [Crear Tablas en Supabase](#3-crear-tablas-en-supabase)
4. [Actualizar Código](#4-actualizar-código)
5. [Migrar Datos Existentes (Opcional)](#5-migrar-datos-existentes-opcional)
6. [Verificación y Testing](#6-verificación-y-testing)
7. [Deployment en Render.com](#7-deployment-en-rendercom)
8. [Rollback (Si es Necesario)](#8-rollback-si-es-necesario)

---

## 1. Por Qué Migrar

### ❌ Problemas con SQLite en Render.com

```plaintext
Render.com usa contenedores efímeros:
- Cada deploy crea nuevo contenedor
- SQLite (permissions.db) se pierde en cada deploy
- No hay persistencia de archivos locales
- Reiniciar servicio = pérdida de datos

Resultado: Usuarios pierden permisos constantemente 😢
```

### ✅ Ventajas de Supabase

```plaintext
✅ Base de datos persistente (PostgreSQL en la nube)
✅ No se pierde en deploys/reinicios
✅ Escalable a millones de registros
✅ Backups automáticos
✅ Row Level Security (RLS) integrado
✅ Ya lo tienes configurado para metas
✅ Gratis hasta 500 MB de datos
```

---

## 2. Pasos de Migración

### Checklist General

- [ ] Paso 1: Crear tablas en Supabase (SQL)
- [ ] Paso 2: Renombrar archivos antiguos (backup)
- [ ] Paso 3: Activar nuevos archivos Supabase
- [ ] Paso 4: Verificar conexión
- [ ] Paso 5: Migrar datos existentes (si tienes usuarios en SQLite)
- [ ] Paso 6: Testing local
- [ ] Paso 7: Deploy a Render.com
- [ ] Paso 8: Verificar en producción

---

## 3. Crear Tablas en Supabase

### 3.1 Acceder al Dashboard de Supabase

```bash
1. Ir a: https://supabase.com/dashboard
2. Seleccionar tu proyecto
3. En el menú izquierdo, clic en "SQL Editor"
4. Clic en "New query"
```

### 3.2 Ejecutar Script SQL

```sql
Copiar el contenido completo de:
📁 sql/create_permissions_tables_supabase.sql

Pegar en el SQL Editor y clic en "Run" (▶️)
```

### 3.3 Verificar Creación de Tablas

```sql
-- Ejecutar en SQL Editor para verificar:
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('user_permissions', 'audit_log_permissions');

-- Deberías ver 2 tablas:
-- user_permissions
-- audit_log_permissions
```

### 3.4 Verificar Primer Usuario Admin

```sql
-- Verificar que tu usuario admin se creó:
SELECT * FROM user_permissions WHERE role = 'admin_full';

-- Si no aparece, crearlo manualmente:
INSERT INTO user_permissions (user_email, role, created_by, is_active)
VALUES ('TU_EMAIL@agrovetmarket.com', 'admin_full', 'SYSTEM', TRUE);
```

---

## 4. Actualizar Código

### 4.1 Opción A: Reemplazar Archivos (Recomendado)

```bash
# En PowerShell (terminal de VS Code):
cd C:\Users\jcerda\Desktop\Dashboard-Ventas-Backup

# Hacer backup de archivos originales
Move-Item src\permissions_manager.py src\permissions_manager_OLD_SQLITE.py
Move-Item src\audit_logger.py src\audit_logger_OLD_SQLITE.py -ErrorAction SilentlyContinue

# Renombrar archivos Supabase a nombres finales
Move-Item src\permissions_manager_supabase.py src\permissions_manager.py
Move-Item src\audit_logger_supabase.py src\audit_logger.py
```

### 4.2 Verificar Variables de Entorno

```bash
# Archivo: .env
# Verificar que existen estas variables:

SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_supabase_key_aqui

# Si no existen, agregarlas desde Supabase Dashboard:
# Settings > API > Project URL y Project API keys (service_role key)
```

### 4.3 Actualizar app.py (Instanciar Managers)

```python
# Buscar estas líneas en app.py:
from src.permissions_manager import PermissionsManager

# Instanciar (verificar que existe):
permissions_manager = PermissionsManager()
```

**NO hay cambios necesarios en app.py** si ya está usando `permissions_manager.has_permission()`.

---

## 5. Migrar Datos Existentes (Opcional)

### 5.1 ¿Tienes Usuarios en SQLite?

```bash
# Verificar si existe permissions.db:
Test-Path permissions.db

# Si retorna True, tienes usuarios en SQLite
```

### 5.2 Script de Migración (Si es Necesario)

```python
# Archivo: migrate_sqlite_to_supabase.py
import sqlite3
from src.permissions_manager import PermissionsManager
from src.audit_logger import AuditLogger

def migrate_users():
    """Migra usuarios de SQLite a Supabase"""
    # Leer de SQLite
    conn = sqlite3.connect('permissions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_email, role FROM user_permissions")
    users = cursor.fetchall()
    conn.close()
    
    # Escribir en Supabase
    pm = PermissionsManager()
    audit = AuditLogger()
    
    for email, role in users:
        success = pm.add_user(email, role, created_by='MIGRATION')
        if success:
            print(f"✅ Migrado: {email} ({role})")
            audit.log_user_created('MIGRATION', email, role)
        else:
            print(f"❌ Error: {email}")

if __name__ == '__main__':
    migrate_users()
```

```bash
# Ejecutar migración:
python migrate_sqlite_to_supabase.py
```

---

## 6. Verificación y Testing

### 6.1 Test de Conexión

```python
# test_supabase_permissions.py
from src.permissions_manager import PermissionsManager
from src.audit_logger import AuditLogger

def test_connection():
    """Test básico de conexión"""
    try:
        pm = PermissionsManager()
        audit = AuditLogger()
        
        print("✅ PermissionsManager inicializado")
        print("✅ AuditLogger inicializado")
        
        # Test agregar usuario
        test_email = 'test@agrovetmarket.com'
        success = pm.add_user(test_email, 'user_basic', created_by='TEST')
        
        if success:
            print(f"✅ Usuario de prueba creado: {test_email}")
            
            # Verificar que se puede leer
            role = pm.get_user_role(test_email)
            print(f"✅ Rol verificado: {role}")
            
            # Eliminar usuario de prueba
            pm.delete_user(test_email, soft_delete=False)
            print(f"✅ Usuario de prueba eliminado")
        else:
            print(f"❌ Error creando usuario de prueba")
        
        print("\n🎉 TODOS LOS TESTS PASARON")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == '__main__':
    test_connection()
```

```bash
# Ejecutar test:
python test_supabase_permissions.py
```

### 6.2 Test de Permisos en App

```bash
# Iniciar Flask localmente:
python app.py

# En el navegador:
# 1. Ir a http://localhost:5000
# 2. Login con tu usuario admin
# 3. Verificar acceso a /analytics (si eres admin)
# 4. Verificar que no da errores de DB
```

### 6.3 Revisar Logs

```bash
# Ver logs de la app:
# Buscar líneas como:
# ✅ PermissionsManager inicializado con Supabase
# ✅ AuditLogger inicializado con Supabase

# Si ves errores de conexión:
# ❌ Error al conectar con Supabase: ...
# Verificar SUPABASE_URL y SUPABASE_KEY en .env
```

---

## 7. Deployment en Render.com

### 7.1 Configurar Variables de Entorno en Render

```bash
1. Ir a: https://dashboard.render.com
2. Seleccionar tu servicio (Dashboard-Ventas)
3. Ir a "Environment" tab
4. Agregar/verificar variables:
   - SUPABASE_URL = https://tu-proyecto.supabase.co
   - SUPABASE_KEY = tu_service_role_key_de_supabase
5. Clic en "Save Changes"
```

### 7.2 Hacer Deploy

```bash
# Opción A: Push a GitHub (si tienes auto-deploy)
git add .
git commit -m "feat: Migrar sistema de permisos a Supabase"
git push origin main

# Opción B: Deploy manual desde Render Dashboard
# Clic en "Manual Deploy" > "Deploy latest commit"
```

### 7.3 Verificar Deploy

```bash
# Una vez que deploy termine:
1. Ir a la URL de tu app en Render
2. Hacer login
3. Verificar que dashboard carga correctamente
4. Verificar analytics si eres admin

# Revisar logs en Render:
# Dashboard > Logs
# Buscar:
# ✅ PermissionsManager inicializado con Supabase
```

---

## 8. Rollback (Si es Necesario)

### 8.1 ¿Cuándo Hacer Rollback?

```plaintext
Si ves estos errores después del deploy:
❌ Error al conectar con Supabase
❌ PermissionsManager no inicializado
❌ Usuarios no pueden acceder
```

### 8.2 Pasos de Rollback Rápido

```bash
# En tu máquina local:
cd C:\Users\jcerda\Desktop\Dashboard-Ventas-Backup

# Restaurar archivos originales:
Move-Item src\permissions_manager.py src\permissions_manager_supabase_BROKEN.py -Force
Move-Item src\permissions_manager_OLD_SQLITE.py src\permissions_manager.py -Force

# Commit y push:
git add .
git commit -m "rollback: Revertir a SQLite temporalmente"
git push origin main

# Render auto-deployrá la versión anterior
```

### 8.3 Investigar Problema

```plaintext
Problemas comunes:
1. SUPABASE_KEY incorrecta en Render
   - Verificar que es service_role key, no anon key
   
2. SUPABASE_URL incorrecta
   - Verificar en Supabase Dashboard > Settings > API
   
3. Tablas no creadas
   - Re-ejecutar script SQL en Supabase
   
4. RLS bloqueando acceso
   - Verificar políticas en Supabase > Authentication > Policies
```

---

## 9. Verificación Final en Producción

### 9.1 Checklist Post-Deploy

- [ ] Login funciona correctamente
- [ ] Dashboard carga sin errores
- [ ] Analytics accesible (si eres admin)
- [ ] No hay errores de DB en logs
- [ ] Logs muestran: "✅ PermissionsManager inicializado con Supabase"
- [ ] Crear usuario de prueba desde Python REPL (opcional)

### 9.2 Test desde Python REPL en Render

```bash
# En Render Dashboard > Shell (si está disponible)
# O conectar por SSH si tienes acceso

python
>>> from src.permissions_manager import PermissionsManager
>>> pm = PermissionsManager()
>>> pm.get_all_users()
# Debería mostrar lista de usuarios
>>> exit()
```

---

## 10. Próximos Pasos

### Una Vez Migrado Exitosamente

1. **[Opcional] Eliminar SQLite**:
   ```bash
   # NO hacer hasta estar 100% seguro de que Supabase funciona
   Remove-Item permissions.db
   Remove-Item src\permissions_manager_OLD_SQLITE.py
   ```

2. **Implementar Módulo Admin Web**:
   - Seguir plan en `docs/PLAN_MODULO_ADMIN_PERMISOS.md`
   - Crear interfaz web para gestionar usuarios

3. **Monitoreo**:
   - Revisar logs de Supabase regularmente
   - Ver tabla `audit_log_permissions` para cambios

---

## 11. FAQ

**Q: ¿Cuánto cuesta Supabase con este uso?**  
A: Gratis hasta 500 MB y 2 GB de transferencia/mes. Con usuarios de permisos, usarás <1 MB.

**Q: ¿Qué pasa si Supabase está caído?**  
A: App no funcionará (usuarios no podrán login). Considera implementar fallback a lista hardcodeada para emergencias.

**Q: ¿Puedo usar PostgreSQL local en lugar de Supabase?**  
A: Sí, pero necesitas servicio PostgreSQL accesible desde Render.com (ej: Railway, Heroku Postgres, AWS RDS).

**Q: ¿Los datos de Supabase son seguros?**  
A: Sí, Supabase usa PostgreSQL con RLS. Hemos configurado políticas para que solo backend acceda.

**Q: ¿Cómo hago backup de las tablas?**  
A: Supabase hace backups automáticos. También puedes exportar desde Dashboard > Database > Export.

---

## 12. Comandos Útiles

### Verificar Estado de Tablas en Supabase

```sql
-- Total de usuarios
SELECT COUNT(*) FROM user_permissions;

-- Usuarios activos por rol
SELECT role, COUNT(*) FROM user_permissions WHERE is_active = TRUE GROUP BY role;

-- Últimos 10 cambios
SELECT * FROM audit_log_permissions ORDER BY timestamp DESC LIMIT 10;

-- Logs de último mes
SELECT 
    admin_email, 
    COUNT(*) as total_changes 
FROM audit_log_permissions 
WHERE timestamp >= NOW() - INTERVAL '30 days' 
GROUP BY admin_email;
```

### Agregar Usuario desde SQL (Emergencia)

```sql
-- Si necesitas agregar admin urgentemente:
INSERT INTO user_permissions (user_email, role, created_by, is_active)
VALUES ('nuevo_admin@company.com', 'admin_full', 'EMERGENCY', TRUE);
```

---

## 📞 Soporte

Si tienes problemas:
1. Revisar logs de Render: Dashboard > Logs
2. Revisar logs de Supabase: Dashboard > Logs
3. Verificar variables de entorno en Render
4. Verificar tablas en Supabase SQL Editor

---

**🎉 ¡Listo! Sistema de permisos migrado a Supabase para producción en Render.com**
