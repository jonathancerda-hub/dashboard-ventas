# 🚀 Prompt para Implementar Módulo de Administración de Permisos

> **Copia este prompt y úsalo en tu proyecto Flask para implementar el módulo completo**

---

## 📋 Prompt para Copiar

```
Necesito implementar un módulo completo de administración de permisos de usuarios en mi proyecto Flask. 

Tengo como referencia la implementación exitosa del proyecto Dashboard-Ventas-Backup que usa Supabase. Necesito que adaptes este sistema a mi proyecto.

## Contexto de mi Proyecto

**Tipo de proyecto**: [Especifica: E-commerce, CRM, Blog, Dashboard Analytics, etc.]

**Base de datos a usar**: [Elige una]
- [ ] Supabase (PostgreSQL en la nube - recomendado para producción)
- [ ] SQLite (desarrollo/prototipos)
- [ ] PostgreSQL (auto-hospedado)
- [ ] MySQL/MariaDB

**Roles necesarios**: [Personaliza según tu proyecto]
Ejemplo:
- admin_full: Acceso total (gestión de usuarios, datos, reportes)
- manager: Acceso a reportes y gestión de su equipo
- user: Solo visualización

**Permisos necesarios**: [Lista los permisos de tu aplicación]
Ejemplo:
- view_dashboard
- view_reports
- edit_data
- export_data
- manage_users

## Requerimientos Funcionales

Implementa un módulo de administración de usuarios con las siguientes características:

### Backend
1. **Gestor de Permisos** (src/permissions_manager.py):
   - Conectar con [tu base de datos elegida]
   - Métodos CRUD completos: add_user, update_user_role, delete_user (soft delete), reactivate_user
   - Verificación de permisos: has_permission(email, permission)
   - Búsqueda y filtrado de usuarios
   - Validación de emails corporativos (dominio: [tu-dominio.com])

2. **Sistema de Auditoría** (src/audit_logger.py):
   - Registrar todas las operaciones: CREATE, UPDATE, DELETE, DEACTIVATE, REACTIVATE
   - Guardar metadata: IP, user agent, timestamp, admin que realizó la acción
   - Métodos para obtener logs recientes y filtrados

3. **Rutas Flask** (app.py):
   - GET  /admin/users - Lista de usuarios con DataTables
   - GET/POST /admin/users/add - Crear usuario
   - GET/POST /admin/users/edit/<email> - Editar rol de usuario
   - POST /admin/users/delete/<email> - Desactivar usuario (soft delete)
   - POST /admin/users/reactivate/<email> - Reactivar usuario
   - GET /admin/audit-log - Historial de cambios

### Frontend
1. **Templates** (templates/admin/):
   - users_list.html - Tabla de usuarios con búsqueda, filtros, badges de color por rol
   - user_add.html - Formulario de creación con preview de permisos
   - user_edit.html - Formulario de edición con validaciones
   - audit_log.html - Historial con filtros por fecha y acción

2. **JavaScript**:
   - Validación de emails corporativos
   - Preview dinámico de permisos según rol seleccionado
   - Confirmaciones con SweetAlert2 antes de eliminar
   - DataTables para búsqueda y paginación

### Seguridad
- ✅ Solo usuarios con rol admin_full pueden acceder al módulo
- ✅ CSRF protection en todos los formularios
- ✅ Prevenir auto-modificación (admin no puede cambiar su propio rol)
- ✅ Prevenir auto-eliminación (admin no puede eliminarse a sí mismo)
- ✅ Rate limiting (10 operaciones por hora)
- ✅ Validación de dominios de email permitidos
- ✅ Soft delete (desactivar en lugar de eliminar físicamente)

### Características Especiales
- Soft delete con posibilidad de reactivación
- Auditoría completa con IP y user agent
- Badges de color según rol (danger, warning, info, secondary)
- Indicadores visuales de usuarios inactivos
- Búsqueda en tiempo real
- Estadísticas (total usuarios, admins activos, cambios recientes)

## Scripts SQL

Proporciona el script SQL completo para crear las tablas según la base de datos elegida:

**Tablas necesarias**:
1. `user_permissions`:
   - user_email (unique)
   - role
   - is_active (para soft delete)
   - created_at, updated_at
   - created_by
   - last_login

2. `audit_log_permissions`:
   - admin_email
   - action (CREATE, UPDATE, DELETE, DEACTIVATE, REACTIVATE)
   - target_user_email
   - old_value, new_value
   - ip_address, user_agent
   - details (JSON/JSONB)
   - timestamp

**Incluye**:
- Índices para optimización
- Triggers para updated_at
- Constraints y validaciones

## Configuración

Proporciona:
1. Variables de entorno (.env):
   ```
   [Tu base de datos]_URL=...
   [Tu base de datos]_KEY=...
   ALLOWED_EMAIL_DOMAINS=@tu-dominio.com
   SECRET_KEY=...
   ```

2. Configuración en config.py con mis roles y permisos personalizados

3. Requirements.txt con todas las dependencias:
   - Flask
   - [Cliente de tu base de datos]
   - Flask-WTF (CSRF)
   - Flask-Limiter (rate limiting)
   - python-dotenv

## Archivos de Referencia

Usa como base la implementación de Dashboard-Ventas-Backup:
- src/permissions_manager.py (con Supabase) - adaptar a [mi base de datos]
- src/audit_logger.py (con Supabase) - adaptar a [mi base de datos]
- app.py líneas 334-610 (rutas admin)
- templates/admin/*.html (adaptar a mi diseño)

Ver documentación completa en:
- PLAN_MODULO_ADMIN_PERMISOS.md - Documentación técnica completa
- CONFIG_EJEMPLO_PERMISOS.md - Ejemplos de configuración
- CHECKLIST_IMPLEMENTACION_PERMISOS.md - Checklist paso a paso

## Testing

Proporciona tests básicos:
1. Tests unitarios para PermissionsManager:
   - test_add_user
   - test_update_user_role
   - test_delete_user (soft delete)
   - test_reactivate_user
   - test_has_permission
   - test_search_users

2. Tests de integración para rutas:
   - test_admin_access_requires_auth
   - test_admin_access_requires_admin_role
   - test_create_user_success
   - test_prevent_self_modification
   - test_prevent_self_deletion

## Usuario Admin Inicial

Proporciona script para crear el primer usuario admin:
```python
from src.permissions_manager import PermissionsManager
pm = PermissionsManager()
pm.add_user('admin@mi-dominio.com', 'admin_full', created_by='SYSTEM')
```

## Entregables

Por favor proporciona:
1. ✅ Código completo de src/permissions_manager.py adaptado a [mi base de datos]
2. ✅ Código completo de src/audit_logger.py adaptado a [mi base de datos]
3. ✅ Rutas Flask para app.py
4. ✅ Templates HTML (users_list, user_add, user_edit, audit_log)
5. ✅ JavaScript para validaciones y confirmaciones
6. ✅ Scripts SQL para crear tablas
7. ✅ Configuración (.env.example y config.py)
8. ✅ Tests básicos
9. ✅ Instrucciones de instalación y configuración
10. ✅ Script de creación de usuario admin inicial

## Adaptaciones Específicas de mi Proyecto

[Agrega aquí cualquier detalle específico de tu proyecto]:
- Framework CSS usado: [Bootstrap 5, Tailwind, Material UI, etc.]
- Sistema de autenticación actual: [Flask-Login, JWT, OAuth, etc.]
- Estructura de carpetas específica
- Convenciones de nombres
- Otras consideraciones especiales

## Referencia de Código

Si estoy migrando desde SQLite a Supabase, proporciona también:
- Script de migración de datos
- Comparativa de código entre ambas implementaciones
- Cambios necesarios en las queries

Si necesito integración con LDAP/Active Directory, incluye:
- Script de sincronización de usuarios
- Mapeo de grupos LDAP a roles de la aplicación

## Documentación

Incluye:
- README con instrucciones de instalación
- Documentación de los roles y permisos definidos
- Guía de usuario para administradores
- Procedimientos de backup y recuperación

---

## Checklist de Validación

Al finalizar la implementación, el módulo debe cumplir:

### Funcionalidad
- [ ] Administradores pueden ver lista de usuarios
- [ ] Administradores pueden crear usuarios nuevos
- [ ] Administradores pueden editar roles
- [ ] Administradores pueden desactivar usuarios
- [ ] Administradores pueden reactivar usuarios desactivados
- [ ] Se puede ver historial de cambios completo
- [ ] Búsqueda y filtros funcionan correctamente

### Seguridad
- [ ] Solo admin_full puede acceder al módulo
- [ ] CSRF protection activo
- [ ] Rate limiting configurado
- [ ] No permite auto-modificación de admin
- [ ] No permite auto-eliminación de admin
- [ ] Todas las acciones se auditan con IP
- [ ] Emails validados contra dominios permitidos

### Performance
- [ ] Lista de usuarios carga rápido (<500ms)
- [ ] Búsquedas responden rápido (<200ms)
- [ ] Índices de DB creados correctamente

### Usabilidad
- [ ] UI intuitiva y responsive
- [ ] Mensajes de error claros
- [ ] Confirmaciones antes de eliminar
- [ ] Feedback visual de todas las acciones
- [ ] Funciona en móvil

### Testing
- [ ] Tests unitarios pasan (100%)
- [ ] Tests de integración pasan
- [ ] Coverage > 80%

---

Por favor implementa este módulo siguiendo las mejores prácticas de seguridad y proporcionando código limpio, bien documentado y listo para producción.
```

