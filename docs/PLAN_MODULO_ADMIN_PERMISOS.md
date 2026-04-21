# Plan de Implementación: Módulo de Administración de Permisos (Permissions Administration Module)
## Sistema Web para Gestión de Usuarios y Roles sin Tocar Código (Web System for User and Role Management without Code Changes)

> 📅 **Última actualización (Last update)**: 21 de abril de 2026  
> 🎯 **Objetivo (Objective)**: Panel administrativo web reutilizable para gestionar usuarios y permisos dinámicamente  
> ⏱️ **Tiempo estimado (Estimated time)**: 12-16 horas de desarrollo  
> 🔒 **Prioridad de seguridad (Security priority)**: ALTA - Solo accesible por admin_full  
> 🔄 **Portabilidad**: Diseñado para ser portable a cualquier proyecto Flask  
> ✅ **Estado**: **IMPLEMENTADO** en Dashboard-Ventas-Backup con Supabase

---

## 🎉 Implementación Actual del Proyecto

**Este módulo YA ESTÁ COMPLETAMENTE IMPLEMENTADO en el proyecto Dashboard-Ventas-Backup con las siguientes características:**

### ✅ Características Implementadas

**Backend:**
- ✅ `src/permissions_manager.py` - Gestor completo con **Supabase**
- ✅ `src/audit_logger.py` - Sistema de auditoría con **Supabase**
  - 🆕 **Auditoría de login/logout** (LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, SESSION_TIMEOUT)
  - 📝 Auditoría de cambios de permisos (CREATE, UPDATE, DELETE, REACTIVATE)
- ✅ **Soft Delete** (desactivación en lugar de eliminación física)
- ✅ **Reactivación de usuarios** desactivados
- ✅ Búsqueda y filtrado de usuarios
- ✅ Validaciones completas

**Frontend:**
- ✅ `templates/admin/users_list.html` - Lista de usuarios con DataTables
- ✅ `templates/admin/user_add.html` - Formulario de creación
- ✅ `templates/admin/user_edit.html` - Formulario de edición
- ✅ `templates/admin/audit_log.html` - Historial de cambios
- ✅ Páginas de error personalizadas (403, 404, 429, 500)

**Rutas Implementadas:**
- ✅ `GET /admin/users` - Lista de usuarios
- ✅ `GET/POST /admin/users/add` - Agregar usuario
- ✅ `GET/POST /admin/users/edit/<email>` - Editar usuario
- ✅ `POST /admin/users/delete/<email>` - Desactivar usuario (soft delete)
- ✅ `POST /admin/users/reactivate/<email>` - Reactivar usuario
- ✅ `GET /admin/audit-log` - Historial de auditoría

**Características Especiales:**
- 🔐 **Supabase** como base de datos (no SQLite)
- 🔄 **Soft Delete** para preservar historial
- 🔙 **Reactivación** de usuarios desactivados
- 📊 **Auditoría completa** con IP y user agent
  - 🆕 Login exitoso/fallido
  - 🆕 Logout manual y timeouts
  - 🆕 Duración de sesiones
  - 🆕 Correlación login-logout con session_id
- 🛡️ **Validaciones de seguridad** (anti auto-modificación)
- ⏱️ **Control de sesiones** (timeout por inactividad y absoluto)

---

## 📚 Propósito de este Documento

Este documento sirve como:

1. **Documentación técnica** del módulo ya implementado
2. **Guía de portabilidad** para implementar en otros proyectos Flask
3. **Referencia de arquitectura** y mejores prácticas
4. **Manual de adaptación** a diferentes bases de datos (SQLite, PostgreSQL, MySQL)

---

## 📋 Índice (Table of Contents)

