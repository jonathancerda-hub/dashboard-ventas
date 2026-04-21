# ✅ Checklist de Implementación - Módulo de Permisos
## Guía Rápida Paso a Paso

> 📅 **Creado**: 21 de abril de 2026  
> 🎯 **Propósito**: Lista de verificación para implementar el módulo en cualquier proyecto Flask  
> ⏱️ **Tiempo estimado**: 12-16 horas

---

## 📋 Fase 0: Preparación (30-60 minutos)

### Análisis del Proyecto

- [ ] **Identificar requisitos de roles**
  - ¿Cuántos roles necesitas?
  - ¿Qué permisos necesita cada rol?
  - ¿Hay jerarquía entre roles?

- [ ] **Definir permisos necesarios**
  ```
  Ejemplo:
  - view_dashboard
  - edit_data
  - export_reports
  - manage_users
  - (listar todos los permisos de tu aplicación)
  ```

- [ ] **Verificar stack tecnológico**
  - [x] Python 3.8+
  - [x] Flask 2.0+
  - [ ] Base de datos (SQLite/PostgreSQL/MySQL)
  - [ ] Bootstrap/Frontend framework

---

## 📦 Fase 1: Configuración Inicial (1-2 horas)

### 1.1 Dependencias

- [ ] **Instalar paquetes necesarios**
  ```bash
  pip install Flask Flask-WTF pydantic Flask-Limiter
  pip install python-dotenv  # Para variables de entorno
  ```

- [ ] **Actualizar requirements.txt**
  ```bash
  pip freeze > requirements.txt
  ```

### 1.2 Variables de Entorno

- [ ] **Crear archivo `.env`**
  ```bash
  cp .env.example .env  # Si existe ejemplo
  # o crear nuevo archivo .env
  ```

- [ ] **Configurar variables básicas**
  ```bash
  FLASK_ENV=development
  SECRET_KEY=your-secret-key-here
  ALLOWED_EMAIL_DOMAINS=@yourcompany.com
  PERMISSIONS_DB_PATH=permissions.db
  ```

- [ ] **Agregar `.env` a `.gitignore`**
  ```bash
  echo ".env" >> .gitignore
  ```

### 1.3 Archivo de Configuración

- [ ] **Crear/actualizar `config.py`**
  - [ ] Definir `ROLE_PERMISSIONS` con tus roles
  - [ ] Definir `ROLE_DISPLAY_NAMES` para UI
  - [ ] Configurar `ALLOWED_EMAIL_DOMAINS`
  - [ ] Establecer `ADMIN_RATE_LIMIT_PER_HOUR`

- [ ] **Ejemplo mínimo**:
  ```python
  # config.py
  class Config:
      SECRET_KEY = os.environ.get('SECRET_KEY')
      ROLE_PERMISSIONS = {
          'admin_full': ['view', 'edit', 'delete', 'manage_users'],
          'user': ['view']
      }
  ```

---

## 🗄️ Fase 2: Base de Datos (1-2 horas)

### 2.1 Scripts SQL

- [ ] **Crear directorio `migrations/`**
  ```bash
  mkdir -p migrations
  ```

- [ ] **Crear script de tablas**
  - [ ] Tabla `user_permissions`
  - [ ] Tabla `audit_log`
  - [ ] Índices necesarios
  - [ ] Triggers para `updated_at`

- [ ] **Archivo**: `migrations/001_create_permissions_tables.sql`

### 2.2 Ejecutar Migraciones

- [ ] **SQLite (desarrollo)**
  ```bash
  sqlite3 permissions.db < migrations/001_create_permissions_tables.sql
  ```

- [ ] **PostgreSQL (producción)**
  ```bash
  psql -d your_database -f migrations/001_create_permissions_tables.sql
  ```

### 2.3 Verificar Tablas

- [ ] **Comprobar que se crearon correctamente**
  ```sql
  SELECT * FROM user_permissions LIMIT 1;
  SELECT * FROM audit_log LIMIT 1;
  ```

---

## 💻 Fase 3: Backend - Lógica de Negocio (3-4 horas)

### 3.1 Permissions Manager

- [ ] **Crear directorio `src/` si no existe**
  ```bash
  mkdir -p src
  touch src/__init__.py
  ```

- [ ] **Crear `src/permissions_manager.py`**
  - [ ] Clase `PermissionsManager`
  - [ ] Método `add_user(email, role)`
  - [ ] Método `update_user_role(email, new_role)`
  - [ ] Método `delete_user(email)`
  - [ ] Método `get_all_users()`
  - [ ] Método `get_user_role(email)`
  - [ ] Método `has_permission(email, permission)`
  - [ ] Método `is_admin(email)`
  - [ ] Método `search_users(query)`
  - [ ] Método `get_users_by_role(role)`