---

## 🎯 Instrucciones de Uso

### 1. **Copia el Prompt Completo**
   - Copia todo el contenido del bloque de código superior
   - Pégalo en tu conversación con el asistente de IA

### 2. **Personaliza las Secciones Marcadas con [ ]**
   - Especifica tu tipo de proyecto
   - Elige la base de datos
   - Define tus roles y permisos
   - Agrega detalles específicos de tu proyecto

### 3. **Variables a Personalizar**

```markdown
[Especifica: E-commerce, CRM, Blog, etc.]  → Tu tipo de proyecto
[tu-dominio.com]                           → Tu dominio corporativo
[mi base de datos]                         → supabase/sqlite/postgresql/mysql
[Bootstrap 5, Tailwind, etc.]              → Tu framework CSS
[Flask-Login, JWT, etc.]                   → Tu sistema de autenticación
```

### 4. **Ejemplo de Personalización**

**Para un proyecto E-commerce con PostgreSQL:**

```markdown
**Tipo de proyecto**: E-commerce con catálogo de productos y sistema de pedidos

**Base de datos a usar**: 
- [x] PostgreSQL (auto-hospedado)

**Roles necesarios**:
- super_admin: Acceso total al sistema
- warehouse_manager: Gestión de inventario y pedidos
- customer_support: Atención a clientes y reembolsos
- marketing: Campañas y análisis de clientes
- viewer: Solo lectura

**Permisos necesarios**:
- view_orders
- edit_orders
- manage_inventory
- create_refunds
- view_customers
- manage_promotions
- export_data
- manage_users

**Dominio de email**: @mitienda.com

**Framework CSS**: Bootstrap 5

**Autenticación actual**: Flask-Login con sesiones
```