1. [Configuración Inicial del Proyecto](#1-configuración-inicial-del-proyecto)
2. [Análisis del Estado Actual](#2-análisis-del-estado-actual)
3. [Arquitectura Propuesta](#3-arquitectura-propuesta)
4. [Plan de Implementación Fase por Fase](#4-plan-de-implementación-fase-por-fase)
5. [Especificación Técnica Detallada](#5-especificación-técnica-detallada)
6. [Seguridad y Validaciones](#6-seguridad-y-validaciones)
7. [Testing y Validación](#7-testing-y-validación)
8. [Roadmap de Implementación](#8-roadmap-de-implementación)
9. [Guía de Portabilidad](#9-guía-de-portabilidad)

---

## 1. Configuración Inicial del Proyecto (Initial Project Setup)

### 1.1 Requisitos Previos (Prerequisites)

**Stack Tecnológico (Implementado en Dashboard-Ventas-Backup)**:
- ✅ Python 3.11+
- ✅ Flask 3.1.3
- ✅ **Supabase** (PostgreSQL en la nube)
- ✅ Bootstrap 5 (frontend)
- ✅ jQuery + DataTables
- ✅ SweetAlert2 (confirmaciones)

**Alternativas para Otros Proyectos**:
- SQLite 3 (desarrollo local)
- PostgreSQL (auto-hospedado)
- MySQL/MariaDB

**Estructura Mínima del Proyecto**:
```plaintext
your-project/
├── app.py                      # Aplicación Flask principal
├── config.py                   # Configuraciones del proyecto
├── requirements.txt            # Dependencias Python
├── .env                        # Variables de entorno
├── src/                        # Código fuente
│   ├── __init__.py
│   └── (módulos existentes)
├── templates/                  # Templates Jinja2
│   └── base.html              # Template base
├── static/                     # Archivos estáticos
│   ├── css/
│   └── js/
└── tests/                      # Tests del proyecto
```

### 1.2 Variables de Configuración (Configuration Variables)

**Agregar a `config.py` o `.env`**:

```python
# config.py (Implementación actual con Supabase)
class Config:
    # Base de datos - Supabase (PostgreSQL)
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Alternativa para SQLite (otros proyectos)
    # PERMISSIONS_DB_PATH = 'permissions.db'
    
    # Seguridad
    SECRET_KEY = 'your-secret-key-here'  # Cambiar por valor seguro
    CSRF_ENABLED = True
    
    # Permisos - Dominios de email permitidos
    ALLOWED_EMAIL_DOMAINS = ['@yourcompany.com', '@example.com']
    
    # Rate Limiting
    ADMIN_RATE_LIMIT_PER_HOUR = 10
    
    # Roles y Permisos (personalizar según proyecto)
    ROLE_PERMISSIONS = {
        'admin_full': ['view_dashboard', 'view_analytics', 'edit_targets', 'export_data', 'manage_users'],
        'admin_export': ['view_dashboard', 'export_data'],
        'analytics_viewer': ['view_dashboard', 'view_analytics'],
        'user_basic': ['view_dashboard']
    }
    
    # Nombres display de roles (traducción)
    ROLE_DISPLAY_NAMES = {
        'admin_full': 'Administrador Completo',
        'admin_export': 'Administrador de Exportación',
        'analytics_viewer': 'Visualizador de Analíticas',
        'user_basic': 'Usuario Básico'
    }
```

**Variables de Entorno (`.env`) - Implementación Actual con Supabase**:
```bash
# Entorno
FLASK_ENV=development
FLASK_DEBUG=True

# Base de datos Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Alternativa SQLite (otros proyectos)
# PERMISSIONS_DB_PATH=permissions.db

# Email corporativo
ALLOWED_EMAIL_DOMAINS=@yourcompany.com,@example.com

# Seguridad
SECRET_KEY=change-this-to-random-secret-key
ADMIN_RATE_LIMIT_PER_HOUR=10

# Sesión
SESSION_TIMEOUT_MINUTES=30
```

### 1.3 Adaptación de Permisos por Proyecto (Project-Specific Permissions)

**Ejemplo para E-commerce**:
```python
ROLE_PERMISSIONS = {
    'admin_full': ['view_orders', 'manage_products', 'manage_users', 'view_reports', 'refund_orders'],
    'warehouse_manager': ['view_orders', 'update_inventory', 'view_products'],
    'customer_support': ['view_orders', 'update_order_status', 'refund_orders'],
    'viewer': ['view_orders', 'view_products']
}
```

**Ejemplo para CRM**:
```python
ROLE_PERMISSIONS = {
    'admin_full': ['manage_leads', 'manage_contacts', 'view_analytics', 'manage_users', 'export_data'],
    'sales_manager': ['manage_leads', 'view_analytics', 'export_data'],
    'sales_rep': ['manage_leads', 'manage_contacts'],
    'viewer': ['view_leads', 'view_contacts']
}
```

**Ejemplo para Sistema de Reportes**:
```python
ROLE_PERMISSIONS = {
    'admin_full': ['create_reports', 'edit_reports', 'delete_reports', 'manage_users', 'export_all'],
    'report_creator': ['create_reports', 'edit_own_reports', 'export_own'],
    'analyst': ['view_all_reports', 'export_all'],
    'viewer': ['view_assigned_reports']
}
```

---

## 2. Análisis del Estado Actual

---

(Current State Analysis)

### 2.1 Implementación Actual (Current Implementation - Supabase)

**📦 Componentes ya implementados (Already implemented components)**:
```python
# src/permissions_manager.py (IMPLEMENTADO con Supabase)
from supabase import create_client, Client

class PermissionsManager:
    # Roles y permisos definidos
    ROLE_PERMISSIONS = {
        'admin_full': ['view_dashboard', 'view_analytics', 'edit_targets', 'export_data', 'manage_users'],
        'admin_export': ['view_dashboard', 'view_analytics', 'export_data'],
        'analytics_viewer': ['view_dashboard', 'view_analytics'],
        'user_basic': ['view_dashboard']
    }
    
    def __init__(self):
        # Conectar con Supabase
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
    
    # ✅ Métodos implementados
    def add_user(email, role, created_by='SYSTEM')  # Crear usuario
    def update_user_role(email, new_role)           # Actualizar rol
    def delete_user(email, soft_delete=True)        # Desactivar usuario (soft delete)
    def reactivate_user(email)                      # Reactivar usuario desactivado
    def get_all_users(include_inactive=False)       # Listar usuarios
    def search_users(query, include_inactive=False) # Buscar usuarios
    def has_permission(email, perm)                 # Verificar permiso
    def is_admin(email)                             # Verificar si es admin
    def get_user_role(email)                        # Obtener rol del usuario
    def get_user_details(email)                     # Detalles completos
```

**Base de datos Supabase (PostgreSQL) - IMPLEMENTADO**:
```sql
-- Tabla: user_permissions (Supabase)
CREATE TABLE user_permissions (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,        -- Soft delete
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT 'SYSTEM',
    last_login TIMESTAMPTZ
);

-- Tabla: audit_log_permissions (Supabase)
CREATE TABLE audit_log_permissions (
    id BIGSERIAL PRIMARY KEY,
    admin_email TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN (
        'CREATE', 'UPDATE', 'DELETE', 'DEACTIVATE', 'ACTIVATE',
        'LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT', 'SESSION_TIMEOUT'
    )),
    target_user_email TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    user_agent TEXT,
    details JSONB,  -- session_id, duration, failure_reason, etc
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para optimización
CREATE INDEX idx_user_role ON user_permissions(role);
CREATE INDEX idx_user_active ON user_permissions(is_active);
CREATE INDEX idx_audit_timestamp ON audit_log_permissions(timestamp DESC);
CREATE INDEX idx_audit_action ON audit_log_permissions(action);
```

**Para proyectos con SQLite**, ver sección 9.5 "Alternativas de Base de Datos".

### 2.2 Problema Común en Sistemas Flask (Common Problem in Flask Systems)

❌ **Gestión manual de usuarios requiere**:
1. Acceso al servidor o entorno de desarrollo
2. Conocimiento de Python y estructura del código
3. Ejecutar comandos manualmente: `permissions_manager.add_user('nuevo@email.com', 'user_basic')`
4. Sin auditoría automática de cambios
5. Sin validación visual de datos
6. Propenso a errores humanos
7. No escalable para equipos no técnicos

### 2.3 Solución Universal Propuesta (Universal Solution Proposed)

✅ **Panel web administrativo en `/admin/users` que proporciona**:
- 📋 **Listado completo** de usuarios con roles y permisos
- ➕ **Crear usuarios** con validación automática
- ✏️ **Editar roles** sin reiniciar la aplicación
- 🗑️ **Eliminar usuarios** con confirmación segura
- 📊 **Historial de auditoría** de todos los cambios
- 🔍 **Búsqueda y filtros** por rol, email, fecha
- 📤 **Exportación** a CSV/Excel
- 🔒 **Seguridad integrada** (CSRF, rate limiting, validaciones)

**Beneficios**:
- ✅ No requiere conocimientos técnicos para gestionar usuarios
- ✅ Trazabilidad completa de cambios
- ✅ Reducción de errores humanos
- ✅ Escalable a equipos grandes
- ✅ Portable entre proyectos Flask

---

## 3. Arquitectura Propuesta (Proposed Architecture)

### 3.1 Estructura de Archivos Modular (Modular File Structure)

```plaintext
your-project/                       # 📁 Proyecto principal
├── app.py                          # ✏️ Agregar rutas del módulo admin
├── config.py                       # ✏️ Agregar configuración de permisos
├── requirements.txt                # ✏️ Agregar nuevas dependencias
├── .env                            # ✏️ Variables de entorno
│
├── src/                            # 📁 Código fuente
│   ├── permissions_manager.py      # 🆕 Gestor de permisos (core)
│   ├── audit_logger.py             # 🆕 Sistema de auditoría
│   └── admin_service.py            # 🆕 Lógica de negocio admin (opcional)
│
├── templates/                      # 📁 Templates Jinja2
│   ├── base.html                   # ✏️ Agregar link al módulo admin
│   └── admin/                      # 🆕 Carpeta del módulo admin
│       ├── users_list.html         # 🆕 Lista de usuarios
│       ├── user_edit.html          # 🆕 Editar usuario
│       ├── user_add.html           # 🆕 Agregar usuario
│       └── audit_log.html          # 🆕 Historial de auditoría
│
├── static/                         # 📁 Archivos estáticos
│   ├── css/
│   │   └── admin.css               # 🆕 Estilos del módulo
│   └── js/
│       └── admin_users.js          # 🆕 JavaScript del módulo
│
├── migrations/                     # 🆕 Migraciones DB (opcional)
│   └── create_permissions_tables.sql
│
└── tests/                          # 📁 Tests
    ├── test_permissions_manager.py # 🆕 Tests unitarios
    └── test_admin_routes.py        # 🆕 Tests de integración
```

**Leyenda**:
- 🆕 = Archivos nuevos a crear
- ✏️ = Archivos existentes a modificar
- 📁 = Carpetas

### 3.2 Patrón de Arquitectura (Architecture Pattern)

**MVC Adaptado para Flask**:

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (View)                    │
│  templates/admin/*.html + static/js/admin_users.js  │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP Requests
┌──────────────────────▼──────────────────────────────┐
│              CONTROLLER (Flask Routes)               │
│              app.py - /admin/* routes                │
└──────────────────────┬──────────────────────────────┘
                       │ Calls
┌──────────────────────▼──────────────────────────────┐
│              BUSINESS LOGIC (Service)                │
│        src/permissions_manager.py (CRUD ops)         │
│        src/audit_logger.py (Audit ops)               │
└──────────────────────┬──────────────────────────────┘
                       │ Queries
┌──────────────────────▼──────────────────────────────┐
│                   MODEL (Database)                   │
│         SQLite/PostgreSQL - permissions.db           │
│    Tables: user_permissions, audit_log               │
└──────────────────────────────────────────────────────┘
```

```mermaid
graph TD
    A[Usuario Admin accede a /admin/users] --> B{¿Tiene permiso admin_full?}
    B -->|No| C[Redirigir a dashboard con error]
    B -->|Sí| D[Mostrar panel admin]
    
    D --> E[Lista de usuarios]
    D --> F[Botón Agregar Usuario]
    D --> G[Búsqueda/Filtros]
    
    E --> H[Ver detalles]
    E --> I[Editar rol]
    E --> J[Eliminar usuario]
    
    F --> K[Formulario nuevo usuario]
    K --> L[Validar email único]
    L --> M[Guardar en DB]
    M --> N[Registrar en audit log]
    N --> O[Mostrar confirmación]
    
    I --> P[Formulario editar rol]
    P --> Q[Actualizar DB]
    Q --> N
    
    J --> R[Confirmación modal]
    R --> S[Eliminar de DB]
    S --> N
```

---

## 4. Plan de Implementación Fase por Fase (Phase-by-Phase Implementation Plan)

> **📌 NOTA**: Estas fases ya están **completadas** en el proyecto Dashboard-Ventas-Backup.
> Este plan sirve como referencia para implementar en **otros proyectos Flask**.

### 📦 Fase 1: Base del Sistema Admin (2-3 horas) ✅ COMPLETADO

**Objetivo**: Crear estructura básica y sistema de auditoría

**Implementación actual en Dashboard-Ventas-Backup:**

1. **✅ `src/audit_logger.py` implementado con Supabase**
   ```python
   # Sistema de auditoría de cambios y accesos - IMPLEMENTADO
   class AuditLogger:
       def __init__(self):
           # Conecta con Supabase
           self.supabase = create_client(...)
       
       # Auditoría de permisos
       def log_user_created(admin_email, new_user_email, role, ip_address, user_agent)
       def log_user_updated(admin_email, user_email, old_role, new_role, ip_address, user_agent)
       def log_user_deleted(admin_email, user_email, soft_delete, ip_address, user_agent)
       def log_user_reactivated(admin_email, user_email, ip_address, user_agent)
       
       # 🆕 Auditoría de autenticación (login/logout)
       def log_login_success(user_email, user_name, role, ip_address, user_agent, oauth_provider, session_id)
       def log_login_failed(attempted_email, ip_address, user_agent, failure_reason, error_message)
       def log_logout(user_email, ip_address, session_duration, logout_type, session_id)
       def log_session_timeout(user_email, timeout_type, last_activity, ip_address)
       
       # Consultas
       def get_recent_logs(limit=50)
       def get_filtered_logs(days, action_filter)
   ```

2. **✅ `src/permissions_manager.py` ampliado con métodos CRUD**
   ```python
   # Métodos implementados con Supabase
   def update_user_role(email, new_role)           # ✅ Implementado
   def delete_user(email, soft_delete=True)        # ✅ Implementado (soft delete)
   def reactivate_user(email)                      # ✅ Implementado (EXTRA)
   def get_all_users(include_inactive=False)       # ✅ Implementado
   def search_users(query, include_inactive=False) # ✅ Implementado
   def get_users_by_role(role)                     # ✅ Implementado
   def get_user_details(email)                     # ✅ Implementado
   ```

3. **✅ Tablas de Supabase creadas**
   - `user_permissions` - Con campo `is_active` para soft delete
   - `audit_log_permissions` - Con campos adicionales (ip_address, user_agent, details JSONB)

**Para otros proyectos con SQLite**, ver script SQL en sección 9.5.

**Criterio de éxito**: 
- ✅ Todos los métodos CRUD funcionan con Supabase
- ✅ Tests unitarios pasan
- ✅ Logs se guardan correctamente con metadata completa

---

### 🎨 Fase 2: Frontend - Lista de Usuarios (3-4 horas) ✅ COMPLETADO

**Objetivo**: Interfaz para ver y buscar usuarios

**Implementación actual:**

1. **✅ Ruta `/admin/users` implementada en app.py**
   ```python
   @app.route('/admin/users')
   @login_required
   def admin_users():
       # Validar que usuario es admin_full
       if not permissions_manager.is_admin(session['username']):
           flash('Acceso denegado. Solo administradores.', 'danger')
           return redirect(url_for('dashboard'))
       
       users = permissions_manager.get_all_users(include_inactive=True)
       audit_logs = audit_logger.get_recent_logs(limit=20)
       
       return render_template('admin/users_list.html',
                              users=users,
                              audit_logs=audit_logs,
                              is_admin=True)
   ```

2. **✅ Template `templates/admin/users_list.html` implementado**
   - Tabla con DataTables para búsqueda y paginación
   - Columnas: Email, Rol, Estado (Activo/Inactivo), Permisos, Fechas, Acciones
   - Botones: Editar, Desactivar, Reactivar
   - Badges de color según rol
   - Indicadores visuales de usuarios inactivos

3. **✅ JavaScript con validaciones**
   - DataTables configurado en español
   - Filtros por rol y estado
   - Confirmaciones con SweetAlert2
   - Búsqueda en tiempo real

**Características adicionales implementadas:**
- 🔍 Búsqueda por email
- 🎨 Badges de color por rol (danger, warning, info, secondary)
- 👁️ Indicador visual de usuarios inactivos (fondo gris)
- 🔄 Botón de reactivación para usuarios inactivos

**Criterio de éxito**:
- ✅ Tabla muestra todos los usuarios (activos e inactivos)
- ✅ Búsqueda funciona correctamente
- ✅ Filtros por rol y estado funcionan
- ✅ Botones redirigen/ejecutan correctamente

---

### ➕ Fase 3: Agregar Usuarios (2-3 horas) ✅ COMPLETADO

**Objetivo**: Formulario para crear nuevos usuarios

**Implementación actual:**

1. **✅ Ruta POST `/admin/users/add` implementada**
   - Validaciones de email corporativo
   - Verificación de duplicados
   - Registro automático en audit log con IP y user agent
   - Mensajes flash de éxito/error

2. **✅ Template `templates/admin/user_add.html` implementado**
   - Formulario con email y rol
   - Preview dinámico de permisos según rol seleccionado
   - Validación de dominios permitidos
   - CSRF token integrado

3. **✅ Validación JavaScript implementada**
   - Validación de formato de email
   - Verificación de dominio corporativo
   - Preview de permisos en tiempo real
   - Feedback visual

**Criterio de éxito**:
- ✅ Formulario valida email correctamente (@agrovetmarket.com)
- ✅ No permite duplicados
- ✅ Muestra permisos del rol seleccionado dinámicamente
- ✅ Se registra en audit log con metadata completa

---

### ✏️ Fase 4: Editar y Eliminar Usuarios (2-3 horas) ✅ COMPLETADO

**Objetivo**: Modificar roles existentes y desactivar usuarios

**Implementación actual:**

1. **✅ Ruta `/admin/users/edit/<email>` implementada**
   - Previene auto-modificación de admin
   - Muestra cambios de permisos antes de guardar
   - Auditoría automática de cambios

2. **✅ Ruta `/admin/users/delete/<email>` implementada**
   - **Soft delete** (desactivación, no eliminación física)
   - Previene auto-eliminación
   - Confirmación con SweetAlert2
   - Preserva datos para auditoría

3. **✅ Ruta `/admin/users/reactivate/<email>` implementada** (CARACTERÍSTICA EXTRA)
   - Permite reactivar usuarios desactivados
   - Registra reactivación en audit log
   - Restaura acceso completo

4. **✅ Templates implementados**
   - `user_edit.html` - Formulario de edición con preview de cambios
   - Modales de confirmación integrados

**Características de seguridad implementadas:**
- 🛡️ No permite que admin cambie su propio rol
- 🛡️ No permite auto-eliminación
- 🛡️ Confirmación doble antes de desactivar
- 🛡️ Todas las acciones registradas con IP

**Criterio de éxito**:
- ✅ No permite auto-modificación de admins
- ✅ Soft delete preserva historial
- ✅ Reactivación funciona correctamente
- ✅ Todas las acciones se auditan

---

### 📊 Fase 5: Dashboard de Auditoría (2-3 horas) ✅ COMPLETADO

**Objetivo**: Ver historial de cambios

**Implementación actual:**

1. **✅ Ruta `/admin/audit-log` implementada**
   - Filtros por fecha y tipo de acción
   - Paginación de resultados
   - Estadísticas de usuarios y cambios

2. **✅ Template `audit_log.html` implementado**
   - Tabla de logs con detalles completos
   - Cards con estadísticas (total usuarios, admins, cambios recientes)
   - Filtros interactivos
   - Indicadores de tipo de acción (color badges)

3. **✅ Metadata completa en logs**
   - IP address
   - User agent
   - Timestamp
   - Detalles en formato JSONB
   - Admin que realizó el cambio
   - Usuario afectado
   - Valores anteriores y nuevos

**Criterio de éxito**:
- ✅ Muestra todos los cambios con detalles completos
- ✅ Filtros por fecha y acción funcionan
- ✅ Estadísticas se calculan correctamente
- ✅ Incluye información de IP y navegador

---

### 🔐 Fase 6: Auditoría de Autenticación (Login/Logout) (2-3 horas) ✅ COMPLETADO

> **🆕 Funcionalidad agregada el 21 de abril de 2026**

**Objetivo**: Registrar todos los eventos de autenticación para cumplimiento de seguridad

**Implementación actual:**

#### 1. **✅ Métodos de auditoría agregados a `src/audit_logger.py`**

```python
def log_login_success(user_email, user_name, role, ip_address, 
                     user_agent, oauth_provider, session_id):
    """Registra inicio de sesión exitoso"""
    # Guarda: email, nombre, rol, IP, user agent, provider OAuth, session_id

def log_login_failed(attempted_email, ip_address, user_agent,
                    failure_reason, error_message):
    """Registra intento de login fallido"""
    # Guarda: email intentado, IP, user agent, razón del fallo, mensaje de error

def log_logout(user_email, ip_address, session_duration, 
              logout_type, session_id):
    """Registra cierre de sesión"""
    # Guarda: email, IP, duración de sesión, tipo (manual/timeout), session_id

def log_session_timeout(user_email, timeout_type, last_activity, ip_address):
    """Registra expiración de sesión por timeout"""
    # Guarda: email, tipo de timeout (inactivity/absolute_limit), última actividad
```

#### 2. **✅ Integración en rutas de autenticación**

**Ruta `/authorize` (OAuth callback):**
```python
# Login exitoso
audit_logger.log_login_success(
    user_email=email,
    user_name=name,
    role=role,
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent'),
    oauth_provider='google',
    session_id=session.get('session_id')
)

# Login fallido (usuario no autorizado)
audit_logger.log_login_failed(
    attempted_email=email,
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent'),
    failure_reason='user_not_authorized',
    error_message='El correo no tiene permiso para acceder'
)
```

**Ruta `/logout`:**
```python
# Cálculo de duración de sesión
login_time = datetime.fromisoformat(session['login_time'])
logout_time = datetime.now(UTC_TZ)
duration_delta = logout_time - login_time
session_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Registro de logout
audit_logger.log_logout(
    user_email=username,
    ip_address=request.remote_addr,
    session_duration=session_duration,
    logout_type='manual',
    session_id=session_id
)
```

**Función `verify_session_expiration()`:**
```python
# Timeout por inactividad
audit_logger.log_session_timeout(
    user_email=username,
    timeout_type='inactivity',
    last_activity=session.get('last_activity_time'),
    ip_address=request.remote_addr
)

# Timeout absoluto (8 horas)
audit_logger.log_session_timeout(
    user_email=username,
    timeout_type='absolute_limit',
    last_activity=session.get('last_activity_time'),
    ip_address=request.remote_addr
)
```

#### 3. **✅ Tipos de eventos registrados**

| Acción | Descripción | Datos guardados |
|--------|-------------|-----------------|
| `LOGIN_SUCCESS` | Login exitoso | email, nombre, rol, IP, user agent, OAuth provider, session_id |
| `LOGIN_FAILED` | Login fallido | email intentado, IP, user agent, razón (user_not_authorized, oauth_error, etc) |
| `LOGOUT` | Cierre de sesión manual | email, IP, duración de sesión, session_id |
| `SESSION_TIMEOUT` | Expiración automática | email, tipo (inactivity/absolute_limit), última actividad, IP |

#### 4. **✅ Metadata en campo JSONB `details`**

**Para LOGIN_SUCCESS:**
```json
{
  "name": "Juan Pérez",
  "role": "admin_full",
  "oauth_provider": "google",
  "session_id": "abc123def456...",
  "timestamp_readable": "2026-04-21T10:30:00Z"
}
```

**Para LOGIN_FAILED:**
```json
{
  "failure_reason": "user_not_authorized",
  "error_message": "El correo no tiene permiso para acceder a esta aplicación",
  "timestamp_readable": "2026-04-21T10:31:00Z"
}
```

**Para LOGOUT:**
```json
{
  "logout_type": "manual",
  "session_duration": "01:30:00",
  "session_id": "abc123def456...",
  "timestamp_readable": "2026-04-21T12:00:00Z"
}
```

**Para SESSION_TIMEOUT:**
```json
{
  "timeout_type": "inactivity",
  "last_activity": "2026-04-21T11:30:00Z",
  "timestamp_readable": "2026-04-21T12:00:00Z"
}
```

#### 5. **✅ Cumplimiento de estándares de seguridad**

| Estándar | Requisito | Estado |
|----------|-----------|--------|
| **ISO 27001** | A.12.4.1 - Registros de eventos (login/logout) | ✅ Completo |
| **OWASP Top 10** | A09:2021 - Security Logging | ✅ Completo |
| **PCI-DSS** | Requisito 10.2.5 - Accesos y cambios de privilegios | ✅ Completo |
| **GDPR** | Art. 32 - Trazabilidad de acceso a datos personales | ✅ Completo |
| **SOC 2** | CC6.8 - Monitoreo de actividades de usuarios | ✅ Completo |

#### 6. **✅ Beneficios implementados**

**Detección de amenazas:**
- ✅ Múltiples intentos fallidos desde misma IP → Posible ataque de fuerza bruta
- ✅ Login desde IP/ubicación inusual → Acceso sospechoso
- ✅ Login fuera de horario laboral → Alerta de seguridad

**Investigación de incidentes:**
- ✅ Rastreo completo de "¿Quién accedió cuándo?"
- ✅ Correlación login-logout con `session_id`
- ✅ Duración de sesiones para análisis de comportamiento

**Auditorías y compliance:**
- ✅ Evidencia para auditorías internas/externas
- ✅ Historial completo de accesos para certificaciones
- ✅ Trazabilidad de IP y dispositivos

**Criterio de éxito**:
- ✅ Todos los login exitosos se registran con metadata completa
- ✅ Todos los intentos fallidos se registran con razón del fallo
- ✅ Logout incluye duración de sesión calculada
- ✅ Timeouts se registran distinguiendo inactividad vs límite absoluto
- ✅ session_id permite correlacionar login con logout
- ✅ Información de IP y user agent en todos los eventos
- ✅ Cumple con ISO 27001, OWASP, PCI-DSS, GDPR, SOC 2

---

## 5. Especificación Técnica Detallada - Implementación con Supabase

> **Implementación actual del proyecto Dashboard-Ventas-Backup**

### 5.1 `src/permissions_manager.py` - Versión Supabase (IMPLEMENTADO)
   CREATE TABLE audit_log (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       admin_email TEXT NOT NULL,
       action TEXT NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE'
       target_user_email TEXT NOT NULL,
       old_value TEXT,
       new_value TEXT,
       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       ip_address TEXT
   );
   ```

**Criterio de éxito**: 
- ✅ Todos los métodos CRUD funcionan
- ✅ Tests unitarios pasan (test_permissions_manager.py)
- ✅ Logs se guardan correctamente

---

### 🎨 Fase 2: Frontend - Lista de Usuarios (3-4 horas)

**Objetivo**: Interfaz para ver y buscar usuarios

**Tareas**:

1. **Crear ruta `/admin/users` en app.py**
   ```python
   @app.route('/admin/users')
   @login_required
   def admin_users():
       # Validar que usuario es admin_full
       if not permissions_manager.is_admin(session['username']):
           flash('Acceso denegado. Solo administradores.', 'danger')
           return redirect(url_for('dashboard'))
       
       users = permissions_manager.get_all_users()
       audit_logs = audit_logger.get_recent_logs(limit=20)
       
       return render_template('admin/users_list.html',
                              users=users,
                              audit_logs=audit_logs,
                              is_admin=True)
   ```

2. **Crear `templates/admin/users_list.html`**
   ```html
   <!-- Tabla con DataTables para búsqueda y paginación -->
   <table id="usersTable" class="table table-striped">
       <thead>
           <tr>
               <th>Email</th>
               <th>Rol</th>
               <th>Permisos</th>
               <th>Creado</th>
               <th>Actualizado</th>
               <th>Acciones</th>
           </tr>
       </thead>
       <tbody>
           {% for user in users %}
           <tr>
               <td>{{ user.email }}</td>
               <td><span class="badge badge-{{ user.role_class }}">{{ user.role_display }}</span></td>
               <td>
                   {% for perm in user.permissions %}
                   <span class="badge badge-secondary">{{ perm }}</span>
                   {% endfor %}
               </td>
               <td>{{ user.created_at | date }}</td>
               <td>{{ user.updated_at | date }}</td>
               <td>
                   <a href="{{ url_for('admin_edit_user', email=user.email) }}" class="btn btn-sm btn-primary">
                       <i class="fas fa-edit"></i> Editar
                   </a>
                   <button onclick="deleteUser('{{ user.email }}')" class="btn btn-sm btn-danger">
                       <i class="fas fa-trash"></i> Eliminar
                   </button>
               </td>
           </tr>
           {% endfor %}
       </tbody>
   </table>
   ```

3. **Agregar búsqueda y filtros**
   ```javascript
   // static/js/admin_users.js
   $(document).ready(function() {
       $('#usersTable').DataTable({
           language: {
               url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json'
           },
           order: [[4, 'desc']], // Ordenar por fecha actualización
           columnDefs: [
               { targets: 5, orderable: false } // No ordenar columna Acciones
           ]
       });
       
       // Filtro por rol
       $('#roleFilter').on('change', function() {
           var role = $(this).val();
           $('#usersTable').DataTable().column(1).search(role).draw();
       });
   });
   ```

**Criterio de éxito**:
- ✅ Tabla muestra todos los usuarios
- ✅ Búsqueda funciona correctamente
- ✅ Filtro por rol funciona
- ✅ Botones redirigen correctamente

---

### ➕ Fase 3: Agregar Usuarios (2-3 horas)

**Objetivo**: Formulario para crear nuevos usuarios

**Tareas**:

1. **Crear ruta POST `/admin/users/add`**
   ```python
   @app.route('/admin/users/add', methods=['GET', 'POST'])
   @login_required
   def admin_add_user():
       if not permissions_manager.is_admin(session['username']):
           return jsonify({'error': 'Unauthorized'}), 403
       
       if request.method == 'POST':
           email = request.form.get('email').strip().lower()
           role = request.form.get('role')
           
           # Validaciones
           if not email or '@' not in email:
               flash('Email inválido', 'danger')
               return redirect(url_for('admin_users'))
           
           if role not in PermissionsManager.ROLE_PERMISSIONS:
               flash('Rol inválido', 'danger')
               return redirect(url_for('admin_users'))
           
           # Verificar que no existe
           if permissions_manager.get_user_role(email):
               flash(f'Usuario {email} ya existe', 'warning')
               return redirect(url_for('admin_users'))
           
           # Crear usuario
           success = permissions_manager.add_user(email, role)
           if success:
               # Log de auditoría
               audit_logger.log_user_created(
                   admin_email=session['username'],
                   new_user_email=email,
                   role=role,
                   ip_address=request.remote_addr
               )
               flash(f'Usuario {email} creado con rol {role}', 'success')
           else:
               flash('Error al crear usuario', 'danger')
           
           return redirect(url_for('admin_users'))
       
       return render_template('admin/user_add.html',
                              roles=PermissionsManager.ROLE_PERMISSIONS)
   ```

2. **Crear `templates/admin/user_add.html`**
   ```html
   <form method="POST" action="{{ url_for('admin_add_user') }}" id="addUserForm">
       <div class="form-group">
           <label for="email">Email del Usuario *</label>
           <input type="email" 
                  class="form-control" 
                  id="email" 
                  name="email" 
                  required
                  placeholder="usuario@yourcompany.com"
                  pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$">
           <small class="form-text text-muted">
               Debe ser un email corporativo válido
           </small>
       </div>
       
       <div class="form-group">
           <label for="role">Rol *</label>
           <select class="form-control" id="role" name="role" required>
               <option value="">-- Seleccionar Rol --</option>
               {% for role_key, permissions in roles.items() %}
               <option value="{{ role_key }}">
                   {{ role_key | replace('_', ' ') | title }} 
                   ({{ permissions | length }} permisos)
               </option>
               {% endfor %}
           </select>
       </div>
       
       <!-- Mostrar permisos dinámicamente según rol seleccionado -->
       <div id="permissionsPreview" class="alert alert-info" style="display:none;">
           <strong>Permisos incluidos:</strong>
           <ul id="permissionsList"></ul>
       </div>
       
       <button type="submit" class="btn btn-primary">
           <i class="fas fa-user-plus"></i> Crear Usuario
       </button>
       <a href="{{ url_for('admin_users') }}" class="btn btn-secondary">Cancelar</a>
   </form>
   ```

3. **Validación JavaScript**
   ```javascript
   // Mostrar permisos según rol seleccionado
   $('#role').on('change', function() {
       const role = $(this).val();
       const permissions = {
           'admin_full': ['view_dashboard', 'view_analytics', 'edit_targets', 'export_data'],
           'admin_export': ['view_dashboard', 'export_data'],
           'analytics_viewer': ['view_dashboard', 'view_analytics'],
           'user_basic': ['view_dashboard']
       };
       
       if (role && permissions[role]) {
           const permList = permissions[role].map(p => `<li>${p}</li>`).join('');
           $('#permissionsList').html(permList);
           $('#permissionsPreview').show();
       } else {
           $('#permissionsPreview').hide();
       }
   });
   
   // Validar email corporativo
   $('#addUserForm').on('submit', function(e) {
       const email = $('#email').val();
       const validDomains = ['@agrovetmarket.com', '@company.com']; // Configurar según dominio
       
       const isValid = validDomains.some(domain => email.endsWith(domain));
       if (!isValid) {
           e.preventDefault();
           alert('Solo se permiten emails corporativos');
           return false;
       }
   });
   ```

**Criterio de éxito**:
- ✅ Formulario valida email correctamente
- ✅ No permite duplicados
- ✅ Muestra permisos del rol seleccionado
- ✅ Se registra en audit log

---

### ✏️ Fase 4: Editar y Eliminar Usuarios (2-3 horas)

**Objetivo**: Modificar roles existentes y eliminar usuarios

**Tareas**:

1. **Ruta `/admin/users/edit/<email>`**
   ```python
   @app.route('/admin/users/edit/<email>', methods=['GET', 'POST'])
   @login_required
   def admin_edit_user(email):
       if not permissions_manager.is_admin(session['username']):
           return jsonify({'error': 'Unauthorized'}), 403
       
       user = permissions_manager.get_user_details(email)
       if not user:
           flash('Usuario no encontrado', 'danger')
           return redirect(url_for('admin_users'))
       
       if request.method == 'POST':
           new_role = request.form.get('role')
           old_role = user['role']
           
           if new_role == old_role:
               flash('No hay cambios que guardar', 'info')
               return redirect(url_for('admin_users'))
           
           # Prevenir que admin se quite sus propios permisos
           if email == session['username'] and new_role != 'admin_full':
               flash('No puedes cambiar tu propio rol de admin', 'danger')
               return redirect(url_for('admin_users'))
           
           success = permissions_manager.update_user_role(email, new_role)
           if success:
               audit_logger.log_user_updated(
                   admin_email=session['username'],
                   user_email=email,
                   old_role=old_role,
                   new_role=new_role,
                   ip_address=request.remote_addr
               )
               flash(f'Rol de {email} actualizado a {new_role}', 'success')
           else:
               flash('Error al actualizar usuario', 'danger')
           
           return redirect(url_for('admin_users'))
       
       return render_template('admin/user_edit.html', 
                              user=user,
                              roles=PermissionsManager.ROLE_PERMISSIONS)
   ```

2. **Ruta `/admin/users/delete/<email>` (DELETE o POST)**
   ```python
   @app.route('/admin/users/delete/<email>', methods=['POST'])
   @login_required
   def admin_delete_user(email):
       if not permissions_manager.is_admin(session['username']):
           return jsonify({'error': 'Unauthorized'}), 403
       
       # No permitir auto-eliminación
       if email == session['username']:
           return jsonify({'error': 'No puedes eliminar tu propio usuario'}), 400
       
       user = permissions_manager.get_user_details(email)
       if not user:
           return jsonify({'error': 'Usuario no encontrado'}), 404
       
       success = permissions_manager.delete_user(email)
       if success:
           audit_logger.log_user_deleted(
               admin_email=session['username'],
               user_email=email,
               ip_address=request.remote_addr
           )
           return jsonify({'message': f'Usuario {email} eliminado correctamente'}), 200
       else:
           return jsonify({'error': 'Error al eliminar usuario'}), 500
   ```

3. **Modal de confirmación para eliminar**
   ```javascript
   function deleteUser(email) {
       Swal.fire({
           title: '¿Eliminar usuario?',
           html: `Se eliminará permanentemente el usuario:<br><strong>${email}</strong>`,
           icon: 'warning',
           showCancelButton: true,
           confirmButtonColor: '#d33',
           cancelButtonColor: '#3085d6',
           confirmButtonText: 'Sí, eliminar',
           cancelButtonText: 'Cancelar'
       }).then((result) => {
           if (result.isConfirmed) {
               fetch(`/admin/users/delete/${email}`, {
                   method: 'POST',
                   headers: {
                       'Content-Type': 'application/json'
                   }
               })
               .then(response => response.json())
               .then(data => {
                   if (data.message) {
                       Swal.fire('Eliminado', data.message, 'success')
                           .then(() => location.reload());
                   } else {
                       Swal.fire('Error', data.error, 'error');
                   }
               })
               .catch(error => {
                   Swal.fire('Error', 'Error al eliminar usuario', 'error');
               });
           }
       });
   }
   ```

**Criterio de éxito**:
- ✅ No permite que admin edite su propio rol
- ✅ No permite auto-eliminación
- ✅ Confirmación antes de eliminar
- ✅ Todas las acciones se auditan

---

### 📊 Fase 5: Dashboard de Auditoría (2-3 horas)

**Objetivo**: Ver historial de cambios

**Tareas**:

1. **Ruta `/admin/audit-log`**
   ```python
   @app.route('/admin/audit-log')
   @login_required
   def admin_audit_log():
       if not permissions_manager.is_admin(session['username']):
           return jsonify({'error': 'Unauthorized'}), 403
       
       # Filtros opcionales
       days = request.args.get('days', 30, type=int)
       action_filter = request.args.get('action', '')
       
       logs = audit_logger.get_filtered_logs(
           days=days,
           action=action_filter
       )
       
       # Estadísticas
       stats = {
           'total_users': permissions_manager.count_users(),
           'total_admins': permissions_manager.count_admins(),
           'changes_last_week': audit_logger.count_changes_last_week()
       }
       
       return render_template('admin/audit_log.html',
                              logs=logs,
                              stats=stats)
   ```

2. **Vista de auditoría**
   ```html
   <!-- templates/admin/audit_log.html -->
   <div class="row mb-4">
       <div class="col-md-4">
           <div class="card text-white bg-primary">
               <div class="card-body">
                   <h5 class="card-title">Total Usuarios</h5>
                   <h2>{{ stats.total_users }}</h2>
               </div>
           </div>
       </div>
       <div class="col-md-4">
           <div class="card text-white bg-success">
               <div class="card-body">
                   <h5 class="card-title">Administradores</h5>
                   <h2>{{ stats.total_admins }}</h2>
               </div>
           </div>
       </div>
       <div class="col-md-4">
           <div class="card text-white bg-info">
               <div class="card-body">
                   <h5 class="card-title">Cambios (Última Semana)</h5>
                   <h2>{{ stats.changes_last_week }}</h2>
               </div>
           </div>
       </div>
   </div>
   
   <table class="table table-hover">
       <thead>
           <tr>
               <th>Fecha/Hora</th>
               <th>Administrador</th>
               <th>Acción</th>
               <th>Usuario Afectado</th>
               <th>Cambios</th>
               <th>IP</th>
           </tr>
       </thead>
       <tbody>
           {% for log in logs %}
           <tr>
               <td>{{ log.timestamp | datetime }}</td>
               <td>{{ log.admin_email }}</td>
               <td>
                   <span class="badge badge-{{ log.action_class }}">
                       {{ log.action }}
                   </span>
               </td>
               <td>{{ log.target_user_email }}</td>
               <td>
                   {% if log.action == 'UPDATE' %}
                   {{ log.old_value }} → {{ log.new_value }}
                   {% else %}
                   {{ log.new_value }}
                   {% endif %}
               </td>
               <td><small>{{ log.ip_address }}</small></td>
           </tr>
           {% endfor %}
       </tbody>
   </table>
   ```

**Criterio de éxito**:
- ✅ Muestra todos los cambios con detalles
- ✅ Filtros por fecha y tipo de acción funcionan
- ✅ Estadísticas se calculan correctamente

---

## 4. Especificación Técnica Detallada (Detailed Technical Specification)

### 4.1 Ampliaciones de `permissions_manager.py`

```python
class PermissionsManager:
    # ... métodos existentes ...
    
    def update_user_role(self, user_email: str, new_role: str) -> bool:
        """
        Actualiza el rol de un usuario existente.
        
        Args:
            user_email: Email del usuario
            new_role: Nuevo rol a asignar
        
        Returns:
            bool: True si se actualizó correctamente
        """
        if new_role not in self.ROLE_PERMISSIONS:
            logger.error(f"Rol inválido: {new_role}")
            return False
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_permissions 
                    SET role = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_email = ?
                """, (new_role, user_email))
                
                if cursor.rowcount == 0:
                    logger.warning(f"Usuario no encontrado: {user_email}")
                    return False
                
                logger.info(f"Rol actualizado: {user_email} → {new_role}")
                return True
        except Exception as e:
            logger.error(f"Error al actualizar rol: {e}", exc_info=True)
            return False
    
    def delete_user(self, user_email: str) -> bool:
        """
        Elimina un usuario del sistema de permisos.
        
        Args:
            user_email: Email del usuario a eliminar
        
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM user_permissions 
                    WHERE user_email = ?
                """, (user_email,))
                
                if cursor.rowcount == 0:
                    logger.warning(f"Usuario no encontrado para eliminar: {user_email}")
                    return False
                
                logger.info(f"Usuario eliminado: {user_email}")
                return True
        except Exception as e:
            logger.error(f"Error al eliminar usuario: {e}", exc_info=True)
            return False
    
    def get_all_users(self) -> List[Dict]:
        """
        Obtiene lista de todos los usuarios con sus detalles.
        
        Returns:
            List[Dict]: Lista de usuarios con email, role, permisos, fechas
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_email, role, created_at, updated_at
                    FROM user_permissions
                    ORDER BY updated_at DESC
                """)
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'email': row['user_email'],
                        'role': row['role'],
                        'role_display': row['role'].replace('_', ' ').title(),
                        'permissions': self.ROLE_PERMISSIONS[row['role']],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'role_class': self._get_role_badge_class(row['role'])
                    })
                
                return users
        except Exception as e:
            logger.error(f"Error al obtener usuarios: {e}", exc_info=True)
            return []
    
    def search_users(self, query: str) -> List[Dict]:
        """Busca usuarios por email"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_email, role, created_at, updated_at
                    FROM user_permissions
                    WHERE user_email LIKE ?
                    ORDER BY user_email
                """, (f'%{query}%',))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}", exc_info=True)
            return []
    
    def get_users_by_role(self, role: str) -> List[Dict]:
        """Filtra usuarios por rol específico"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_email, role, created_at, updated_at
                    FROM user_permissions
                    WHERE role = ?
                    ORDER BY user_email
                """, (role,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al filtrar por rol: {e}", exc_info=True)
            return []
    
    def get_user_details(self, user_email: str) -> Optional[Dict]:
        """Obtiene detalles completos de un usuario"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_email, role, created_at, updated_at
                    FROM user_permissions
                    WHERE user_email = ?
                """, (user_email,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'email': row['user_email'],
                        'role': row['role'],
                        'permissions': self.ROLE_PERMISSIONS[row['role']],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                return None
        except Exception as e:
            logger.error(f"Error al obtener detalles: {e}", exc_info=True)
            return None
    
    def count_users(self) -> int:
        """Cuenta total de usuarios"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM user_permissions")
                return cursor.fetchone()['count']
        except Exception as e:
            logger.error(f"Error al contar usuarios: {e}", exc_info=True)
            return 0
    
    def count_admins(self) -> int:
        """Cuenta total de administradores"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM user_permissions 
                    WHERE role = 'admin_full'
                """)
                return cursor.fetchone()['count']
        except Exception as e:
            logger.error(f"Error al contar admins: {e}", exc_info=True)
            return 0
    
    @staticmethod
    def _get_role_badge_class(role: str) -> str:
        """Retorna clase CSS para badge según rol"""
        badge_classes = {
            'admin_full': 'danger',
            'admin_export': 'warning',
            'analytics_viewer': 'info',
            'user_basic': 'secondary'
        }
        return badge_classes.get(role, 'secondary')
```

### 4.2 Crear `src/audit_logger.py`

```python
"""
audit_logger.py - Sistema de auditoría de cambios de permisos

Registra todas las operaciones CRUD sobre usuarios y permisos
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from src.logging_config import get_logger

logger = get_logger(__name__)


class AuditLogger:
    """
    Logger de auditoría para cambios en permisos de usuario.
    
    Registra:
    - Creación de usuarios
    - Actualización de roles
    - Eliminación de usuarios
    - IP, timestamp, admin que realizó el cambio
    """
    
    def __init__(self, db_path='permissions.db'):
        """Inicializa el audit logger"""
        self.db_path = db_path
        self._init_audit_table()
        logger.info(f"AuditLogger inicializado con DB: {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en conexión DB audit: {e}", exc_info=True)
            raise
        finally:
            if conn:
                conn.close()
    
    def _init_audit_table(self):
        """Crea tabla de auditoría si no existe"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        admin_email TEXT NOT NULL,
                        action TEXT NOT NULL CHECK(action IN ('CREATE', 'UPDATE', 'DELETE')),
                        target_user_email TEXT NOT NULL,
                        old_value TEXT,
                        new_value TEXT,
                        ip_address TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índices para búsquedas rápidas
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                    ON audit_log(timestamp DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_admin 
                    ON audit_log(admin_email)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_target 
                    ON audit_log(target_user_email)
                """)
                
                logger.info("Tabla de auditoría inicializada")
        except Exception as e:
            logger.error(f"Error al inicializar tabla audit: {e}", exc_info=True)
    
    def log_user_created(self, admin_email: str, new_user_email: str, 
                         role: str, ip_address: str = None):
        """Registra creación de nuevo usuario"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_log (admin_email, action, target_user_email, 
                                           new_value, ip_address)
                    VALUES (?, 'CREATE', ?, ?, ?)
                """, (admin_email, new_user_email, role, ip_address))
                
                logger.info(f"Audit log: {admin_email} creó usuario {new_user_email} con rol {role}")
        except Exception as e:
            logger.error(f"Error al registrar creación: {e}", exc_info=True)
    
    def log_user_updated(self, admin_email: str, user_email: str, 
                         old_role: str, new_role: str, ip_address: str = None):
        """Registra actualización de rol"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_log (admin_email, action, target_user_email, 
                                           old_value, new_value, ip_address)
                    VALUES (?, 'UPDATE', ?, ?, ?, ?)
                """, (admin_email, user_email, old_role, new_role, ip_address))
                
                logger.info(f"Audit log: {admin_email} actualizó {user_email}: {old_role} → {new_role}")
        except Exception as e:
            logger.error(f"Error al registrar actualización: {e}", exc_info=True)
    
    def log_user_deleted(self, admin_email: str, user_email: str, ip_address: str = None):
        """Registra eliminación de usuario"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_log (admin_email, action, target_user_email, 
                                           ip_address)
                    VALUES (?, 'DELETE', ?, ?)
                """, (admin_email, user_email, ip_address))
                
                logger.info(f"Audit log: {admin_email} eliminó usuario {user_email}")
        except Exception as e:
            logger.error(f"Error al registrar eliminación: {e}", exc_info=True)
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Obtiene logs recientes con detalles formateados"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, admin_email, action, target_user_email,
                           old_value, new_value, ip_address, timestamp
                    FROM audit_log
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                logs = []
                for row in cursor.fetchall():
                    logs.append({
                        'id': row['id'],
                        'admin_email': row['admin_email'],
                        'action': row['action'],
                        'action_class': self._get_action_badge_class(row['action']),
                        'target_user_email': row['target_user_email'],
                        'old_value': row['old_value'],
                        'new_value': row['new_value'],
                        'ip_address': row['ip_address'] or 'N/A',
                        'timestamp': row['timestamp']
                    })
                
                return logs
        except Exception as e:
            logger.error(f"Error al obtener logs: {e}", exc_info=True)
            return []
    
    def get_filtered_logs(self, days: int = 30, action: str = '') -> List[Dict]:
        """Obtiene logs con filtros"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, admin_email, action, target_user_email,
                           old_value, new_value, ip_address, timestamp
                    FROM audit_log
                    WHERE timestamp >= datetime('now', '-{} days')
                """.format(days)
                
                params = []
                if action:
                    query += " AND action = ?"
                    params.append(action)
                
                query += " ORDER BY timestamp DESC"
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al filtrar logs: {e}", exc_info=True)
            return []
    
    def count_changes_last_week(self) -> int:
        """Cuenta cambios en los últimos 7 días"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM audit_log
                    WHERE timestamp >= datetime('now', '-7 days')
                """)
                return cursor.fetchone()['count']
        except Exception as e:
            logger.error(f"Error al contar cambios: {e}", exc_info=True)
            return 0
    
    @staticmethod
    def _get_action_badge_class(action: str) -> str:
        """Retorna clase CSS para badge según acción"""
        badge_classes = {
            'CREATE': 'success',
            'UPDATE': 'info',
            'DELETE': 'danger'
        }
        return badge_classes.get(action, 'secondary')
```

---

## 5. Seguridad y Validaciones (Security & Validations)

### 5.1 Validaciones del Backend

```python
# Decorador de seguridad para rutas admin
from functools import wraps
from flask import session, redirect, url_for, flash

def require_admin_full(f):
    """Decorador que requiere rol admin_full para acceder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('login'))
        
        if not permissions_manager.is_admin(session['username']):
            flash('Acceso denegado. Solo administradores.', 'danger')
            logger.warning(f"Intento de acceso no autorizado a admin: {session['username']}")
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# Uso en rutas:
@app.route('/admin/users')
@require_admin_full
def admin_users():
    # ... código de la ruta
```

### 5.2 Validaciones de Datos

```python
from pydantic import BaseModel, EmailStr, validator

class UserCreateSchema(BaseModel):
    """Schema de validación para crear usuario"""
    email: EmailStr
    role: str
    
    @validator('email')
    def validate_corporate_email(cls, v):
        """Solo permite emails corporativos"""
        from config import Config
        allowed_domains = Config.ALLOWED_EMAIL_DOMAINS
        if not any(v.endswith(domain) for domain in allowed_domains):
            raise ValueError('Solo se permiten emails corporativos autorizados')
        return v.lower()
    
    @validator('role')
    def validate_role_exists(cls, v):
        """Verifica que el rol exista"""
        if v not in PermissionsManager.ROLE_PERMISSIONS:
            raise ValueError(f'Rol inválido: {v}')
        return v

class UserUpdateSchema(BaseModel):
    """Schema de validación para actualizar usuario"""
    role: str
    
    @validator('role')
    def validate_role_exists(cls, v):
        if v not in PermissionsManager.ROLE_PERMISSIONS:
            raise ValueError(f'Rol inválido: {v}')
        return v
```

### 5.3 Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Aplicar a rutas admin
@app.route('/admin/users/add', methods=['POST'])
@require_admin_full
@limiter.limit("10 per hour")  # Máximo 10 usuarios creados por hora
def admin_add_user():
    # ... código
```

### 5.4 CSRF Protection

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# En templates de formularios:
<form method="POST">
    {{ csrf_token() }}
    <!-- resto del formulario -->
</form>

# Para AJAX:
<script>
    fetch('/admin/users/delete/email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token() }}'
        }
    });
</script>
```

---

## 6. Testing y Validación (Testing & Validation)

### 6.1 Tests Unitarios

```python
# tests/test_admin_permissions.py
import pytest
from src.permissions_manager import PermissionsManager
from src.audit_logger import AuditLogger

@pytest.fixture
def permissions_manager():
    """Fixture con DB de prueba"""
    pm = PermissionsManager(db_path=':memory:')
    yield pm

@pytest.fixture
def audit_logger():
    """Fixture con audit logger de prueba"""
    al = AuditLogger(db_path=':memory:')
    yield al

class TestPermissionsManager:
    def test_update_user_role(self, permissions_manager):
        """Test actualización de rol"""
        # Crear usuario
        permissions_manager.add_user('test@company.com', 'user_basic')
        
        # Actualizar rol
        success = permissions_manager.update_user_role('test@company.com', 'admin_full')
        assert success is True
        
        # Verificar cambio
        role = permissions_manager.get_user_role('test@company.com')
        assert role == 'admin_full'
    
    def test_delete_user(self, permissions_manager):
        """Test eliminación de usuario"""
        permissions_manager.add_user('delete@company.com', 'user_basic')
        
        success = permissions_manager.delete_user('delete@company.com')
        assert success is True
        
        # Verificar que no existe
        role = permissions_manager.get_user_role('delete@company.com')
        assert role is None
    
    def test_get_all_users(self, permissions_manager):
        """Test obtener todos los usuarios"""
        permissions_manager.add_user('user1@company.com', 'user_basic')
        permissions_manager.add_user('user2@company.com', 'admin_full')
        
        users = permissions_manager.get_all_users()
        assert len(users) == 2
        assert users[0]['email'] == 'user1@company.com'
    
    def test_search_users(self, permissions_manager):
        """Test búsqueda de usuarios"""
        permissions_manager.add_user('john@company.com', 'user_basic')
        permissions_manager.add_user('jane@company.com', 'admin_full')
        
        results = permissions_manager.search_users('john')
        assert len(results) == 1
        assert results[0]['user_email'] == 'john@company.com'

class TestAuditLogger:
    def test_log_user_created(self, audit_logger):
        """Test registro de creación"""
        audit_logger.log_user_created(
            admin_email='admin@company.com',
            new_user_email='new@company.com',
            role='user_basic',
            ip_address='127.0.0.1'
        )
        
        logs = audit_logger.get_recent_logs(limit=1)
        assert len(logs) == 1
        assert logs[0]['action'] == 'CREATE'
        assert logs[0]['target_user_email'] == 'new@company.com'
    
    def test_log_user_updated(self, audit_logger):
        """Test registro de actualización"""
        audit_logger.log_user_updated(
            admin_email='admin@company.com',
            user_email='user@company.com',
            old_role='user_basic',
            new_role='admin_full',
            ip_address='127.0.0.1'
        )
        
        logs = audit_logger.get_recent_logs(limit=1)
        assert len(logs) == 1
        assert logs[0]['action'] == 'UPDATE'
        assert logs[0]['old_value'] == 'user_basic'
        assert logs[0]['new_value'] == 'admin_full'
    
    def test_count_changes_last_week(self, audit_logger):
        """Test conteo de cambios recientes"""
        audit_logger.log_user_created('admin@company.com', 'user1@company.com', 'user_basic')
        audit_logger.log_user_created('admin@company.com', 'user2@company.com', 'user_basic')
        
        count = audit_logger.count_changes_last_week()
        assert count == 2
```

### 6.2 Tests de Integración

```python
# tests/test_admin_routes.py
import pytest
from app import app

@pytest.fixture
def client():
    """Cliente de prueba Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestAdminRoutes:
    def test_admin_users_requires_login(self, client):
        """Test que /admin/users requiere autenticación"""
        response = client.get('/admin/users')
        assert response.status_code == 302  # Redirect a login
    
    def test_admin_users_requires_admin_role(self, client):
        """Test que solo admin_full puede acceder"""
        # Login como user_basic
        with client.session_transaction() as sess:
            sess['username'] = 'basic@company.com'
        
        response = client.get('/admin/users')
        assert response.status_code == 302  # Redirect a dashboard
        # Verificar flash message de acceso denegado
    
    def test_admin_add_user_success(self, client):
        """Test crear usuario exitosamente"""
        with client.session_transaction() as sess:
            sess['username'] = 'admin@company.com'
        
        response = client.post('/admin/users/add', data={
            'email': 'newuser@company.com',
            'role': 'user_basic'
        })
        
        assert response.status_code == 302  # Redirect después de crear
        # Verificar que usuario se creó en DB
    
    def test_admin_edit_user_prevent_self_demotion(self, client):
        """Test que admin no puede cambiar su propio rol"""
        with client.session_transaction() as sess:
            sess['username'] = 'admin@company.com'
        
        response = client.post('/admin/users/edit/admin@company.com', data={
            'role': 'user_basic'
        })
        
        # Debe rechazar el cambio
        assert 'No puedes cambiar tu propio rol' in response.data.decode()
```

---

## 8. Roadmap de Implementación (Implementation Roadmap)

> **✅ PROYECTO DASHBOARD-VENTAS-BACKUP: TODAS LAS FASES COMPLETADAS**

### 📅 Estado Actual del Proyecto

| Fase | Estado | Implementación |
|------|--------|----------------|
| 0. Preparación | ✅ COMPLETADO | Análisis de requisitos, roles definidos |
| 1. Configuración y Base | ✅ COMPLETADO | Supabase configurado, variables de entorno |
| 2. Backend - Lógica | ✅ COMPLETADO | permissions_manager.py + audit_logger.py |
| 3. Backend - Rutas | ✅ COMPLETADO | 6 rutas admin implementadas |
| 4. Frontend - Templates | ✅ COMPLETADO | 4 templates + páginas de error |
| 5. Frontend - JS/CSS | ✅ COMPLETADO | Validaciones, DataTables, SweetAlert2 |
| 6. Seguridad | ✅ COMPLETADO | CSRF, validaciones, rate limiting |
| 7. Testing | ✅ COMPLETADO | Tests unitarios e integración |
| 8. Deployment | ✅ COMPLETADO | Desplegado en Render.com |
| 9. Documentación | 🔄 EN PROCESO | Este documento |

---

### 📋 Para Implementar en Otros Proyectos (New Project Implementation)

**Sprint 1: Semana 1 (Sprint 1: Week 1)**

**Días 1-2: Configuración y Base del Sistema**
- [ ] Configurar variables de entorno (.env)
- [ ] Decidir base de datos (Supabase/SQLite/PostgreSQL)
- [ ] Definir roles y permisos en config.py
- [ ] Crear `src/audit_logger.py` (adaptar de este proyecto)
- [ ] Crear `src/permissions_manager.py` (adaptar de este proyecto)
- [ ] Crear tablas en base de datos
- [ ] Crear tests unitarios
- [ ] Validar que todos los tests pasan

**Días 3-4: Frontend - Lista de Usuarios**
- [ ] Copiar y adaptar ruta `/admin/users` de app.py
- [ ] Copiar template `templates/admin/users_list.html`
- [ ] Adaptar a tu diseño (Bootstrap/Tailwind/etc)
- [ ] Integrar DataTables (opcional)
- [ ] Agregar filtros por rol
- [ ] Testing manual de la interfaz

**Día 5: Agregar Usuarios**
- [ ] Copiar ruta POST `/admin/users/add`
- [ ] Copiar template `user_add.html`
- [ ] Adaptar validaciones de dominio de email
- [ ] Implementar preview de permisos
- [ ] Testing de validaciones
- [ ] Testing de validaciones

### 📅 Sprint 2: Semana 2 (Sprint 2: Week 2)

**Días 6-7: Editar y Eliminar (Days 6-7: Edit & Delete)**
- [ ] Crear ruta `/admin/users/edit/<email>`
- [ ] Crear `templates/admin/user_edit.html`
- [ ] Crear ruta DELETE `/admin/users/delete/<email>`
- [ ] Modal de confirmación SweetAlert2
- [ ] Validar que admin no se auto-elimina

**Días 8-9: Auditoría (Days 8-9: Audit)**
- [ ] Crear ruta `/admin/audit-log`
- [ ] Crear `templates/admin/audit_log.html`
- [ ] Dashboard con estadísticas
- [ ] Filtros por fecha y acción

**Día 10: Testing y Deployment (Day 10: Testing & Deployment)**
- [ ] Tests de integración completos
- [ ] Validación de seguridad (OWASP A01, A04)
- [ ] Documentación final
- [ ] Deploy a producción

---

## 📊 Métricas de Éxito (Success Metrics)

### Funcionalidad (Functionality)
- ✅ Administradores pueden agregar usuarios sin tocar código
- ✅ Administradores pueden editar roles dinámicamente
- ✅ Administradores pueden eliminar usuarios
- ✅ Todas las acciones se auditan correctamente
- ✅ Búsqueda y filtros funcionan correctamente

### Seguridad (Security)
- ✅ Solo admin_full puede acceder al módulo
- ✅ Admin no puede cambiar su propio rol a uno inferior
- ✅ Admin no puede auto-eliminarse
- ✅ Todas las validaciones de email funcionan
- ✅ Rate limiting previene abuso
- ✅ CSRF protection activo

### Performance (Performance)
- ✅ Lista de usuarios carga en <500ms
- ✅ Búsquedas responden en <200ms
- ✅ Operaciones CRUD en <100ms

### Usabilidad (Usability)
- ✅ UI intuitiva sin necesidad de capacitación
- ✅ Confirmaciones apropiadas antes de eliminar
- ✅ Feedback claro de éxito/error
- ✅ Responsive en móvil/tablet

---

## 🔧 Configuración Adicional (Additional Configuration)

### Agregar a `requirements.txt`

```plaintext
# Ya existentes...
Flask==3.1.3
Flask-WTF==1.2.1

# Nuevas dependencias
Flask-Limiter==3.5.0  # Rate limiting
pydantic==2.10.5  # Validación de datos
```

### Variables de Entorno (`.env`)

```bash
# Admin módule configuration
ADMIN_RATE_LIMIT_PER_HOUR=10
ALLOWED_EMAIL_DOMAINS=@agrovetmarket.com,@company.com
```

---

## 📚 Documentación de Usuario Final (End User Documentation)

### Guía para Administradores (Administrator Guide)

**Acceso al Módulo (Module Access)**:
1. Iniciar sesión como usuario con rol `admin_full`
2. En el menú superior, clic en "Administración" → "Usuarios"
3. Verás listado completo de usuarios actuales

**Agregar Nuevo Usuario (Add New User)**:
1. Clic en botón "➕ Agregar Usuario"
2. Ingresar email corporativo válido
3. Seleccionar rol apropiado:
   - **Admin Full**: Acceso total (administrar usuarios, metas, analytics, exports)
   - **Admin Export**: Puede exportar datos solamente
   - **Analytics Viewer**: Solo visualiza analytics
   - **User Basic**: Solo visualiza dashboards
4. Revisar permisos que se otorgarán (aparecen automáticamente)
5. Clic en "Crear Usuario"
6. Confirmar mensaje de éxito

**Editar Rol de Usuario (Edit User Role)**:
1. En la lista de usuarios, clic en "✏️ Editar"
2. Seleccionar nuevo rol del dropdown
3. Revisar cambios de permisos
4. Clic en "Guardar Cambios"
5. Usuario recibirá nuevo nivel de acceso inmediatamente

**Eliminar Usuario (Delete User)**:
1. En la lista, clic en "🗑️ Eliminar"
2. Confirmar en el modal de seguridad
3. Usuario pierde acceso inmediatamente

**Ver Historial de Cambios (View Change History)**:
1. Clic en pestaña "Historial de Auditoría"
2. Ver todos los cambios con:
   - Quién hizo el cambio
   - Cuándo (fecha/hora)
   - Qué cambió (rol anterior → nuevo rol)
   - IP desde donde se hizo el cambio

---

## 🎯 Próximos Pasos Recomendados (Recommended Next Steps)

### Mejoras Futuras (Future Improvements)

**Fase 3: Permisos Granulares (2-3 semanas)**:
- [ ] Permitir crear permisos personalizados por usuario
- [ ] Sistema de "Grupos" de usuarios
- [ ] Permisos por línea comercial específica

**Fase 4: Notificaciones (1 semana)**:
- [ ] Enviar email al usuario cuando se crea su cuenta
- [ ] Notificar cuando cambia su rol
- [ ] Alertas a admins cuando se crean usuarios nuevos

**Fase 5: Integraciones (2 semanas)**:
- [ ] Integración con LDAP/Active Directory corporativo
- [ ] SSO (Single Sign-On) con Azure AD
- [ ] Sincronización automática de bajas/altas

---

## 💬 Preguntas Frecuentes (FAQ)

**Q: ¿Los cambios son inmediatos?**  
A: Sí, cuando actualizas un rol, el usuario debe cerrar sesión y volver a ingresar para que se apliquen los nuevos permisos.

**Q: ¿Puedo importar una lista masiva de usuarios?**  
A: En Fase 1 es manual. Puedes agregar funcionalidad de "Import CSV" en mejoras futuras.

**Q: ¿Hay límite de usuarios?**  
A: No hay límite técnico. SQLite soporta millones de registros.

**Q: ¿Qué pasa si elimino a todos los admins?**  
A: Sistema requiere al menos 1 admin. Si intentas eliminar al último admin_full, se rechaza la operación.

**Q: ¿Los logs de auditoría se pueden exportar?**  
A: Sí, puedes agregar botón "Exportar a CSV" en la vista de audit log.

---

## 📞 Soporte (Support)

Para consultas técnicas sobre implementación:
- **Documentación completa**: Ver este documento
- **Ejemplos de código**: Ver secciones 4.1 y 4.2
- **Tests de referencia**: Ver `tests/test_admin_permissions.py`

---

**🎯 Resumen Ejecutivo Final (Final Executive Summary)**:

### Proyecto Dashboard-Ventas-Backup (IMPLEMENTADO ✅)

Este módulo está **completamente implementado y funcional** en el proyecto Dashboard-Ventas-Backup con:

✅ **CRUD completo** de usuarios con Supabase  
✅ **4 roles predefinidos** personalizables  
✅ **Sistema de auditoría** completo con metadata (IP, user agent)  
✅ **Seguridad robusta** (CSRF, validaciones, rate limiting, anti auto-modificación)  
✅ **Soft delete** (desactivación en lugar de eliminación física)  
✅ **Reactivación de usuarios** desactivados  
✅ **UI intuitiva** (DataTables, SweetAlert2, badges de color)  
✅ **Testing exhaustivo** (unitarios + integración)  
✅ **Portable** a cualquier proyecto Flask  
✅ **Desplegado en producción** (Render.com)

**Características técnicas:**
- **Base de datos**: Supabase (PostgreSQL en la nube)
- **Backend**: Flask 3.1.3 + Python 3.11
- **Frontend**: Bootstrap 5 + jQuery + DataTables
- **Seguridad**: CSRF protection, rate limiting, validaciones
- **Auditoría**: Logs completos con IP, timestamp, user agent

---

### Para Implementar en Otros Proyectos

**Tiempo estimado**: 12-16 horas (usando este proyecto como referencia)  
**Complejidad**: Media  
**ROI**: Alto (elimina necesidad de acceso técnico para gestionar usuarios)  
**Escalabilidad**: Diseñado para 10-10,000+ usuarios

**Opciones de base de datos:**
- **Supabase**: Recomendado para producción cloud (como Dashboard-Ventas-Backup)
- **SQLite**: Ideal para desarrollo y prototipos
- **PostgreSQL**: Para producción on-premise
- **MySQL**: Alternativa compatible

**Archivos de referencia en este proyecto:**
- `src/permissions_manager.py` - Gestor completo con Supabase
- `src/audit_logger.py` - Sistema de auditoría
- `app.py` - Rutas `/admin/*` (líneas 334-610)
- `templates/admin/*.html` - Templates del módulo
- `static/js/admin_users.js` - JavaScript del módulo

---

## 📞 Soporte y Contacto (Support & Contact)

Para consultas sobre esta implementación:
- **Código fuente**: Dashboard-Ventas-Backup
- **Documentación técnica**: Este documento
- **Ejemplos de configuración**: [CONFIG_EJEMPLO_PERMISOS.md](CONFIG_EJEMPLO_PERMISOS.md)
- **Checklist de implementación**: [CHECKLIST_IMPLEMENTACION_PERMISOS.md](CHECKLIST_IMPLEMENTACION_PERMISOS.md)

**Migración entre bases de datos**:
- SQLite → Supabase: Sección 9.3
- Supabase → PostgreSQL: Compatible directo (ambos usan PostgreSQL)
- SQLite → PostgreSQL: Script incluido en sección 9.5

**Contribuciones**:
Si implementas mejoras o adaptaciones útiles, documéntalas para futuros proyectos.

---

**📌 Nota Final**: 

Este plan documenta un **módulo ya implementado y probado en producción**. Úsalo como:

1. **Documentación técnica** del sistema actual
2. **Guía de referencia** para entender la arquitectura
3. **Template portable** para implementar en otros proyectos Flask
4. **Comparativa de bases de datos** (Supabase vs SQLite vs PostgreSQL)

La implementación actual con **Supabase** ha demostrado ser:
- ✅ Escalable (maneja tráfico de producción)
- ✅ Confiable (backups automáticos, alta disponibilidad)
- ✅ Económica (plan gratuito para desarrollo)
- ✅ Fácil de mantener (managed service)

Para proyectos nuevos, considera **Supabase** como primera opción, especialmente si necesitas:
- Despliegue rápido en la nube
- Escalabilidad automática
- API REST out-of-the-box
- Panel de administración visual

Para proyectos locales o con requisitos específicos de privacidad, usa **SQLite** (desarrollo) o **PostgreSQL local** (producción).

---

**Última actualización**: 21 de abril de 2026  
**Versión del módulo**: 1.0 (Estable - Producción)  
**Proyecto**: Dashboard-Ventas-Backup  
**Stack**: Flask 3.1.3 + Supabase + Bootstrap 5

---

## 9. Guía de Portabilidad (Portability Guide)

### 9.1 Diferencias Clave: Supabase vs SQLite vs PostgreSQL

**Implementación actual (Dashboard-Ventas-Backup)** usa **Supabase**. Esta sección documenta cómo adaptar a otras bases de datos.

| Característica | Supabase (Actual) | SQLite | PostgreSQL Local |
|----------------|-------------------|--------|------------------|
| **Tipo** | PostgreSQL en la nube | Archivo local | Servidor local |
| **Conexión** | API REST + Python SDK | sqlite3 module | psycopg2 |
| **Escalabilidad** | Alta (cloud) | Baja (archivo único) | Media-Alta |
| **Costo** | Freemium (500MB gratis) | Gratis | Gratis (self-hosted) |
| **Complejidad** | Baja (managed) | Muy baja | Media |
| **Backups** | Automáticos | Manuales | Configurables |
| **Concurrencia** | Alta | Baja-Media | Alta |
| **Mejor para** | Producción cloud | Desarrollo/prototipos | Producción on-premise |

---

### 9.2 Código Comparativo: Supabase vs SQLite

#### **A. Inicialización (Init)**

**Supabase (Implementación actual):**
```python
# src/permissions_manager.py
from supabase import create_client, Client

class PermissionsManager:
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Conectado a Supabase")
```

**SQLite (Para otros proyectos):**
```python
# src/permissions_manager.py
import sqlite3
from contextlib import contextmanager

class PermissionsManager:
    def __init__(self, db_path='permissions.db'):
        self.db_path = db_path
        self._init_database()
        logger.info(f"✅ Conectado a SQLite: {db_path}")
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
```

---

#### **B. Agregar Usuario (Add User)**

**Supabase (Implementación actual):**
```python
def add_user(self, user_email: str, role: str = 'user_basic', created_by: str = 'SYSTEM') -> bool:
    try:
        data = {
            'user_email': user_email.lower(),
            'role': role,
            'is_active': True,
            'created_by': created_by
        }
        
        response = self.supabase.table('user_permissions')\
            .insert(data)\
            .execute()
        
        if response.data:
            logger.info(f"✅ Usuario creado: {user_email}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error al crear usuario: {e}")
        return False
```

**SQLite (Para otros proyectos):**
```python
def add_user(self, user_email: str, role: str = 'user_basic') -> bool:
    try:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_permissions (user_email, role, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_email.lower(), role))
            
            logger.info(f"✅ Usuario creado: {user_email}")
            return True
    except sqlite3.IntegrityError:
        logger.warning(f"Usuario ya existe: {user_email}")
        return False
    except Exception as e:
        logger.error(f"❌ Error al crear usuario: {e}")
        return False
```

---

#### **C. Obtener Todos los Usuarios (Get All Users)**

**Supabase (Implementación actual):**
```python
def get_all_users(self, include_inactive: bool = False) -> List[Dict]:
    try:
        query = self.supabase.table('user_permissions')\
            .select('*')\
            .order('updated_at', desc=True)
        
        if not include_inactive:
            query = query.eq('is_active', True)
        
        response = query.execute()
        
        users = []
        for user in response.data:
            users.append({
                'email': user['user_email'],
                'role': user['role'],
                'is_active': user.get('is_active', True),
                'permissions': self.ROLE_PERMISSIONS[user['role']],
                'created_at': user.get('created_at'),
                'updated_at': user.get('updated_at'),
                'role_class': self._get_role_badge_class(user['role'])
            })
        
        return users
    except Exception as e:
        logger.error(f"❌ Error al obtener usuarios: {e}")
        return []
```

**SQLite (Para otros proyectos):**
```python
def get_all_users(self) -> List[Dict]:
    try:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_email, role, created_at, updated_at
                FROM user_permissions
                ORDER BY updated_at DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'email': row['user_email'],
                    'role': row['role'],
                    'permissions': self.ROLE_PERMISSIONS[row['role']],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'role_class': self._get_role_badge_class(row['role'])
                })
            
            return users
    except Exception as e:
        logger.error(f"❌ Error al obtener usuarios: {e}")
        return []
```

---

#### **D. Soft Delete (Desactivación)**

**Supabase (Implementación actual):**
```python
def delete_user(self, user_email: str, soft_delete: bool = True) -> bool:
    try:
        if soft_delete:
            # Desactivar usuario (soft delete)
            response = self.supabase.table('user_permissions')\
                .update({'is_active': False})\
                .eq('user_email', user_email.lower())\
                .execute()
        else:
            # Eliminación física (no recomendado)
            response = self.supabase.table('user_permissions')\
                .delete()\
                .eq('user_email', user_email.lower())\
                .execute()
        
        if response.data:
            logger.info(f"✅ Usuario {'desactivado' if soft_delete else 'eliminado'}: {user_email}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error al eliminar usuario: {e}")
        return False
```

**SQLite (Para otros proyectos):**
```python
def delete_user(self, user_email: str, soft_delete: bool = True) -> bool:
    try:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if soft_delete:
                # Soft delete - agregar columna is_active a tu tabla
                cursor.execute("""
                    UPDATE user_permissions 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE user_email = ?
                """, (user_email.lower(),))
            else:
                # Hard delete
                cursor.execute("""
                    DELETE FROM user_permissions 
                    WHERE user_email = ?
                """, (user_email.lower(),))
            
            if cursor.rowcount == 0:
                logger.warning(f"Usuario no encontrado: {user_email}")
                return False
            
            logger.info(f"✅ Usuario {'desactivado' if soft_delete else 'eliminado'}: {user_email}")
            return True
    except Exception as e:
        logger.error(f"❌ Error al eliminar usuario: {e}")
        return False
```

---

### 9.3 Migración de SQLite a Supabase

Si tienes un proyecto con SQLite y quieres migrar a Supabase:

**Paso 1: Crear tablas en Supabase**
```sql
-- Ejecutar en Supabase SQL Editor
CREATE TABLE user_permissions (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT 'SYSTEM'
);

CREATE TABLE audit_log_permissions (
    id BIGSERIAL PRIMARY KEY,
    admin_email TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN (
        'CREATE', 'UPDATE', 'DELETE', 'DEACTIVATE', 'ACTIVATE',
        'LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT', 'SESSION_TIMEOUT'
    )),
    target_user_email TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    user_agent TEXT,
    details JSONB,  -- session_id, duration, failure_reason, oauth_provider, etc
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

**Paso 2: Script de migración de datos**
```python
# migrate_sqlite_to_supabase.py
import sqlite3
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_users():
    """Migrar usuarios de SQLite a Supabase"""
    
    # Conectar a SQLite
    sqlite_conn = sqlite3.connect('permissions.db')
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    # Conectar a Supabase
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    # Leer usuarios de SQLite
    cursor.execute("SELECT * FROM user_permissions")
    users = cursor.fetchall()
    
    migrated = 0
    errors = 0
    
    for user in users:
        try:
            data = {
                'user_email': user['user_email'],
                'role': user['role'],
                'is_active': user.get('is_active', True),
                'created_by': 'MIGRATION'
            }
            
            supabase.table('user_permissions').insert(data).execute()
            migrated += 1
            print(f"✅ Migrado: {user['user_email']}")
        except Exception as e:
            errors += 1
            print(f"❌ Error migrando {user['user_email']}: {e}")
    
    sqlite_conn.close()
    print(f"\n📊 Resumen: {migrated} migrados, {errors} errores")

if __name__ == '__main__':
    migrate_users()
```

---

### 9.4 Características Únicas de la Implementación con Supabase

**Ventajas implementadas en Dashboard-Ventas-Backup:**

1. **🔄 Real-time subscriptions** (no usado actualmente, pero disponible)
   ```python
   # Posible mejora futura: notificaciones en tiempo real
   def subscribe_to_user_changes(callback):
       channel = supabase.channel('user_permissions')
       channel.on('INSERT', callback).subscribe()
   ```

2. **🔐 Row Level Security (RLS)** 
   - Configurado en Supabase para seguridad adicional
   - Solo permite operaciones de usuarios autenticados

3. **📊 JSONB para metadata**
   - Campo `details` en audit_log permite almacenar metadata compleja
   - Búsquedas eficientes en JSON

4. **🔍 Full-text search** (disponible, no implementado)
   ```python
   # Búsqueda avanzada de texto completo
   response = supabase.table('user_permissions')\
       .select('*')\
       .text_search('user_email', 'juan')\
       .execute()
   ```

5. **🌐 Edge Functions** (disponible para lógica serverless)

---

### 9.5 Alternativas de Base de Datos - Scripts SQL Completos

#### **A. SQLite (Desarrollo / Prototipos)**

```sql
-- migrations/create_permissions_tables_sqlite.sql
-- Sistema de permisos con SQLite

-- Tabla de usuarios y roles
CREATE TABLE IF NOT EXISTS user_permissions (
    user_email TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,  -- 1 = activo, 0 = inactivo (soft delete)
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    created_by TEXT DEFAULT 'SYSTEM',
    last_login TEXT
);

-- Tabla de auditoría
CREATE TABLE IF NOT EXISTS audit_log_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_email TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('CREATE', 'UPDATE', 'DELETE', 'DEACTIVATE', 'REACTIVATE')),
    target_user_email TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    user_agent TEXT,
    details TEXT,  -- JSON como texto
    timestamp TEXT DEFAULT (datetime('now'))
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_user_role ON user_permissions(role);
CREATE INDEX IF NOT EXISTS idx_user_active ON user_permissions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_email ON user_permissions(user_email);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log_permissions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_admin ON audit_log_permissions(admin_email);
CREATE INDEX IF NOT EXISTS idx_audit_target ON audit_log_permissions(target_user_email);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log_permissions(action);

-- Trigger para actualizar updated_at automáticamente
CREATE TRIGGER IF NOT EXISTS update_user_timestamp 
AFTER UPDATE ON user_permissions
FOR EACH ROW
BEGIN
    UPDATE user_permissions 
    SET updated_at = datetime('now')
    WHERE user_email = NEW.user_email;
END;

-- Insertar usuario admin inicial
INSERT OR IGNORE INTO user_permissions (user_email, role, created_by)
VALUES ('admin@yourcompany.com', 'admin_full', 'SYSTEM');
```

**Ejecutar:**
```bash
sqlite3 permissions.db < migrations/create_permissions_tables_sqlite.sql
```

---

#### **B. PostgreSQL Local (Producción On-Premise)**

```sql
-- migrations/create_permissions_tables_postgres.sql
-- Sistema de permisos con PostgreSQL

-- Tabla de usuarios y roles
CREATE TABLE IF NOT EXISTS user_permissions (
    id BIGSERIAL PRIMARY KEY,
    user_email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'SYSTEM',
    last_login TIMESTAMPTZ,
    CONSTRAINT valid_role CHECK (role IN ('admin_full', 'admin_export', 'analytics_viewer', 'user_basic'))
);

-- Tabla de auditoría
CREATE TABLE IF NOT EXISTS audit_log_permissions (
    id BIGSERIAL PRIMARY KEY,
    admin_email VARCHAR(255) NOT NULL,
    action VARCHAR(20) NOT NULL CHECK(action IN ('CREATE', 'UPDATE', 'DELETE', 'DEACTIVATE', 'REACTIVATE')),
    target_user_email VARCHAR(255) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),  -- IPv4 o IPv6
    user_agent TEXT,
    details JSONB,  -- Metadata en formato JSON
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para optimización
CREATE INDEX idx_user_role ON user_permissions(role);
CREATE INDEX idx_user_active ON user_permissions(is_active);
CREATE INDEX idx_user_email_lower ON user_permissions(LOWER(user_email));

CREATE INDEX idx_audit_timestamp ON audit_log_permissions(timestamp DESC);
CREATE INDEX idx_audit_admin ON audit_log_permissions(admin_email);
CREATE INDEX idx_audit_target ON audit_log_permissions(target_user_email);
CREATE INDEX idx_audit_action ON audit_log_permissions(action);

-- Índice GIN para búsquedas en JSONB
CREATE INDEX idx_audit_details ON audit_log_permissions USING GIN (details);

-- Function para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para updated_at
CREATE TRIGGER update_user_timestamp 
BEFORE UPDATE ON user_permissions 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- Insertar usuario admin inicial
INSERT INTO user_permissions (user_email, role, created_by)
VALUES ('admin@yourcompany.com', 'admin_full', 'SYSTEM')
ON CONFLICT (user_email) DO NOTHING;

-- Comentarios para documentación
COMMENT ON TABLE user_permissions IS 'Usuarios y roles del sistema';
COMMENT ON TABLE audit_log_permissions IS 'Log de auditoría de cambios en permisos';
COMMENT ON COLUMN audit_log_permissions.details IS 'Metadata adicional en formato JSON';
```

**Ejecutar:**
```bash
psql -U username -d database_name -f migrations/create_permissions_tables_postgres.sql
```

---

#### **C. MySQL/MariaDB (Alternativa)**

```sql
-- migrations/create_permissions_tables_mysql.sql
-- Sistema de permisos con MySQL/MariaDB

-- Tabla de usuarios y roles
CREATE TABLE IF NOT EXISTS user_permissions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(255) DEFAULT 'SYSTEM',
    last_login TIMESTAMP NULL,
    INDEX idx_user_role (role),
    INDEX idx_user_active (is_active),
    INDEX idx_user_email (user_email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de auditoría
CREATE TABLE IF NOT EXISTS audit_log_permissions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    admin_email VARCHAR(255) NOT NULL,
    action VARCHAR(20) NOT NULL,
    target_user_email VARCHAR(255) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_timestamp (timestamp DESC),
    INDEX idx_audit_admin (admin_email),
    INDEX idx_audit_target (target_user_email),
    INDEX idx_audit_action (action),
    CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'DEACTIVATE', 'REACTIVATE'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar usuario admin inicial
INSERT IGNORE INTO user_permissions (user_email, role, created_by)
VALUES ('admin@yourcompany.com', 'admin_full', 'SYSTEM');
```

**Ejecutar:**
```bash
mysql -u username -p database_name < migrations/create_permissions_tables_mysql.sql
```

---

### 9.6 Checklist de Adaptación a Nuevo Proyecto (New Project Adaptation Checklist)

> Usa esta checklist cuando implementes en un proyecto diferente

**Antes de Implementar:**

- [ ] **1. Analizar requisitos del proyecto**
  - ¿Qué roles necesitas?
  - ¿Qué permisos necesita cada rol?
  - ¿Usarás Supabase, SQLite, PostgreSQL o MySQL?

- [ ] **2. Configurar base de datos**
  - Supabase: Crear proyecto en supabase.com
  - SQLite: Ejecutar script SQL de migración
  - PostgreSQL: Configurar servidor y ejecutar script
  - MySQL: Configurar servidor y ejecutar script

- [ ] **3. Copiar archivos de Dashboard-Ventas-Backup**
  - `src/permissions_manager.py` (adaptar conexión a DB)
  - `src/audit_logger.py` (adaptar conexión a DB)
  - `templates/admin/*.html` (adaptar diseño)
  - `static/js/admin_users.js` (opcional)
  - `static/css/admin.css` (opcional)

- [ ] **4. Configurar variables de entorno**
  ```bash
  # Para Supabase
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=your-anon-key
  
  # Para SQLite
  PERMISSIONS_DB_PATH=permissions.db
  
  # Para PostgreSQL/MySQL
  DATABASE_URL=postgresql://user:pass@host:5432/dbname
  ```

- [ ] **5. Personalizar roles en config.py**
  ```python
  ROLE_PERMISSIONS = {
      # Adaptar según tu proyecto
      'role_name': ['permission1', 'permission2']
  }
  ```

**Durante la Implementación:**

- [ ] **6. Adaptar código de conexión**
  - Si usas Supabase: Usar código actual
  - Si usas SQLite: Ver ejemplos en sección 9.2
  - Si usas PostgreSQL/MySQL: Adaptar con psycopg2 o mysql-connector

- [ ] **7. Crear rutas en app.py**
  - Copiar rutas de app.py líneas 334-610
  - Adaptar según estructura de tu proyecto

- [ ] **8. Personalizar templates**
  - Adaptar a tu framework CSS (Bootstrap/Tailwind/Material)
  - Integrar con tu base.html existente
  - Personalizar mensajes y textos

- [ ] **9. Crear usuario admin inicial**
  ```python
  from src.permissions_manager import PermissionsManager
  pm = PermissionsManager()
  pm.add_user('admin@yourcompany.com', 'admin_full')
  ```

**Después de Implementar:**

- [ ] **10. Testing completo**
  - Tests unitarios de PermissionsManager
  - Tests de integración de rutas
  - Tests de seguridad

- [ ] **11. Documentar para tu equipo**
  - Roles disponibles
  - Procedimientos de altas/bajas
  - Políticas de seguridad

---

## 📚 Recursos Adicionales (Additional Resources)

**Documentación Relacionada:**
- Flask Documentation: https://flask.palletsprojects.com/
- Supabase Python Client: https://supabase.com/docs/reference/python
- SQLite Documentation: https://www.sqlite.org/docs.html
- PostgreSQL Documentation: https://www.postgresql.org/docs/

**Herramientas Recomendadas:**
- **Supabase Studio**: Panel visual para gestionar base de datos
- **DBeaver**: Cliente universal de bases de datos
- **pytest**: Framework de testing Python
- **Postman**: Testing de API endpoints

**Comandos Útiles:**

```bash
# Verificar seguridad del código
bandit -r src/

# Verificar vulnerabilidades en dependencias
safety check

# Ejecutar tests con coverage
pytest --cov=src tests/ -v

# Generar reporte HTML de coverage
pytest --cov=src --cov-report=html tests/

# Backup de SQLite
cp permissions.db permissions_backup_$(date +%Y%m%d).db

# Dump de PostgreSQL
pg_dump -U username database_name > backup.sql
```

---

**📌 Nota sobre Migración de Datos**:

Si ya tienes usuarios en otro sistema y necesitas importarlos:

1. Exporta usuarios a CSV
2. Usa script de migración (ver ejemplo en sección 9.3)
3. Verifica que todos los roles existen
4. Importa en lotes pequeños (100-500 usuarios)
5. Valida que la importación fue exitosa
6. Actualiza audit log con registro de importación masiva

---

### 9.1 Checklist de Adaptación a Nuevo Proyecto (New Project Adaptation Checklist)

**Antes de Implementar**:

- [ ] **1. Analizar requisitos del proyecto**
  - ¿Qué roles necesitas? (admin, editor, viewer, etc.)
  - ¿Qué permisos necesita cada rol?
  - ¿Usarás SQLite o PostgreSQL/MySQL?

- [ ] **2. Configurar variables de entorno**
  - Crear `.env` con dominios de email permitidos
  - Configurar SECRET_KEY segura
  - Definir timeout de sesiones

- [ ] **3. Personalizar roles en `config.py`**
  ```python
  ROLE_PERMISSIONS = {
      # Adaptar según tu proyecto
      'role_name': ['permission1', 'permission2']
  }
  ```

- [ ] **4. Adaptar validaciones**
  - Dominios de email corporativos
  - Reglas de contraseñas (si aplica)
  - Restricciones de roles

**Durante la Implementación**:

- [ ] **5. Crear estructura de carpetas**
  - `src/` para módulos Python
  - `templates/admin/` para vistas del módulo
  - `static/css/` y `static/js/` para assets

- [ ] **6. Instalar dependencias**
  ```bash
  pip install Flask Flask-WTF pydantic Flask-Limiter
  ```

- [ ] **7. Crear base de datos**
  - Ejecutar scripts SQL de creación
  - Agregar índices para performance

- [ ] **8. Implementar código base**
  - Copiar `permissions_manager.py`
  - Copiar `audit_logger.py`
  - Adaptar según necesidades específicas

- [ ] **9. Crear rutas Flask**
  - `/admin/users` (lista)
  - `/admin/users/add` (crear)
  - `/admin/users/edit/<email>` (editar)
  - `/admin/users/delete/<email>` (eliminar)
  - `/admin/audit-log` (auditoría)

- [ ] **10. Implementar templates**
  - Copiar templates de `templates/admin/`
  - Adaptar a tu diseño existente
  - Integrar con tu `base.html`

**Después de Implementar**:

- [ ] **11. Testing completo**
  - Tests unitarios de `PermissionsManager`
  - Tests unitarios de `AuditLogger`
  - Tests de integración de rutas
  - Tests de seguridad (intentos no autorizados)

- [ ] **12. Crear usuario admin inicial**
  ```python
  from src.permissions_manager import PermissionsManager
  pm = PermissionsManager()
  pm.add_user('admin@yourcompany.com', 'admin_full')
  ```

- [ ] **13. Documentar roles y permisos**
  - Crear documentación para tu equipo
  - Definir procedimientos de altas/bajas
  - Establecer políticas de seguridad

- [ ] **14. Configurar backups**
  - Backup automático de `permissions.db`
  - Exportación periódica de audit logs

### 9.2 Ejemplo de Adaptación por Tipo de Proyecto (Adaptation Examples by Project Type)

#### **Proyecto E-commerce**

```python
# config.py
ROLE_PERMISSIONS = {
    'super_admin': ['*'],  # Todos los permisos
    'warehouse_manager': [
        'view_orders',
        'update_inventory',
        'manage_shipments',
        'view_products'
    ],
    'customer_support': [
        'view_orders',
        'update_order_status',
        'create_refunds',
        'view_customers'
    ],
    'marketing': [
        'view_analytics',
        'manage_promotions',
        'view_customers'
    ],
    'viewer': ['view_orders', 'view_products']
}

ROLE_DISPLAY_NAMES = {
    'super_admin': 'Super Administrador',
    'warehouse_manager': 'Gerente de Almacén',
    'customer_support': 'Soporte al Cliente',
    'marketing': 'Marketing',
    'viewer': 'Solo Lectura'
}
```

#### **Proyecto CRM**

```python
# config.py
ROLE_PERMISSIONS = {
    'admin_full': ['*'],
    'sales_director': [
        'view_all_leads',
        'manage_team',
        'view_analytics',
        'export_reports',
        'edit_forecasts'
    ],
    'sales_manager': [
        'view_team_leads',
        'manage_leads',
        'view_team_analytics',
        'export_own_data'
    ],
    'sales_rep': [
        'view_own_leads',
        'create_leads',
        'update_own_leads',
        'view_own_analytics'
    ],
    'analyst': [
        'view_all_data',
        'export_reports',
        'view_analytics'
    ]
}
```

#### **Proyecto de Gestión de Contenido**

```python
# config.py
ROLE_PERMISSIONS = {
    'admin': ['*'],
    'editor_chief': [
        'create_content',
        'edit_all_content',
        'publish_content',
        'manage_authors',
        'view_analytics'
    ],
    'editor': [
        'create_content',
        'edit_own_content',
        'publish_own',
        'view_analytics'
    ],
    'author': [
        'create_content',
        'edit_own_content',
        'submit_for_review'
    ],
    'reviewer': [
        'view_all_content',
        'comment_content',
        'approve_content'
    ]
}
```

### 9.3 Personalización de Componentes (Component Customization)

#### **A. Personalizar Validaciones de Email**

```python
# src/permissions_manager.py

import re
from typing import List

class PermissionsManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.allowed_domains = self.config.get(
            'ALLOWED_EMAIL_DOMAINS',
            ['@yourcompany.com']
        )
    
    def validate_email(self, email: str) -> tuple[bool, str]:
        """
        Valida email según reglas del proyecto.
        
        Returns:
            (is_valid, error_message)
        """
        # Formato básico
        if not re.match(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', email):
            return False, 'Formato de email inválido'
        
        # Dominio permitido
        if not any(email.endswith(domain) for domain in self.allowed_domains):
            return False, f'Solo se permiten dominios: {", ".join(self.allowed_domains)}'
        
        # Bloquear emails de prueba (opcional)
        if 'test' in email or 'temp' in email:
            return False, 'No se permiten emails de prueba'
        
        return True, ''
```

#### **B. Agregar Campos Personalizados**

```python
# Si necesitas campos adicionales como departamento, ubicación, etc.

# SQL Migration
"""
ALTER TABLE user_permissions 
ADD COLUMN department TEXT DEFAULT 'General';

ALTER TABLE user_permissions 
ADD COLUMN location TEXT DEFAULT 'Headquarters';

ALTER TABLE user_permissions 
ADD COLUMN phone_extension TEXT;
"""

# Actualizar PermissionsManager
class PermissionsManager:
    def add_user(self, email: str, role: str, 
                 department: str = None, 
                 location: str = None,
                 phone_extension: str = None) -> bool:
        """Crear usuario con campos personalizados"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_permissions 
                    (user_email, role, department, location, phone_extension, created_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (email, role, department, location, phone_extension))
                return True
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
```

#### **C. Integración con Sistemas Externos**

```python
# src/ldap_integration.py (ejemplo)

import ldap
from src.permissions_manager import PermissionsManager

class LDAPIntegration:
    """Sincronizar usuarios desde LDAP/Active Directory"""
    
    def __init__(self, ldap_server, base_dn):
        self.server = ldap_server
        self.base_dn = base_dn
        self.pm = PermissionsManager()
    
    def sync_users_from_ldap(self):
        """Importar usuarios desde LDAP"""
        conn = ldap.initialize(self.server)
        
        # Buscar usuarios
        results = conn.search_s(
            self.base_dn,
            ldap.SCOPE_SUBTREE,
            '(objectClass=person)'
        )
        
        for dn, entry in results:
            email = entry.get('mail', [None])[0]
            if email:
                # Determinar rol según grupo LDAP
                role = self._determine_role(entry)
                
                # Crear si no existe
                if not self.pm.get_user_role(email):
                    self.pm.add_user(email, role)
        
        conn.unbind()
    
    def _determine_role(self, ldap_entry):
        """Mapear grupos LDAP a roles de la aplicación"""
        groups = ldap_entry.get('memberOf', [])
        
        if b'CN=Admins,OU=Groups' in groups:
            return 'admin_full'
        elif b'CN=Managers,OU=Groups' in groups:
            return 'manager'
        else:
            return 'user_basic'
```

### 9.4 Despliegue en Diferentes Entornos (Deployment Environments)

#### **Desarrollo Local**

```bash
# .env.development
FLASK_ENV=development
FLASK_DEBUG=True
PERMISSIONS_DB_PATH=permissions_dev.db
ALLOWED_EMAIL_DOMAINS=@test.com,@dev.com
SECRET_KEY=dev-secret-key-change-me
```

#### **Staging**

```bash
# .env.staging
FLASK_ENV=staging
FLASK_DEBUG=False
PERMISSIONS_DB_PATH=/var/data/permissions_staging.db
ALLOWED_EMAIL_DOMAINS=@yourcompany.com
SECRET_KEY=staging-secret-key-from-vault
ADMIN_RATE_LIMIT_PER_HOUR=20
```

#### **Producción**

```bash
# .env.production
FLASK_ENV=production
FLASK_DEBUG=False

# PostgreSQL en producción
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Dominios corporativos únicamente
ALLOWED_EMAIL_DOMAINS=@yourcompany.com

# Secret key desde gestor de secretos
SECRET_KEY=${VAULT_SECRET_KEY}

# Rate limiting estricto
ADMIN_RATE_LIMIT_PER_HOUR=10

# Sesiones seguras
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### 9.5 Migración desde Otro Sistema (Migration from Other Systems)

#### **Script de Migración desde CSV**

```python
# migrate_users.py

import csv
from src.permissions_manager import PermissionsManager
from src.audit_logger import AuditLogger

def migrate_from_csv(csv_file_path, admin_email='system@import'):
    """
    Importar usuarios desde CSV.
    
    CSV Format:
    email,role,department,location
    user1@company.com,admin_full,IT,HQ
    user2@company.com,user_basic,Sales,Branch1
    """
    pm = PermissionsManager()
    audit = AuditLogger()
    
    imported = 0
    skipped = 0
    errors = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            email = row['email'].strip().lower()
            role = row['role'].strip()
            
            # Validar rol
            if role not in pm.ROLE_PERMISSIONS:
                errors.append(f"Rol inválido para {email}: {role}")
                skipped += 1
                continue
            
            # Verificar si ya existe
            if pm.get_user_role(email):
                print(f"Usuario ya existe: {email}, omitiendo...")
                skipped += 1
                continue
            
            # Importar
            try:
                department = row.get('department')
                location = row.get('location')
                
                pm.add_user(email, role, department, location)
                audit.log_user_created(admin_email, email, role, 'CSV Import')
                imported += 1
                print(f"✓ Importado: {email} ({role})")
            except Exception as e:
                errors.append(f"Error importando {email}: {e}")
                skipped += 1
    
    print(f"\n=== Resumen de Importación ===")
    print(f"Importados: {imported}")
    print(f"Omitidos: {skipped}")
    print(f"Errores: {len(errors)}")
    
    if errors:
        print("\nErrores:")
        for error in errors:
            print(f"  - {error}")

if __name__ == '__main__':
    migrate_from_csv('users_to_import.csv')
```

### 9.6 Troubleshooting Común (Common Troubleshooting)

#### **Problema 1: Error "No module named 'src'"**

```python
# Solución: Agregar al inicio de app.py
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))
```

#### **Problema 2: Base de datos bloqueada (SQLite)**

```python
# Solución: Usar timeout y WAL mode
import sqlite3

conn = sqlite3.connect(
    'permissions.db',
    timeout=30.0,  # Esperar 30 segundos si está bloqueada
    check_same_thread=False
)

# Activar Write-Ahead Logging para mejor concurrencia
conn.execute('PRAGMA journal_mode=WAL')
```

#### **Problema 3: Sesiones no persisten tras reiniciar**

```python
# Solución: Configurar secret key fija
# config.py
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-dev-key'

# NO usar valores aleatorios que cambien en cada reinicio
```

#### **Problema 4: CSRF token missing**

```python
# Solución en app.py
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# En templates con AJAX
<meta name="csrf-token" content="{{ csrf_token() }}">

// En JavaScript
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
fetch('/admin/users/delete/user@test.com', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken
    }
});
```

### 9.7 Recursos Adicionales (Additional Resources)

**Documentación Relacionada**:
- Flask Security Best Practices: https://flask.palletsprojects.com/en/latest/security/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Flask-Login Documentation: https://flask-login.readthedocs.io/

**Herramientas Recomendadas**:
- **Bandit**: Análisis de seguridad Python
- **Safety**: Verificar vulnerabilidades en dependencias
- **pytest**: Framework de testing
- **Faker**: Generar datos de prueba

**Comandos Útiles**:
```bash
# Verificar seguridad del código
bandit -r src/

# Verificar vulnerabilidades en dependencias
safety check

# Ejecutar tests
pytest tests/ -v

# Generar coverage report
pytest --cov=src tests/
```

---

## 📞 Soporte y Contacto (Support & Contact)

Para consultas sobre implementación:
- **Documentación completa**: Este documento
- **Ejemplos de código**: Secciones 4 y 5
- **Tests de referencia**: Sección 7
- **Guía de portabilidad**: Sección 9

**Contribuciones**:
Si implementas mejoras o adaptaciones útiles, considera documentarlas para futuros proyectos.

---

**📌 Nota Final**: Este plan está diseñado para ser **altamente portable**. Adapta los roles, permisos y validaciones según las necesidades específicas de tu proyecto. La arquitectura modular permite implementar solo las partes que necesites.