- [ ] **Verificar imports necesarios**
  ```python
  import sqlite3
  from contextlib import contextmanager
  from typing import List, Dict, Optional
  ```

### 3.2 Audit Logger

- [ ] **Crear `src/audit_logger.py`**
  - [ ] Clase `AuditLogger`
  - [ ] Método `log_user_created()`
  - [ ] Método `log_user_updated()`
  - [ ] Método `log_user_deleted()`
  - [ ] Método `get_recent_logs(limit)`
  - [ ] Método `get_filtered_logs(days, action)`

### 3.3 Logging Config

- [ ] **Crear `src/logging_config.py`**
  - [ ] Función `setup_logging()`
  - [ ] Función `get_logger(name)`

- [ ] **Crear directorio `logs/`**
  ```bash
  mkdir -p logs
  echo "logs/" >> .gitignore
  ```

---

## 🌐 Fase 4: Backend - Rutas Flask (2-3 horas)

### 4.1 Decorador de Seguridad

- [ ] **Agregar a `app.py` o crear `src/decorators.py`**
  ```python
  def require_admin_full(f):
      @wraps(f)
      def decorated_function(*args, **kwargs):
          # Verificar autenticación y permisos
          ...
      return decorated_function
  ```

### 4.2 Rutas Administrativas

- [ ] **Crear ruta `/admin/users` (GET)**
  - Listar todos los usuarios
  - Aplicar decorador `@require_admin_full`

- [ ] **Crear ruta `/admin/users/add` (GET, POST)**
  - Mostrar formulario (GET)
  - Procesar creación (POST)
  - Validar email y rol
  - Registrar en audit log

- [ ] **Crear ruta `/admin/users/edit/<email>` (GET, POST)**
  - Mostrar formulario de edición (GET)
  - Procesar actualización (POST)
  - Prevenir auto-demotion de admin
  - Registrar en audit log

- [ ] **Crear ruta `/admin/users/delete/<email>` (POST)**
  - Eliminar usuario
  - Prevenir auto-eliminación
  - Registrar en audit log

- [ ] **Crear ruta `/admin/audit-log` (GET)**
  - Mostrar historial de cambios
  - Filtros opcionales

### 4.3 Validaciones Backend

- [ ] **Validar formato de email**
- [ ] **Validar dominios permitidos**
- [ ] **Validar que rol existe**
- [ ] **Prevenir duplicados**
- [ ] **Prevenir auto-modificación de admins**

---

## 🎨 Fase 5: Frontend - Templates (2-3 horas)

### 5.1 Estructura de Carpetas

- [ ] **Crear directorio `templates/admin/`**
  ```bash
  mkdir -p templates/admin
  ```

### 5.2 Templates

- [ ] **Crear `templates/admin/users_list.html`**
  - [ ] Tabla de usuarios
  - [ ] Columnas: Email, Rol, Permisos, Fechas, Acciones
  - [ ] Botones: Editar, Eliminar
  - [ ] Link a "Agregar Usuario"
  - [ ] Búsqueda y filtros (opcional con DataTables)

- [ ] **Crear `templates/admin/user_add.html`**
  - [ ] Formulario con email y rol
  - [ ] Select de roles dinámico
  - [ ] Preview de permisos según rol seleccionado
  - [ ] Validación de email
  - [ ] CSRF token

- [ ] **Crear `templates/admin/user_edit.html`**
  - [ ] Similar a add pero para editar
  - [ ] Email readonly (no editable)
  - [ ] Select de rol
  - [ ] Mostrar cambios de permisos

- [ ] **Crear `templates/admin/audit_log.html`**
  - [ ] Tabla de logs
  - [ ] Filtros por fecha y acción
  - [ ] Estadísticas (cards)

### 5.3 Agregar Link en Navegación

- [ ] **Actualizar `templates/base.html`** (o navbar)
  ```html
  {% if is_admin %}
  <li class="nav-item">
      <a class="nav-link" href="{{ url_for('admin_users') }}">
          <i class="fas fa-users-cog"></i> Administrar Usuarios
      </a>
  </li>
  {% endif %}
  ```

---

## 🎯 Fase 6: Frontend - JavaScript (1-2 horas)

### 6.1 Archivo Principal

- [ ] **Crear `static/js/admin_users.js`**
  - [ ] Validación de formularios
  - [ ] Preview de permisos dinámico
  - [ ] Confirmación antes de eliminar (SweetAlert2 o modal)
  - [ ] Integración con DataTables (opcional)

### 6.2 Estilos

- [ ] **Crear `static/css/admin.css`**
  - [ ] Estilos para badges de roles
  - [ ] Estilos para tablas
  - [ ] Responsive design

### 6.3 Incluir en Templates