---

## 💡 Consejos para Mejores Resultados

### **Sé Específico**
```markdown
❌ Malo: "Necesito un sistema de permisos"
✅ Bueno: "Necesito un sistema de permisos para mi CRM de ventas con 3 niveles jerárquicos: director, manager y vendedor"
```

### **Proporciona Contexto**
```markdown
✅ "Mi proyecto ya usa Flask-Login para autenticación"
✅ "Uso Bootstrap 5 en todos los templates"
✅ "La base de datos ya está en PostgreSQL 15"
✅ "Necesito integración con Active Directory"
```

### **Especifica Prioridades**
```markdown
✅ "Prioridad ALTA: Seguridad y validaciones"
✅ "Prioridad MEDIA: UI bonita"
✅ "Prioridad BAJA: Exportación a Excel"
```

### **Menciona Restricciones**
```markdown
✅ "No puedo usar librerías de pago"
✅ "Debe funcionar en Python 3.8+"
✅ "Necesito que sea compatible con mi estructura actual de carpetas"
```

---

## 🔄 Variantes del Prompt

### **Variante 1: Solo Backend (API REST)**

Si solo necesitas el backend sin frontend:

```markdown
Implementa SOLO el backend del módulo de permisos como API REST con los siguientes endpoints:

POST   /api/users              - Crear usuario
GET    /api/users              - Listar usuarios
GET    /api/users/:email       - Obtener usuario
PUT    /api/users/:email       - Actualizar rol
DELETE /api/users/:email       - Desactivar usuario
POST   /api/users/:email/reactivate - Reactivar
GET    /api/audit-log          - Historial

Respuestas en JSON. Sin templates HTML.
Base de datos: [tu elección]
```