- [ ] **Agregar scripts en templates admin**
  ```html
  <link rel="stylesheet" href="{{ url_for('static', filename='css/admin.css') }}">
  <script src="{{ url_for('static', filename='js/admin_users.js') }}"></script>
  ```

---

## 🧪 Fase 7: Testing (2-3 horas)

### 7.1 Configuración de Tests

- [ ] **Crear directorio `tests/` si no existe**
  ```bash
  mkdir -p tests
  touch tests/__init__.py
  ```

- [ ] **Crear `pytest.ini`**
  ```ini
  [pytest]
  testpaths = tests
  python_files = test_*.py
  ```

- [ ] **Crear `tests/conftest.py`**
  - [ ] Fixture `permissions_manager`
  - [ ] Fixture `audit_logger`
  - [ ] Fixture `client` (Flask test client)
  - [ ] Fixture `sample_users`

### 7.2 Tests Unitarios

- [ ] **Crear `tests/test_permissions_manager.py`**
  - [ ] Test `test_add_user()`
  - [ ] Test `test_update_user_role()`
  - [ ] Test `test_delete_user()`
  - [ ] Test `test_get_all_users()`
  - [ ] Test `test_search_users()`
  - [ ] Test `test_has_permission()`
  - [ ] Test `test_is_admin()`

- [ ] **Crear `tests/test_audit_logger.py`**
  - [ ] Test `test_log_user_created()`
  - [ ] Test `test_log_user_updated()`
  - [ ] Test `test_log_user_deleted()`
  - [ ] Test `test_get_recent_logs()`

### 7.3 Tests de Integración

- [ ] **Crear `tests/test_admin_routes.py`**
  - [ ] Test acceso requiere autenticación
  - [ ] Test acceso requiere rol admin
  - [ ] Test crear usuario exitoso
  - [ ] Test editar usuario exitoso
  - [ ] Test eliminar usuario exitoso
  - [ ] Test prevenir auto-demotion
  - [ ] Test prevenir auto-eliminación
  - [ ] Test validaciones de email

### 7.4 Ejecutar Tests

- [ ] **Correr tests**
  ```bash
  pytest tests/ -v
  ```

- [ ] **Verificar cobertura**
  ```bash
  pytest --cov=src tests/
  ```

- [ ] **Todos los tests pasan (100%)**

---

## 🔒 Fase 8: Seguridad (1-2 horas)

### 8.1 CSRF Protection

- [ ] **Instalar Flask-WTF**
  ```bash
  pip install Flask-WTF
  ```

- [ ] **Configurar en app.py**
  ```python
  from flask_wtf.csrf import CSRFProtect
  csrf = CSRFProtect(app)
  ```

- [ ] **Agregar tokens en formularios**
  ```html
  {{ csrf_token() }}
  ```

### 8.2 Rate Limiting

- [ ] **Instalar Flask-Limiter**
  ```bash
  pip install Flask-Limiter
  ```

- [ ] **Configurar en app.py**
  ```python
  from flask_limiter import Limiter
  limiter = Limiter(app)
  ```

- [ ] **Aplicar a rutas admin**
  ```python
  @limiter.limit("10 per hour")
  ```

### 8.3 Validaciones

- [ ] **Email corporativo solamente**
- [ ] **Roles válidos únicamente**
- [ ] **Prevenir inyección SQL** (usar parametrized queries)
- [ ] **Sanitizar inputs**

### 8.4 Auditoría

- [ ] **Registrar IP en audit log**
- [ ] **Registrar user agent**
- [ ] **Timestamp en todas las operaciones**

---

## 🚀 Fase 9: Deployment (1-2 horas)

### 9.1 Preparación

- [ ] **Crear usuario admin inicial**
  ```python
  from src.permissions_manager import PermissionsManager
  pm = PermissionsManager()
  pm.add_user('admin@yourcompany.com', 'admin_full')
  ```

- [ ] **Verificar variables de entorno producción**
  - [ ] `SECRET_KEY` segura (no hardcoded)
  - [ ] `ALLOWED_EMAIL_DOMAINS` correctos
  - [ ] `DATABASE_URL` configurada (si PostgreSQL)

### 9.2 Base de Datos Producción

- [ ] **Ejecutar migraciones en producción**
- [ ] **Verificar backups automáticos**
- [ ] **Configurar índices**

### 9.3 Testing en Staging

- [ ] **Deploy a ambiente staging**
- [ ] **Probar todas las funcionalidades**
  - [ ] Crear usuario
  - [ ] Editar usuario
  - [ ] Eliminar usuario
  - [ ] Ver audit log
  - [ ] Búsquedas y filtros

- [ ] **Probar casos edge**
  - [ ] Intentar auto-eliminarse
  - [ ] Intentar cambiar propio rol
  - [ ] Intentar acceder sin permisos

### 9.4 Deployment Producción