### **Variante 2: Migración desde Sistema Existente**

Si ya tienes usuarios en otro sistema:

```markdown
Tengo un sistema existente con usuarios en [SQLite/CSV/otro].
Necesito:
1. Implementar el módulo de permisos con [nueva base de datos]
2. Script de migración que preserve los usuarios actuales
3. Mapeo de roles antiguos a roles nuevos:
   - rol_antiguo_1 → rol_nuevo_1
   - rol_antiguo_2 → rol_nuevo_2

Estructura actual: [describe tu tabla/archivo actual]
```

### **Variante 3: Integración con LDAP/Active Directory**

Si necesitas integración con directorio corporativo:

```markdown
Además del módulo estándar, necesito:
- Sincronización automática con Active Directory
- Mapeo de grupos AD a roles de la aplicación:
  - CN=Admins,OU=Groups → admin_full
  - CN=Managers,OU=Groups → manager
  - CN=Users,OU=Groups → user_basic
- Script de sincronización diaria
- Fallback si LDAP no está disponible

Servidor LDAP: [tu servidor]
Base DN: [tu base DN]
```

---

## 📚 Archivos de Referencia para Adjuntar

Cuando uses el prompt, considera adjuntar estos archivos para mejor contexto:

1. **PLAN_MODULO_ADMIN_PERMISOS.md** - Documentación técnica completa
2. **CONFIG_EJEMPLO_PERMISOS.md** - Ejemplos de configuración
3. **CHECKLIST_IMPLEMENTACION_PERMISOS.md** - Checklist paso a paso

O simplemente menciona:
```markdown
Tengo documentación de referencia de una implementación exitosa con Supabase.
¿Quieres que te la comparta para que la uses como base?
```

---

## ⚡ Prompt Corto (Versión Rápida)

Si prefieres un prompt más conciso:

```markdown
Implementa un módulo completo de administración de permisos para mi proyecto Flask basado en la arquitectura de Dashboard-Ventas-Backup.

**Mi configuración**:
- Proyecto: [tipo]
- Base de datos: [elegir]
- Roles: [listar]
- Dominio email: @[tu-dominio]

**Necesito**:
✅ Backend con CRUD completo (soft delete + reactivación)
✅ Frontend con DataTables y validaciones
✅ Sistema de auditoría con IP y timestamps
✅ Seguridad (CSRF, rate limiting, anti auto-modificación)
✅ Tests básicos
✅ Scripts SQL
✅ Documentación

Usa como referencia: src/permissions_manager.py y src/audit_logger.py del proyecto Dashboard-Ventas-Backup (implementación con Supabase).

Adapta a mi base de datos [elegida] y personaliza roles según mi proyecto.
```

---

## 🎓 Mejores Prácticas

1. **Primero Define Bien los Roles**
   - Identifica todos los tipos de usuarios de tu sistema
   - Define claramente qué puede hacer cada uno
   - Evita roles demasiado granulares al inicio

2. **Empieza Simple**
   - Comienza con 3-4 roles básicos
   - Añade más según necesites
   - Más fácil expandir que simplificar

3. **Prueba con SQLite Primero**
   - Desarrolla y prueba localmente con SQLite
   - Migra a Supabase/PostgreSQL cuando funcione
   - Menos fricción en desarrollo

4. **Documenta tus Decisiones**
   - Qué rol puede hacer qué
   - Por qué elegiste esa estructura
   - Procedimientos de alta/baja de usuarios

---

## 📞 Soporte

Si el asistente necesita más información, puede pedirte:
- Estructura actual de tu base de datos
- Código de tu sistema de autenticación actual
- Templates base que uses (base.html)
- Convenciones de nombres de tu proyecto

**Prepara esta información antes de usar el prompt para mejores resultados.**

---

**Última actualización**: 21 de abril de 2026  
**Basado en**: Dashboard-Ventas-Backup v1.0  
**Compatibilidad**: Flask 2.0+ / Python 3.8+