- [ ] **Deploy a producción**
- [ ] **Verificar que todo funciona**
- [ ] **Monitorear logs**

---

## 📚 Fase 10: Documentación (1 hora)

### 10.1 Documentación Técnica

- [ ] **Documentar configuración en README**
  - [ ] Variables de entorno necesarias
  - [ ] Roles y permisos definidos
  - [ ] Instrucciones de instalación

- [ ] **Documentar API/rutas**
  - [ ] Endpoints disponibles
  - [ ] Parámetros requeridos
  - [ ] Respuestas esperadas

### 10.2 Documentación de Usuario

- [ ] **Crear guía para administradores**
  - [ ] Cómo agregar usuarios
  - [ ] Cómo editar roles
  - [ ] Cómo ver historial
  - [ ] Mejores prácticas

- [ ] **Definir políticas**
  - [ ] Quién puede ser admin
  - [ ] Procedimiento para altas/bajas
  - [ ] Política de retención de logs

### 10.3 Comentarios en Código

- [ ] **Docstrings en funciones principales**
- [ ] **Comentarios en lógica compleja**
- [ ] **Type hints donde sea apropiado**

---

## ✅ Checklist Final de Validación

### Funcionalidad

- [ ] ✅ Administradores pueden ver lista de usuarios
- [ ] ✅ Administradores pueden crear usuarios
- [ ] ✅ Administradores pueden editar roles
- [ ] ✅ Administradores pueden eliminar usuarios
- [ ] ✅ Se puede ver historial de cambios
- [ ] ✅ Búsqueda y filtros funcionan
- [ ] ✅ Exportar a CSV funciona (si implementado)

### Seguridad

- [ ] ✅ Solo admin_full puede acceder al módulo
- [ ] ✅ CSRF protection activo
- [ ] ✅ Rate limiting configurado
- [ ] ✅ Validaciones de email funcionan
- [ ] ✅ No se permiten auto-modificaciones peligrosas
- [ ] ✅ Todas las acciones se auditan
- [ ] ✅ Logs incluyen IP y timestamp

### Performance

- [ ] ✅ Lista de usuarios carga rápido (<500ms)
- [ ] ✅ Búsquedas responden rápido (<200ms)
- [ ] ✅ Índices de DB están creados
- [ ] ✅ No hay queries N+1

### Usabilidad

- [ ] ✅ UI es intuitiva
- [ ] ✅ Mensajes de error claros
- [ ] ✅ Confirmaciones antes de eliminar
- [ ] ✅ Feedback visual de acciones
- [ ] ✅ Responsive en móvil

### Testing

- [ ] ✅ Todos los tests unitarios pasan
- [ ] ✅ Todos los tests de integración pasan
- [ ] ✅ Cobertura de código > 80%
- [ ] ✅ Tests de seguridad pasan

### Deployment

- [ ] ✅ Variables de entorno configuradas
- [ ] ✅ Base de datos migrada
- [ ] ✅ Usuario admin inicial creado
- [ ] ✅ Backups configurados
- [ ] ✅ Logs están siendo guardados

---

## 🎯 Tiempo Total Estimado

| Fase | Tiempo Estimado |
|------|----------------|
| 0. Preparación | 0.5-1h |
| 1. Configuración Inicial | 1-2h |
| 2. Base de Datos | 1-2h |
| 3. Backend - Lógica | 3-4h |
| 4. Backend - Rutas | 2-3h |
| 5. Frontend - Templates | 2-3h |
| 6. Frontend - JS/CSS | 1-2h |
| 7. Testing | 2-3h |
| 8. Seguridad | 1-2h |
| 9. Deployment | 1-2h |
| 10. Documentación | 1h |
| **TOTAL** | **12-16h** |

---

## 📝 Notas Importantes

**Consejos**:
- ✅ No saltes el testing
- ✅ Implementa seguridad desde el inicio
- ✅ Documenta mientras desarrollas
- ✅ Haz commits frecuentes
- ✅ Prueba en staging antes de producción

**Errores Comunes a Evitar**:
- ❌ Hardcodear SECRET_KEY
- ❌ No validar inputs del usuario
- ❌ Olvidar índices en base de datos
- ❌ No implementar rate limiting
- ❌ No crear usuario admin inicial
- ❌ Commitear archivos .env

**Recursos Útiles**:
- 📖 Plan completo: `PLAN_MODULO_ADMIN_PERMISOS.md`
- ⚙️ Ejemplos de config: `CONFIG_EJEMPLO_PERMISOS.md`
- 🔧 Flask Docs: https://flask.palletsprojects.com/
- 🧪 Pytest Docs: https://docs.pytest.org/

---

**🎉 ¡Éxito!** Una vez completados todos los checkboxes, tendrás un módulo de administración de permisos completamente funcional y seguro.
