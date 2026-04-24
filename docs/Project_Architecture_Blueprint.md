# Plano de Arquitectura del Proyecto (Project Architecture Blueprint)
## Dashboard de Ventas Farmacéuticas - Documentación Integral de Arquitectura (Comprehensive Architecture Documentation)

**Generado (Generated):** 21 de abril de 2026  
**Proyecto (Project):** Dashboard de Ventas Farmacéuticas  
**Versión (Version):** 2.1  
**Stack Tecnológico (Technology Stack):** Python/Flask, Odoo ERP, Supabase, PostgreSQL/SQLite  
**Última Actualización:** Dashboard de Seguridad y Auditoría completa (Abril 2026)

---

## 1. Resumen Ejecutivo (Executive Summary)

El Dashboard de Ventas Farmacéuticas es una aplicación web empresarial construida con Flask que integra datos de Odoo ERP para proporcionar visualizaciones analíticas de ventas, gestión de metas, y métricas de desempeño del equipo comercial. La aplicación implementa una arquitectura en capas (Layered Architecture) con separación clara de responsabilidades entre presentación, lógica de negocio, y acceso a datos.

### Características Principales (Key Features)
- **Integración ERP**: Conexión en tiempo real con Odoo mediante JSON-RPC (migrado desde XML-RPC en Marzo 2026)
- **Gestión de Metas**: Sistema de metas de ventas con Supabase como backend
- **Analytics Integrado**: Sistema de monitoreo de uso y adopción del dashboard
- **Autenticación Corporativa**: OAuth2 con Google Workspace + timeout dual de sesión (15 min inactividad + 8h absoluto)
- **Exportación de Datos**: Generación de reportes Excel con formato profesional
- **Control de Permisos**: Sistema granular de permisos por rol y funcionalidad (PermissionsManager con Supabase)
- **Auditoría Completa**: Sistema de auditoría de login/logout + cambios de permisos (AuditLogger con Supabase) - **NUEVO Abril 2026**
- **Dashboard de Seguridad**: Visualización de métricas de seguridad con gráficas Chart.js, alertas de riesgo - **NUEVO Abril 2026**
- **Seguridad Robusta**: Headers de seguridad (CSP, HSTS), protección SQL injection, validación de inputs, timezone Peru (UTC-5)
- **Cumplimiento Normativo**: Alineado con ISO 27001, OWASP, PCI-DSS, GDPR, SOC 2 - **NUEVO Abril 2026**

---

## 2. Detección y Análisis de Arquitectura (Architecture Detection and Analysis)

### 2.1 Detección del Stack Tecnológico (Technology Stack Detection)

#### Framework Backend (Backend Framework)
```python
Flask==3.1.3          # Web framework principal
Werkzeug==3.1.6       # WSGI utility library
gunicorn==23.0.0      # Production WSGI server
```

#### Autenticación y Seguridad (Authentication & Security)
```python
Authlib==1.6.7        # OAuth2 implementation
python-dotenv==1.1.1  # Environment configuration
```

#### Capa de Datos (Data Layer)
```python
psycopg2-binary==2.9.10  # PostgreSQL adapter
supabase==2.14.0         # Supabase client for metas
pandas==2.2.3            # Data processing
openpyxl==3.1.5          # Excel export
```

#### Capa de Integración (Integration Layer)
```python
requests==2.32.5      # HTTP client for Odoo JSON-RPC
```

### 2.2 Análisis de Patrones Arquitectónicos (Architectural Pattern Analysis)

El proyecto implementa **Layered Architecture** con las siguientes capas:

1. **Presentation Layer** (`templates/`, `static/`)
   - Templates Jinja2 para renderizado server-side
   - Assets estáticos (CSS, JavaScript, imágenes)
   - Componentes reutilizables (base.html)

2. **Application Layer** (`app.py`)
   - Flask routes y endpoints
   - Request handling y response formatting
   - Middleware (analytics, authentication)
   - Session management

3. **Business Logic Layer** (`src/`)
   - Managers especializados por dominio
   - Transformación y agregación de datos
   - Reglas de negocio y validaciones

4. **Data Access Layer** (`src/*_manager.py`)
   - Abstracción de acceso a Odoo
   - Cliente Supabase para metas
   - Database abstraction (SQLite/PostgreSQL)

5. **Infrastructure Layer** (Configuration)
   - Environment variables (.env)
   - OAuth2 configuration
   - Database connection management

---

## 3. Visión General de la Arquitectura (Architectural Overview)

### 3.1 Principios Fundamentales (Core Principles)

1. **Separation of Concerns**
   - Cada manager gestiona un dominio específico (Odoo, Supabase, Analytics)
   - Templates separados por funcionalidad
   - Configuración centralizada en variables de entorno

2. **Single Responsibility**
   - `OdooManager`: Exclusivamente integración con Odoo ERP
   - `SupabaseManager`: Gestión de metas de ventas
   - `AnalyticsDB`: Monitoreo y estadísticas de uso

3. **Dependency Injection**
   - Managers instanciados como singletons en app.py
   - Inyección explícita en contextos de request

4. **Fail-Safe Design**
   - Modo offline si Odoo no está disponible
   - Fallback a SQLite si PostgreSQL falla
   - Stub managers para evitar crashes

5. **Environment-Based Configuration**
   - Todas las credenciales y configuraciones en `.env`
   - Ejemplos en `.env.example` para onboarding
   - Separación dev/staging/production

### 3.2 Límites Arquitectónicos (Architectural Boundaries)

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser (Client)                  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS
                         ↓
┌─────────────────────────────────────────────────────────┐
│               Flask Application (app.py)                 │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Routes & Middleware                                │ │
│  │  - OAuth2 Authentication                            │ │
│  │  - Session Management                               │ │
│  │  - Analytics Tracking                               │ │
│  └────────────────────────────────────────────────────┘ │
└────────┬────────────────┬────────────────┬──────────────┘
         │                │                │
         ↓                ↓                ↓
┌────────────────┐ ┌─────────────┐ ┌──────────────────┐
│  OdooManager   │ │ Supabase    │ │  AnalyticsDB     │
│                │ │ Manager     │ │                  │
│ - Sales Data   │ │ - Metas     │ │ - Page Visits    │
│ - Products     │ │ - Goals     │ │ - User Stats     │
│ - Customers    │ │ - Teams     │ │ - Adoption       │
└───────┬────────┘ └──────┬──────┘ └────────┬─────────┘
        │                  │                  │
        ↓                  ↓                  ↓
┌───────────────┐  ┌──────────────┐  ┌────────────────┐
│  Odoo ERP     │  │  Supabase    │  │  PostgreSQL/   │
│  (JSON-RPC)   │  │  (REST API)  │  │  SQLite        │
└───────────────┘  └──────────────┘  └────────────────┘
```

---

## 4. Componentes Arquitectónicos Principales (Core Architectural Components)

### 4.1 OdooManager - Capa de Integración ERP (ERP Integration Layer)

**Purpose**: Proporciona una abstracción completa sobre la API JSON-RPC de Odoo para consultas de datos de ventas, productos, clientes y operaciones comerciales. Migrado desde XML-RPC en Marzo 2026 para mejor rendimiento y evitar bugs en módulos de auditoría.

**Internal Structure**:
```python
class OdooManager:
    # Connection attributes
    self.url                  # Odoo instance URL
    self.db                   # Database name
    self.username             # API user
    self.password             # API password
    self.uid                  # Authenticated user ID
    self.models               # JSON-RPC proxy
    self.rpc_timeout          # Request timeout (30s default)
    self.jsonrpc_url          # Full JSON-RPC endpoint
    
    # Core methods
    __init__()                           # Authentication & connection setup
    _create_jsonrpc_models_proxy()       # Compatibility wrapper
    authenticate_user(user, pwd)         # User validation
    get_sales_lines(filters)             # Main data retrieval
    get_filter_options()                 # UI filter data
    get_all_sellers()                    # Sales team info
    get_commercial_lines_stacked_data()  # Charting aggregations
```

**Key Responsibilities**:
1. **Authentication Management**
   - JSON-RPC authentication via `/jsonrpc` endpoint
   - Session management con UID persistente
   - Credenciales desde variables de entorno
   - Graceful degradation a modo offline

2. **Data Retrieval**
   - Consultas RPC a modelos Odoo (`sale.order.line`, `product.product`, etc.)
   - Filtrado complejo con múltiples dimensiones (fecha, cliente, línea, vendedor)
   - Paginación y límites configurables
   - Timeout handling robusto

3. **Data Transformation**
   - Conversión de many2one Odoo `[id, name]` a diccionarios Python
   - Agregaciones por línea comercial, categoría, cliente
   - Cálculos de cumplimiento de metas
   - Formateo para visualizaciones (ECharts, tablas)

**Interaction Patterns**:
```python
# Dependency Injection en app.py
data_manager = OdooManager()

# Usage en routes con error handling
@app.route('/dashboard')
def dashboard():
    # El manager ya está autenticado o en modo offline
    sales_lines = data_manager.get_sales_lines(
        date_from='2026-01-01',
        date_to='2026-01-31',
        limit=5000
    )
    # Procesamiento adicional...
```

**Evolution & Extension Points**:
- **Nuevas entidades**: Agregar métodos `get_<model>()` siguiendo el patrón existente
- **Filtros adicionales**: Extender parámetros en `get_sales_lines()`
- **Agregaciones custome**: Nuevos métodos de transformación como `get_commercial_lines_stacked_data()`
- **Caching**: Potencial integración de Redis/Memcached para reducir llamadas RPC
- **JSON-RPC Benefits**: Payloads 30% más pequeños vs XML-RPC, mejor para debugging

**Design Patterns Utilized**:
- **Facade Pattern**: Simplifica la API compleja de Odoo JSON-RPC
- **Proxy Pattern**: `JSONRPCModelsProxy` para mantener compatibilidad
- **Null Object Pattern**: Stub manager cuando Odoo no está disponible

---

### 4.2 SupabaseManager - Gestión de Metas y Objetivos (Goals & Targets Management)

**Purpose**: Gestiona el sistema de metas de ventas (targets) almacenadas en Supabase, reemplazando el sistema legacy de Google Sheets.

**Internal Structure**:
```python
class SupabaseManager:
    self.supabase: Client    # Supabase client instance
    self.enabled: bool       # Connection status flag
    
    # Metas Generales
    guardar_meta_venta()
    obtener_metas_mes()
    obtener_meta_especifica()
    eliminar_meta()
    obtener_todas_metas()
    
    # Metas por Vendedor
    guardar_meta_vendedor()
    obtener_metas_vendedor_mes()
    eliminar_meta_vendedor()
    obtener_todas_metas_vendedores()
    obtener_metas_vendedor_linea()
    
    # Equipos de Ventas
    obtener_equipos_ventas()
    actualizar_equipo_ventas()
    guardar_equipo_ventas()
```

**Key Responsibilities**:
1. **CRUD Operations on Sales Targets**
   - Metas mensuales por línea comercial
   - Metas IPN (Introducción de Productos Nuevos)
   - Metas individuales por vendedor

2. **Data Consistency**
   - Upsert operations (on_conflict='mes,linea_comercial')
   - Timestamp tracking (`updated_at`)
   - Normalización de strings (UPPER() para líneas)

3. **Query Optimization**
   - Indexed queries por mes y línea
   - Ordenamiento consistente
   - Filtrado eficiente

**Interaction Patterns**:
```python
# Initialization con fallback
supabase_manager = SupabaseManager()

# Conditional execution basado en enabled flag
if supabase_manager.enabled:
    metas = supabase_manager.obtener_metas_mes('2026-01')
else:
    metas = []  # Default empty state
```

**Data Schema** (Supabase tables):
```sql
-- metas_ventas_2026
CREATE TABLE metas_ventas_2026 (
    id SERIAL PRIMARY KEY,
    mes TEXT NOT NULL,  -- 'YYYY-MM'
    linea_comercial TEXT NOT NULL,
    meta_total NUMERIC NOT NULL,
    meta_ipn NUMERIC,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(mes, linea_comercial)
);

-- metas_vendedores_2026  
CREATE TABLE metas_vendedores_2026 (
    id SERIAL PRIMARY KEY,
    mes TEXT NOT NULL,
    vendedor_nombre TEXT NOT NULL,
    linea_comercial TEXT NOT NULL,
    meta_venta NUMERIC NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(mes, vendedor_nombre, linea_comercial)
);

-- equipos_ventas_2026
CREATE TABLE equipos_ventas_2026 (
    id SERIAL PRIMARY KEY,
    vendedor_nombre TEXT UNIQUE NOT NULL,
    equipo TEXT NOT NULL,
    cargo TEXT,
    activo BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Evolution Patterns**:
- **Nuevas tablas anuales**: Patrón `metas_ventas_YYYY` versionado por año
- **Campos adicionales**: Extensible vía alter table sin breaking changes
- **Validaciones**: Business rules en métodos Python, no en DB

---

### 4.3 AnalyticsDB - Monitoreo de Uso y Métricas (Usage Monitoring & Metrics)

**Purpose**: Sistema interno de telemetría que rastrea el uso del dashboard para medir adopción, identificar páginas populares, y detectar problemas de UX.

**Internal Structure**:
```python
class AnalyticsDB:
    self.database_url        # PostgreSQL connection string (prod)
    self.db_path             # SQLite path (dev)
    self.use_sqlite          # Boolean flag para DB selection
    self.enabled             # Analytics system status
    
    # Connection Management
    @contextmanager get_connection()
    _init_database()
    
    # Core Operations
    registrar_visita()
    obtener_stats_totales()
    obtener_visitas_por_usuario()
    obtener_visitas_por_dia()
    obtener_visitas_por_hora()
    obtener_visitas_recientes()
```

**Key Responsibilities**:
1. **Usage Tracking**
   - Page visits con timestamp
   - User session tracking
   - Referrer y user-agent logging
   - IP address capture (opcional)

2. **Aggregated Metrics**
   - Total visits por período
   - Unique users count
   - Page popularity ranking
   - Temporal patterns (día/hora)

3. **Database Abstraction**
   - Dual-mode: PostgreSQL (prod) / SQLite (dev)
   - Context manager para connection pooling
   - Automatic table creation
   - Graceful error handling

**Database Schema**:
```sql
CREATE TABLE page_visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    user_name TEXT,
    page_url TEXT NOT NULL,
    page_title TEXT,
    visit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_duration INTEGER DEFAULT 0,
    ip_address TEXT,
    user_agent TEXT,
    referrer TEXT,
    method TEXT
);

CREATE INDEX idx_user_email ON page_visits(user_email);
CREATE INDEX idx_visit_timestamp ON page_visits(visit_timestamp);
CREATE INDEX idx_page_url ON page_visits(page_url);
```

**Interaction via Middleware**:
```python
@app.before_request
def before_request():
    """Captura tiempo de inicio de request"""
    g.start_time = datetime.now()

@app.after_request
def after_request(response):
    """Registra visita después de procesar"""
    if 'username' in session and response.status_code == 200:
        if session.get('username') not in excluded_users:
            if not request.path.startswith('/static/'):
                analytics_db.registrar_visita(
                    user_email=session['username'],
                    user_name=session.get('name'),
                    page_url=request.path,
                    page_title=page_titles.get(request.path, request.path),
                    method=request.method,
                    user_agent=request.headers.get('User-Agent'),
                    referrer=request.referrer
                )
    return response
```

**Privacy Considerations**:
- Usuarios específicos pueden ser excluidos (`excluded_users` list)
- Static assets no generan registros
- No tracking de query parameters (evita exponer datos sensibles)

---

### 4.4 PermissionsManager - Control de Acceso Granular (Granular Access Control)

**Purpose**: Sistema centralizado de control de acceso basado en roles (RBAC) que reemplaza las listas hardcodeadas dispersas en el código. Implementado en Marzo 2026 para mejorar seguridad y mantenibilidad. **Migrado a Supabase en Abril 2026** para consistencia con audit_log_permissions.

**Internal Structure**:
```python
class PermissionsManager:
    self.supabase             # Supabase client instance
    self.enabled              # Availability flag
    
    # Core methods
    __init__()                          # Initialize Supabase client
    add_user(email, role, name)        # User registration
    remove_user(email)                  # User deactivation
    update_user_role(email, new_role)  # Role modification
    check_permission(email, feature)    # Permission validation
    get_user_role(email)                # Role lookup
    get_user_details(email)             # Complete user info
    list_users()                        # All active users enumeration
    get_all_roles()                     # Available roles
```

**Role Definitions**:
```python
ROLES = {
    'admin_full': [
        'view_dashboard', 'view_sales', 'view_analytics',
        'edit_metas', 'edit_vendedor_metas', 'edit_equipos',
        'export_sales', 'export_dashboard', 'admin_users',
        'admin_audit_log'  # Nuevo: acceso a dashboard de seguridad
    ],
    'admin_export': [
        'view_dashboard', 'view_sales',
        'export_sales', 'export_dashboard'
    ],
    'analytics_viewer': [
        'view_dashboard', 'view_sales', 'view_analytics'
    ],
    'user_basic': [
        'view_dashboard', 'view_sales'
    ]
}
```

**Database Schema** (Supabase):
```sql
CREATE TABLE user_permissions (
    id SERIAL PRIMARY KEY,
    user_email TEXT UNIQUE NOT NULL,
    user_name TEXT,
    role TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_email ON user_permissions(user_email);
CREATE INDEX idx_role ON user_permissions(role);
CREATE INDEX idx_is_active ON user_permissions(is_active);
```

**Usage Pattern**:
```python
# Initialize manager (singleton)
permissions_manager = PermissionsManager()

# Check permission in route
@app.route('/export/sales')
def export_sales():
    if not permissions_manager.check_permission(
        session['username'], 
        'export_sales'
    ):
        flash('No tienes permiso...', 'danger')
        return redirect(url_for('dashboard'))
    # Proceed with export...
```

**Migration from Legacy**:
```python
# Migrated from hardcoded lists
admin_full_users = ['jonathan.cerda@...', 'janet.hueza@...', ...]
admin_export_users = ['juana.lovaton@...', ...]

# To database-driven permissions
permissions_manager.migrate_from_lists(
    admin_full_users, 
    admin_export_users,
    analytics_viewers
)
```

**Benefits**:
- **Centralized**: Un solo punto de definición de permisos
- **Auditable**: Cambios registrados con timestamps
- **Flexible**: Roles y permisos modificables sin deployment
- **Scalable**: Soporte para múltiples roles y permisos granulares
- **Testable**: Lógica de permisos aislada y testeable

**Security Improvements** (OWASP):
- Elimina duplicación de listas admin (Tech Debt resuelto)
- Principio de privilegio mínimo por rol
- Auditoría de cambios de permisos (vía AuditLogger)
- Separación de concerns (autorización vs autenticación)
- Migración a Supabase para mejor escalabilidad

---

### 4.4.1 AuditLogger - Sistema de Auditoría Completa (Complete Audit System) - **NUEVO Abril 2026**

**Purpose**: Sistema integral de auditoría que registra todos los eventos de autenticación (login/logout) y cambios de permisos, cumpliendo con estándares ISO 27001, OWASP, PCI-DSS, GDPR y SOC 2.

**Internal Structure**:
```python
class AuditLogger:
    self.supabase             # Supabase client instance
    self.enabled              # Availability flag
    
    # Authentication Event Logging
    log_login_success(user_email, user_name, role, ip_address, 
                     user_agent, oauth_provider, session_id)
    log_login_failed(attempted_email, ip_address, user_agent, 
                    failure_reason, error_message)
    log_logout(user_email, ip_address, session_duration, 
              logout_type, session_id)
    log_session_timeout(user_email, timeout_type, last_activity, ip_address)
    
    # Permission Change Logging
    log_user_created(admin_email, user_email, user_name, role, 
                    ip_address, user_agent)
    log_user_updated(admin_email, user_email, old_role, new_role, 
                    ip_address, user_agent)
    log_user_deleted(admin_email, user_email, ip_address, user_agent)
    log_user_deactivated(admin_email, user_email, ip_address, user_agent)
    log_user_reactivated(admin_email, user_email, ip_address, user_agent)
    
    # Security Analytics
    get_security_stats(hours=24)           # Métricas de seguridad
    get_login_timeline(hours=24)           # Timeline de eventos
    get_recent_failed_attempts(limit=10)   # Intentos fallidos
    
    # Permission Analytics
    get_filtered_logs(days, action, admin_email, exclude_auth_events)
    get_statistics()                        # Estadísticas generales
    get_user_history(user_email)           # Historial de usuario
```

**Database Schema** (Supabase):
```sql
CREATE TABLE audit_log_permissions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    admin_email TEXT NOT NULL,            -- Usuario que realizó la acción
    action TEXT NOT NULL,                 -- LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, 
                                         -- SESSION_TIMEOUT, CREATE, UPDATE, DELETE, etc.
    target_user_email TEXT,              -- Usuario afectado
    old_value TEXT,                       -- Valor anterior (rol)
    new_value TEXT,                       -- Valor nuevo (rol)
    ip_address TEXT,                      -- IP del cliente
    user_agent TEXT,                      -- User agent del navegador
    details JSONB,                        -- Metadata adicional
    
    CONSTRAINT audit_log_permissions_action_check 
        CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'DEACTIVATE', 'ACTIVATE',
                         'LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT', 'SESSION_TIMEOUT'))
);

CREATE INDEX idx_audit_timestamp ON audit_log_permissions(timestamp);
CREATE INDEX idx_audit_admin_email ON audit_log_permissions(admin_email);
CREATE INDEX idx_audit_target_user ON audit_log_permissions(target_user_email);
CREATE INDEX idx_audit_action ON audit_log_permissions(action);
```

**Timezone Support** (Peru UTC-5):
```python
import pytz
PERU_TZ = pytz.timezone('America/Lima')
UTC_TZ = pytz.UTC

# Template filters en app.py
@app.template_filter('to_peru_time')
def to_peru_time(utc_timestamp_str):
    """Convierte UTC a 'DD/MM/YYYY HH:MM:SS' hora de Perú"""
    # ... conversión con pytz ...

@app.template_filter('to_peru_date')
def to_peru_date(utc_timestamp_str):
    """Convierte UTC a 'DD/MM/YYYY'"""

@app.template_filter('to_peru_time_only')
def to_peru_time_only(utc_timestamp_str):
    """Convierte UTC a 'HH:MM:SS'"""

@app.template_filter('role_display')
def role_display(role_code):
    """Convierte código de rol a nombre legible"""
```

**Security Event Types**:

1. **LOGIN_SUCCESS**: Login exitoso con OAuth2
   - Captura: email, nombre, rol, IP, user agent, provider, session_id
   - Permite correlación con LOGOUT vía session_id

2. **LOGIN_FAILED**: Intento fallido de autenticación
   - Captura: email intentado, IP, user agent, razón, error message
   - Alertas si >10 intentos desde misma IP

3. **LOGOUT**: Cierre de sesión manual
   - Captura: email, IP, duración de sesión, session_id
   - Calcula tiempo entre login y logout

4. **SESSION_TIMEOUT**: Timeout automático de sesión
   - Captura: email, tipo (inactivity/absolute), última actividad, IP
   - Dos tipos: 15 min inactividad o 8h absoluto

**Permission Event Types**:
- **CREATE**: Nuevo usuario agregado al sistema
- **UPDATE**: Cambio de rol de usuario existente
- **DELETE**: Usuario eliminado permanentemente
- **DEACTIVATE**: Usuario desactivado (soft delete)
- **ACTIVATE**: Usuario reactivado después de desactivación

**Usage Patterns**:

```python
# En route /authorize (login success)
from src.audit_logger import AuditLogger
audit_logger = AuditLogger()

audit_logger.log_login_success(
    user_email=user_info['email'],
    user_name=user_info.get('name'),
    role=user_role,
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent'),
    oauth_provider='google',
    session_id=session.sid  # Para correlación con logout
)

# En route /logout
session_duration = calculate_duration(
    session.get('login_time'),
    datetime.now()
)

audit_logger.log_logout(
    user_email=session['username'],
    ip_address=request.remote_addr,
    session_duration=session_duration,
    logout_type='manual',
    session_id=session.sid
)

# En verify_session_expiration() para timeouts
audit_logger.log_session_timeout(
    user_email=session['username'],
    timeout_type='inactivity',  # o 'absolute'
    last_activity=session.get('last_activity_time'),
    ip_address=request.remote_addr
)

# En route /admin/users/update para cambios de permisos
audit_logger.log_user_updated(
    admin_email=current_user,
    user_email=target_email,
    old_role=old_role,
    new_role=new_role,
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent')
)
```

**Security Dashboard Integration**:

El AuditLogger alimenta el **Dashboard de Seguridad** (`/admin/audit-log`) con:

1. **Métricas 24h** (Security Stats):
   - Login exitosos
   - Intentos fallidos
   - Logouts manuales
   - Timeouts de sesión
   - Tasa de éxito de autenticación
   - Top IPs con intentos fallidos
   - Usuarios activos

2. **Timeline Chart** (Chart.js):
   - Visualización horaria de eventos de autenticación
   - 4 datasets: login_success, login_failed, logout, timeout
   - Datos agrupados por hora en timezone Peru

3. **Tabla de Intentos Fallidos**:
   - Últimos 10 intentos fallidos
   - Detalle: timestamp, email, IP, razón, mensaje
   - Ordenados por timestamp descendente

4. **Tabla de Cambios de Permisos**:
   - Filtrado por período (7/30/90/365 días)
   - Filtrado por acción (CREATE, UPDATE, DELETE, etc.)
   - Badges con colores por rol
   - Timestamps en hora de Perú

**Compliance Benefits**:
- ✅ **ISO 27001**: Trazabilidad completa de accesos
- ✅ **OWASP A01**: Auditoría de autenticación
- ✅ **PCI-DSS Req 10**: Logging de eventos de seguridad
- ✅ **GDPR Art 30**: Registro de actividades de tratamiento
- ✅ **SOC 2**: Control de acceso y monitoreo

**Design Patterns**:
- **Repository Pattern**: Abstracción de acceso a Supabase
- **Observer Pattern**: Eventos registrados en cada acción
- **Strategy Pattern**: Diferentes estrategias de logging por tipo de evento

---

### 4.5 Núcleo de la Aplicación Flask (Flask Application Core) - app.py

**Purpose**: Punto de entrada principal que orquesta todos los componentes, define routes, maneja autenticación y coordina el flujo de datos.

**Structure Breakdown**:

```python
# === Configuration & Initialization ===
load_dotenv()                    # Debe ejecutarse ANTES de imports
from src.odoo_manager import ... # Imports que requieren env vars

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

oauth = OAuth(app)
google = oauth.register(...)  # OAuth2 Google provider

# Manager instantiation
data_manager = OdooManager()
supabase_manager = SupabaseManager()
analytics_db = AnalyticsDB()

# === Middleware Stack ===
@app.before_request
@app.after_request
@app.context_processor

# === Route Definitions ===
# Authentication
@app.route('/login')
@app.route('/google_login')
@app.route('/authorize')
@app.route('/logout')

# Main Dashboards
@app.route('/dashboard')          # Dashboard principal con metas
@app.route('/dashboard_linea')    # Dashboard específico por línea
@app.route('/equipo_ventas')      # Vista de equipos

# Sales Targets Management
@app.route('/meta')               # Gestión de metas generales
@app.route('/metas_vendedor')     # Metas individuales

# Detailed Views
@app.route('/sales')              # Ventas farmacéuticas detalladas

# Analytics & Monitoring
@app.route('/analytics')          # Sistema de estadísticas interno

# Admin Module - User Management (NUEVO Abril 2026)
@app.route('/admin/users')                     # Lista de usuarios
@app.route('/admin/users/create')              # Crear nuevo usuario
@app.route('/admin/users/update/<email>')      # Actualizar rol de usuario
@app.route('/admin/users/delete/<email>')      # Eliminar usuario

# Admin Module - Security Audit (NUEVO Abril 2026)
@app.route('/admin/audit-log')                 # Dashboard de seguridad
                                               # - Tab 1: Métricas de seguridad (24h)
                                               # - Tab 2: Cambios de permisos

# Data Export
@app.route('/export/excel/sales')             # Exportar ventas
@app.route('/export/dashboard/details')       # Exportar dashboard
```

**Authorization Layers**:

1. **Session-based Authentication** (global):
```python
if 'username' not in session:
    return redirect(url_for('login'))
```

2. **Role-based Authorization** (con PermissionsManager - Actualizado Abril 2026):
```python
# Inicialización
from src.permissions_manager import PermissionsManager
permissions_manager = PermissionsManager()

# Decoradores para control de acceso
from functools import wraps

def require_admin_full(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        
        user_role = permissions_manager.get_user_role(session['username'])
        if user_role != 'admin_full':
            flash('Se requiere rol admin_full', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# Uso en routes
@app.route('/admin/users')
@require_admin_full
def admin_users():
    # Solo accesible por admin_full
    users = permissions_manager.list_users()
    return render_template('admin/users.html', users=users)
```

3. **Whitelist Validation** (en login):
```python
# Primero chequea allowed_users.json
with open('allowed_users.json', 'r') as f:
    allowed_data = json.load(f)
    allowed_emails = allowed_data.get('allowed_emails', [])

if email not in allowed_emails:
    flash('No tienes acceso autorizado...', 'danger')
    return render_template('login.html')
```

**Request Flow**:
```
1. User hits endpoint
   ↓
2. @before_request: g.start_time = now()
   ↓
3. Route handler execution
   ├─ Session check
   ├─ Permission check  
   ├─ Data retrieval (managers)
   ├─ Business logic
   └─ Template rendering
   ↓
4. @after_request: analytics registration
   ↓
5. Response to client
```

---

## 5. Capas Arquitectónicas y Dependencias (Architectural Layers and Dependencies)

### 5.1 Estructura de Capas (Layer Structure)

```
┌─────────────────────────────────────────────────────┐
│         PRESENTATION LAYER                          │
│  - Jinja2 Templates (templates/)                    │
│  - Static Assets (static/css, static/js)            │
│  - Client-side Charting (ECharts)                   │
└────────────────┬────────────────────────────────────┘
                 │ Template Context
                 ↓
┌─────────────────────────────────────────────────────┐
│         APPLICATION LAYER                           │
│  - Flask Routes (app.py)                            │
│  - Request/Response Handling                        │
│  - Session Management                               │
│  - Middleware (auth, analytics)                     │
└────────────────┬────────────────────────────────────┘
                 │ Manager Method Calls
                 ↓
┌─────────────────────────────────────────────────────┐
│         BUSINESS LOGIC LAYER                        │
│  - OdooManager (src/odoo_manager.py)                │
│  - SupabaseManager (src/supabase_manager.py)        │
│  - Data Transformations & Aggregations              │
│  - Business Rules & Validations                     │
└────────────────┬────────────────────────────────────┘
                 │ API Calls / Queries
                 ↓
┌─────────────────────────────────────────────────────┐
│         DATA ACCESS LAYER                           │
│  - JSON-RPC Client (requests)                       │
│  - Supabase Client (supabase-py)                    │
│  - AnalyticsDB (SQLite/PostgreSQL)                  │
└────────────────┬────────────────────────────────────┘
                 │ Network/DB Protocols
                 ↓
┌─────────────────────────────────────────────────────┐
│         EXTERNAL SYSTEMS                            │
│  - Odoo ERP (JSON-RPC over HTTPS)                   │
│  - Supabase (REST API over HTTPS)                   │
│  - PostgreSQL Database                              │
└─────────────────────────────────────────────────────┘
```

### 5.2 Reglas de Flujo de Dependencias (Dependency Flow Rules)

**Strict Rules**:
1. ✅ **Presentation → Application**: Templates pueden referenciar routes
2. ✅ **Application → Business Logic**: Routes llaman métodos de managers
3. ✅ **Business Logic → Data Access**: Managers usan clients/connections
4. ❌ **No circular dependencies**: Ninguna capa depende de capas superiores
5. ❌ **No presentation bypass**: Templates NO acceden directamente a data layer

**Dependency Injection Pattern**:
```python
# app.py - Singleton managers
data_manager = OdooManager()       # Inicializado una vez al startup
supabase_manager = SupabaseManager()
analytics_db = AnalyticsDB()

# Los managers son accedidos directamente en routes (no DI container formal)
@app.route('/dashboard')
def dashboard():
    # Uso directo del singleton
    sales_data = data_manager.get_sales_lines(...)
    metas = supabase_manager.obtener_metas_mes(...)
```

**Abstraction Mechanisms**:
- **Manager Classes**: Abstraen implementaciones específicas (JSON-RPC, Supabase SDK)
- **Fallback Patterns**: Stub managers cuando servicios no disponibles
- **Environment Configuration**: `.env` abstrae diferencias dev/staging/prod

### 5.3 Violaciones de Capas y Deuda Técnica (Layer Violations & Technical Debt)

**Identified Issues**:

1. ⚠️ **Business Logic in Routes** (app.py líneas 400-800)
   - Transformaciones de datos ocurren en route handlers
   - Debería moverse a métodos en managers
   ```python
   # ❌ Current: Business logic en route
   @app.route('/dashboard')
   def dashboard():
       sales_lines = data_manager.get_sales_lines(...)
       # 200+ líneas de transformación y cálculos aquí
       total_venta = sum(line['price_subtotal'] for line in sales_lines)
       ...
   
   # ✅ Mejor: Delegar a business layer
   @app.route('/dashboard')
   def dashboard():
       dashboard_data = data_manager.get_dashboard_summary(
           mes=mes, 
           año=año
       )
       return render_template('dashboard.html', **dashboard_data)
   ```

2. ⚠️ **Hardcoded Admin Lists** (múltiples líneas en app.py)
   ```python
   admin_users = ["jonathan.cerda@...", "janet.hueza@...", ...]
   ```
   - Debería estar en base de datos o archivo de configuración
   - Dificulta mantenimiento (aparece en ~10 lugares diferentes)

3. ⚠️ **Template Complexity** (dashboard_clean.html ~1000 líneas)
   - Lógica condicional compleja en templates
   - Candidato para componentización

**Refactoring Recommendations**:
- Extraer `PermissionManager` para centralizar ACL
- Crear `DashboardService` para lógica de negocio de dashboard
- Implementar Repository Pattern para queries complejas

---

## 6. Arquitectura de Datos (Data Architecture)

### 6.1 Visión General del Modelo de Dominio (Domain Model Overview)

El sistema maneja tres dominios principales de datos:

#### **Ventas (Sales Domain)**
Origen: Odoo ERP `sale.order.line`

```python
{
    'id': int,
    'order_id': [id, 'SO0123'],           # Many2one a sale.order
    'product_id': [id, 'Producto X'],     # Many2one a product.product
    'partner_id': [id, 'Cliente ABC'],    # Many2one a res.partner
    'date_order': '2026-01-15',
    'quantity': 100.0,
    'price_unit': 25.50,
    'price_subtotal': 2550.0,
    'user_id': [id, 'Vendedor'],         # Many2one a res.users
    'commercial_line_national_id': [id, 'AGROVET'],
    'pharmaceutical_forms_id': [id, 'Tabletas'],
    'categ_id': [id, 'Antibióticos'],
    'team_id': [id, 'Equipo Lima'],
    'state': 'sale',  # draft|sent|sale|done|cancel
    # ... más campos específicos del negocio
}
```

**Transformación típica**:
```python
# Odoo devuelve many2one como [id, name]
# El dashboard convierte a diccionarios planos

sales_line['cliente'] = sales_line['partner_id'][1] if sales_line['partner_id'] else 'Sin Cliente'
sales_line['producto'] = sales_line['product_id'][1] if sales_line['product_id'] else ''
```

#### **Metas (Goals Domain)**
Origen: Supabase `metas_ventas_2026`, `metas_vendedores_2026`

```python
# Meta General
{
    'id': 123,
    'mes': '2026-01',
    'linea_comercial': 'AGROVET',
    'meta_total': 1570000.0,
    'meta_ipn': 145000.0,
    'updated_at': '2026-01-15T10:30:00'
}

# Meta Individual
{
    'id': 456,
    'mes': '2026-01',
    'vendedor_nombre': 'Juan Portal',
    'linea_comercial': 'PETMEDICA',
    'meta_venta': 350000.0,
    'updated_at': '2026-01-15T10:30:00'
}
```

#### **Analytics Domain**
Origen: Local DB (SQLite/PostgreSQL) `page_visits`

```python
{
    'id': 789,
    'user_email': 'usuario@agrovetmarket.com',
    'user_name': 'Usuario Demo',
    'page_url': '/dashboard',
    'page_title': 'Dashboard de Ventas',
    'visit_timestamp': '2026-03-17T14:25:00',
    'session_duration': 0,
    'ip_address': '192.168.1.100',
    'user_agent': 'Mozilla/5.0...',
    'referrer': None,
    'method': 'GET'
}
```

#### **Audit & Permissions Domain** - **NUEVO Abril 2026**
Origen: Supabase `audit_log_permissions`, `user_permissions`

```python
# Registro de Auditoría (Authentication Event)
{
    'id': 1001,
    'timestamp': '2026-04-21T15:57:42.123456+00:00',
    'admin_email': 'jonathan.cerda@agrovetmarket.com',
    'action': 'LOGIN_SUCCESS',
    'target_user_email': 'jonathan.cerda@agrovetmarket.com',
    'old_value': None,
    'new_value': 'admin_full',  # Rol del usuario
    'ip_address': '190.237.45.123',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'details': {
        'name': 'Jonathan Cerda',
        'role': 'admin_full',
        'oauth_provider': 'google',
        'session_id': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        'timestamp_readable': '2026-04-21T10:57:42-05:00'
    }
}

# Registro de Auditoría (Permission Change)
{
    'id': 1002,
    'timestamp': '2026-03-24T21:46:09.876543+00:00',
    'admin_email': 'jonathan.cerda@agrovetmarket.com',
    'action': 'UPDATE',
    'target_user_email': 'teodoro.balarezo@agrovetmarket.com',
    'old_value': 'user_basic',
    'new_value': 'admin_export',
    'ip_address': '127.0.0.1',
    'user_agent': 'Mozilla/5.0...',
    'details': {
        'changed_by': 'Jonathan Cerda',
        'reason': 'Promotion to export role'
    }
}

# Permisos de Usuario
{
    'id': 42,
    'user_email': 'janet.hueza@agrovetmarket.com',
    'user_name': 'Janet Hueza',
    'role': 'admin_full',
    'is_active': True,
    'created_at': '2026-03-10T12:00:00',
    'updated_at': '2026-03-10T12:00:00'
}
```

**Tipos de Acciones (Action Types)**:
- **Autenticación**: `LOGIN_SUCCESS`, `LOGIN_FAILED`, `LOGOUT`, `SESSION_TIMEOUT`
- **Permisos**: `CREATE`, `UPDATE`, `DELETE`, `DEACTIVATE`, `ACTIVATE`

### 6.2 Patrones de Flujo de Datos (Data Flow Patterns)

#### **Read Flow (Dashboard)**
```
User Request
    ↓
Flask Route Handler
    ↓
OdooManager.get_sales_lines(filters)
    ↓
JSON-RPC Request a Odoo
    ↓
Odoo ejecuta domain filters
    ↓
Odoo devuelve recordset
    ↓
OdooManager transforma many2one
    ↓
Route calcula agregaciones
    ↓
Template renderiza con Jinja2
    ↓
Response HTML al cliente
```

#### **Write Flow (Guardar Meta)**
```
User Form Submission (POST)
    ↓
Flask Route Handler (@app.route('/meta', methods=['POST']))
    ↓
Extrae datos de request.form
    ↓
SupabaseManager.guardar_meta_venta(mes, linea, meta_total, meta_ipn)
    ↓
Supabase Client ejecuta upsert
    ↓
Supabase persiste en PostgreSQL
    ↓
Flash message de confirmación
    ↓
Redirect a página de metas
```

### 6.3 Patrones de Acceso a Datos (Data Access Patterns)

#### **Repository-like Pattern en OdooManager**
```python
class OdooManager:
    def get_sales_lines(self, date_from=None, date_to=None, 
                        partner_id=None, linea_id=None, limit=1000):
        """
        Encapsula query compleja a Odoo con domain filters
        """
        # Build Odoo domain (list of tuples)
        domain = [('state', 'in', ['sale', 'done'])]
        
        if date_from:
            domain.append(('date_order', '>=', date_from))
        if date_to:
            domain.append(('date_order', '<=', date_to))
        if partner_id:
            domain.append(('partner_id', '=', int(partner_id)))
            
        # Execute via JSON-RPC
        sales_lines = self.models.execute_kw(
            self.db, self.uid, self.password,
            'sale.order.line', 'search_read',
            [domain],
            {'fields': FIELDS_LIST, 'limit': limit, 'order': 'date_order desc'}
        )
        
        return sales_lines
```

#### **Active Record Pattern en SupabaseManager**
```python
def guardar_meta_venta(self, mes, linea_comercial, meta_total, meta_ipn):
    """
    Upsert directo usando Supabase SDK
    """
    data = {
        'mes': mes,
        'linea_comercial': linea_comercial.upper(),
        'meta_total': float(meta_total),
        'meta_ipn': float(meta_ipn) if meta_ipn else None,
        'updated_at': datetime.now().isoformat()
    }
    
    result = self.supabase.table('metas_ventas_2026')\
        .upsert(data, on_conflict='mes,linea_comercial')\
        .execute()
    
    return result.data[0] if result.data else None
```

### 6.4 Estrategias de Caché (Caching Strategies)

**Current State**: No caching implementado (todas las queries son en tiempo real)

**Opportunities for Optimization**:

1. **Odoo Data Caching**
   ```python
   # Potencial implementación con Redis
   def get_sales_lines_cached(self, date_from, date_to, ...):
       cache_key = f"sales:{date_from}:{date_to}:{partner_id}:{linea_id}"
       cached = redis_client.get(cache_key)
       
       if cached:
           return json.loads(cached)
       
       data = self.get_sales_lines(date_from, date_to, ...)
       redis_client.setex(cache_key, 300, json.dumps(data))  # 5 min TTL
       return data
   ```

2. **Filter Options Caching**
   - `get_filter_options()` devuelve listas de clientes y líneas
   - Cambia raramente → candidato para caching de 1 hora

3. **Metas Caching**
   - Metas mensuales no cambian frecuentemente
   - Cache de 15 minutos reduciría carga en Supabase

---

## 7. Implementación de Aspectos Transversales (Cross-Cutting Concerns Implementation)

### 7.1 Autenticación y Autorización (Authentication & Authorization)

#### **Session Timeout (Implementado Marzo 2026)**

```python
# Dual timeout system
MAX_IDLE_MINUTES = 15           # Inactivity timeout
MAX_ABSOLUTE_SESSION_HOURS = 8  # Absolute timeout from login

# Session tracking
session['login_time'] = datetime.now(UTC_TZ).isoformat()
session['last_activity_time'] = datetime.now(UTC_TZ).isoformat()

# Validation on each request
@app.before_request
def before_request():
    if not verify_session_expiration():
        session.clear()
        return redirect(url_for('login'))
    # Update activity timestamp
    session['last_activity_time'] = datetime.now(UTC_TZ).isoformat()
    session.modified = True
```

**Security Benefits**:
- Protege contra sesiones abandonadas (walk-away scenarios)
- Cumple OWASP A01 - Broken Authentication
- Configuración flexible por entorno (.env)

#### **OAuth2 Flow (Google Workspace)**

```python
# 1. Configuración del provider
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# 2. Inicio de sesión
@app.route('/google_login')
def google_login():
    redirect_uri = url_for('authorize', _external=True, _scheme='https')
    return google.authorize_redirect(redirect_uri)

# 3. Callback & token exchange
@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    email = user_info.get('email')
    name = user_info.get('name')
    
    # 4. Whitelist validation
    with open('allowed_users.json', 'r') as f:
        allowed_emails = json.load(f).get('allowed_emails', [])
    
    if email not in allowed_emails:
        flash('No tienes acceso autorizado', 'danger')
        return redirect(url_for('login'))
    
    # 5. Session creation
    session['username'] = email
    session['name'] = name
    session['authenticated'] = True
    
    return redirect(url_for('dashboard'))
```

#### **Permission Model** (Role-Based Access Control - Migrado a PermissionsManager Marzo 2026)

**Sistema Legacy** (deprecado):
```python
# Definición de roles (hardcoded en app.py - TECH DEBT RESUELTO)
ROLES = {
    'admin_full': [  # Todos los permisos
        'jonathan.cerda@agrovetmarket.com',
        'janet.hueza@agrovetmarket.com',
        'juan.portal@agrovetmarket.com',
    ],
    'admin_export': [  # Puede exportar datos
        'miguel.hernandez@agrovetmarket.com',
        'juana.lovaton@agrovetmarket.com',
        'jimena.delrisco@agrovetmarket.com',
    ]
}
```

**Sistema Actual** (PermissionsManager con SQLite):
```python
# Inicialización
permissions_manager = PermissionsManager()

# Migración desde listas hardcodeadas
permissions_manager.migrate_from_lists(admin_full_users, admin_export_users, [])

# Enforcement en routes (nuevo patrón)
@app.route('/export/dashboard/details')
def export_dashboard_details():
    if not permissions_manager.check_permission(
        session['username'], 
        'export_dashboard'
    ):
        flash('No tienes permiso para realizar esta acción.', 'warning')
        return redirect(url_for('dashboard'))
    # Proceed with export...
```

**Beneficios de la migración**:
- ✅ Permisos centralizados en base de datos
- ✅ Auditoría de cambios con timestamps
- ✅ Roles y permisos modificables sin deployment
- ✅ Elimina duplicación de listas en ~10 rutas

**Security Boundaries**:
1. **Perimeter**: OAuth2 con Google (autenticación corporativa)
2. **Application**: Whitelist en `allowed_users.json`
3. **Feature**: PermissionsManager con roles granulares (migrado Marzo 2026)
4. **Session**: Flask signed cookies + dual timeout (inactividad + absoluto)

#### **Security Headers (Implementado Marzo 2026)**

**Content Security Policy (CSP)**:
```python
@app.after_request
def add_security_headers(response):
    # CSP para prevenir XSS y controlar recursos externos
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com https://*.google.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "img-src 'self' data: https: blob:",
        "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "connect-src 'self' https://accounts.google.com https://*.google.com https://*.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "frame-src 'self' https://accounts.google.com https://*.google.com",
        "frame-ancestors 'self'",
        "base-uri 'self'",
        "form-action 'self' https://accounts.google.com"
    ]
    response.headers['Content-Security-Policy'] = "; ".join(csp_directives)
    
    # Otros headers de seguridad
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # HSTS solo en producción
    if os.getenv('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response
```

**Security Improvements** (OWASP Coverage):
- **A01 - Broken Authentication**: Timeout dual ✅
- **A03 - SQL Injection**: Queries parametrizadas ✅
- **A04 - Insecure Design**: Headers de seguridad ✅
- **A05 - Security Misconfiguration**: CSP configurado ✅

**Score Evolution**:
- SQL Injection (A03): 4/10 → 7/10 (6/6 queries corregidas)
- Security Headers (A04): 6/10 → 7/10 (7 headers implementados)
- Overall Security: 7.1/10 → 7.4/10

### 7.2 Manejo de Errores y Resiliencia (Error Handling & Resilience)

#### **Graceful Degradation Pattern**

```python
# OdooManager initialization con fallback
try:
    data_manager = OdooManager()
except Exception as e:
    print(f"⚠️ No se pudo inicializar OdooManager: {e}")
    
    class _StubManager:
        def get_filter_options(self):
            return {'lineas': [], 'clients': []}
        def get_sales_lines(self, *args, **kwargs):
            return []
        # ... stubs para todos los métodos públicos
    
    data_manager = _StubManager()
```

#### **Timeout Handling**

```python
class OdooManager:
    def __init__(self):
        self.rpc_timeout = int(os.getenv('ODOO_RPC_TIMEOUT', '30'))
        
        try:
            response = requests.post(
                self.jsonrpc_url,
                json=payload,
                headers=headers,
                timeout=self.rpc_timeout  # ← Configurable
            )
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout después de {self.rpc_timeout}s")
            self.uid = None
            self.models = None
```

#### **Database Fallback Strategy**

```python
class AnalyticsDB:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url or self.database_url == "":
            self.use_sqlite = True
            self.db_path = 'analytics.db'
            print("📊 Analytics: Usando SQLite local")
        else:
            self.use_sqlite = False
            print("📊 Analytics: Usando PostgreSQL")
    
    @contextmanager
    def get_connection(self):
        try:
            if self.use_sqlite:
                conn = sqlite3.connect(self.db_path)
            else:
                if not PSYCOPG2_AVAILABLE:
                    # Fallback automático
                    self.use_sqlite = True
                    conn = sqlite3.connect(self.db_path)
                else:
                    conn = psycopg2.connect(self.database_url)
            
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Error en conexión DB: {e}")
            raise
        finally:
            conn.close()
```

#### **User-Facing Error Messages**

```python
# Flash messages para feedback
try:
    result = supabase_manager.guardar_meta_venta(...)
    if result:
        flash('✅ Meta guardada exitosamente', 'success')
    else:
        flash('⚠️ No se pudo guardar la meta', 'warning')
except Exception as e:
    flash(f'❌ Error: {str(e)}', 'danger')
finally:
    return redirect(url_for('meta'))
```

### 7.3 Registro y Monitoreo (Logging & Monitoring)

#### **Application Logging**

```python
# Stdout logging (capturado por Gunicorn/systemd)
print("[OK] Conexión a Odoo establecida exitosamente.")
print("[ERROR] Advertencia: No se pudo autenticar.")
print(f"⚠️ Error durante authenticate(): {e}")
```

**Log Levels** (implementado via print prefixes):
- `[OK]` / `✅`: Operaciones exitosas
- `[ERROR]` / `❌`: Errores que requieren atención
- `⚠️`: Warnings recuperables
- `📊`: Mensajes informativos de analytics
- `⏱️`: Performance/timeout warnings

**Recommendation**: Migrar a `logging` module estándar:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Conexión a Odoo establecida")
logger.error("Autenticación falló", exc_info=True)
```

#### **Analytics as Monitoring**

El sistema de analytics funciona como Application Performance Monitoring (APM) básico:

```python
# Métricas disponibles vía /analytics
analytics_db.obtener_stats_totales(dias=30)
# → {'total_visitas': 1250, 'usuarios_unicos': 42, 'ratio_adopcion': 0.95}

analytics_db.obtener_visitas_por_pagina(dias=7)
# → [{'page_title': 'Dashboard', 'total_visitas': 450}, ...]

analytics_db.obtener_visitas_por_hora(dias=1)
# → [{'hora': 9, 'total_visitas': 35}, {'hora': 10, 'total_visitas': 52}, ...]
```

**Usage Insights Enabled**:
- Feature adoption tracking (qué páginas se usan más)
- User engagement (frecuencia de visitas por usuario)
- Time-of-day patterns (picos de uso)
- Dead features detection (páginas sin visitas)

### 7.4 Patrones de Validación (Validation Patterns)

#### **Input Validation (Forms)**

```python
@app.route('/meta', methods=['POST'])
def meta():
    # Extract form data
    mes = request.form.get('mes')
    linea_comercial = request.form.get('linea_comercial')
    meta_total = request.form.get('meta_total')
    meta_ipn = request.form.get('meta_ipn')
    
    # Basic validation
    if not all([mes, linea_comercial, meta_total]):
        flash('Todos los campos son obligatorios', 'danger')
        return redirect(url_for('meta'))
    
    try:
        meta_total = float(meta_total)
        meta_ipn = float(meta_ipn) if meta_ipn else None
    except ValueError:
        flash('Meta debe ser un número válido', 'danger')
        return redirect(url_for('meta'))
    
    # Business rule validation
    if meta_total < 0:
        flash('Meta no puede ser negativa', 'danger')
        return redirect(url_for('meta'))
    
    # Proceed with save...
```

#### **Data Normalization**

```python  
class SupabaseManager:
    def guardar_meta_venta(self, mes, linea_comercial, meta_total, meta_ipn):
        data = {
            'mes': mes,
            'linea_comercial': linea_comercial.upper(),  # ← Normalización
            'meta_total': float(meta_total),             # ← Type casting
            'meta_ipn': float(meta_ipn) if meta_ipn else None,  # ← Null handling
            'updated_at': datetime.now().isoformat()
        }
```

### 7.5 Gestión de Configuración (Configuration Management)

#### **Environment Variables (.env)**

```bash
# Odoo ERP Connection
ODOO_URL=https://amah-test.odoo.com
ODOO_DB=amah-staging-29683881
ODOO_USER=jonathan.cerda@agrovetmarket.com
ODOO_PASSWORD=secure_password_here
ODOO_RPC_TIMEOUT=30

# Flask Secret
SECRET_KEY=random_secret_key_32_chars

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Supabase (Metas)
SUPABASE_URL=https://project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5...

# Google OAuth2
GOOGLE_CLIENT_ID=405410518889-xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxx

# Flask Environment
FLASK_ENV=development

# Session Security (Implementado Marzo 2026)
ENABLE_SESSION_EXPIRATION=true
MAX_IDLE_MINUTES=15
MAX_ABSOLUTE_SESSION_HOURS=8

# Logging
LOG_LEVEL=INFO
```

#### **Configuration Loading Order**

```python
# app.py línea 1-6 (CRÍTICO: orden importa)
from dotenv import load_dotenv
import os

# ⚠️ DEBE ejecutarse ANTES de importar managers
load_dotenv()

# Ahora es seguro importar (los managers usan env vars en __init__)
from src.odoo_manager import OdooManager
```

**Problema conocido**: Import order dependency + BOM UTF-8 en .env  
**Solución 1**: Mover `load_dotenv()` antes de todos los imports que requieran env vars  
**Solución 2**: Asegurar que .env esté en UTF-8 sin BOM (causó problemas en Marzo 2026)

#### **Secret Management**

**Archivos sensibles en `.gitignore`**:
```gitignore
.env
credentials.json
allowed_users.json
security_reports/
datos_reporte_ceo.json
```

**Ejemplos para onboarding**:
- `.env.example`: Template sin valores reales
- `allowed_users.json.example`: Estructura del whitelist

---

## 8. Patrones de Comunicación entre Servicios (Service Communication Patterns)

### 8.1 Integración Odoo ERP (JSON-RPC) (Odoo ERP Integration - JSON-RPC)

**Protocol**: JSON-RPC 2.0 over HTTPS

**Endpoint Structure**:
```
https://{ODOO_URL}/jsonrpc
```

**Authentication Flow**:
```json
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",
        "method": "authenticate",
        "args": [database, username, password, {}]
    },
    "id": 1
}

// Response
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": 74  // UID del usuario autenticado
}
```

**Data Query Pattern** (search_read):
```json
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "object",
        "method": "execute_kw",
        "args": [
            "amah-staging-29683881",  // database
            74,                        // uid
            "password",               // password
            "sale.order.line",        // model
            "search_read",            // method
            [                         // domain filters
                ["state", "in", ["sale", "done"]],
                ["date_order", ">=", "2026-01-01"],
                ["date_order", "<=", "2026-01-31"]
            ],
            {                         // options
                "fields": ["id", "partner_id", "product_id", ...],
                "limit": 1000,
                "order": "date_order desc"
            }
        ]
    },
    "id": 2
}
```

**Resilience Patterns**:
- ✅ **Timeout Configurables**: `ODOO_RPC_TIMEOUT=30`
- ✅ **Retry Logic**: No implementado (oportunidad de mejora)
- ✅ **Circuit Breaker**: No formal, pero modo offline actúa como fallback
- ✅ **Connection Pooling**: Requests library maneja pool automáticamente

**Error Handling**:
```python
try:
    response = requests.post(url, json=payload, timeout=timeout)
    result = response.json()
    
    if "result" in result and result["result"]:
        return result["result"]
    else:
        print("❌ Advertencia: resultado inesperado")
        return None
        
except requests.exceptions.Timeout:
    print(f"⏱️ Timeout después de {timeout}s")
    return None
    
except requests.exceptions.ConnectionError:
    print("🔌 Error de conexión a Odoo")
    return None
    
except Exception as e:
    print(f"⚠️ Error: {e}")
    return None
```

### 8.2 Integración Supabase (REST API) (Supabase Integration - REST API)

**Protocol**: REST over HTTPS (PostgREST)

**Client SDK**: `supabase-py` (abstrae REST calls)

**Query Patterns**:

```python
# SELECT with filters
result = self.supabase.table('metas_ventas_2026')\
    .select('*')\
    .eq('mes', '2026-01')\
    .order('linea_comercial')\
    .execute()

data = result.data  # List of dicts

# UPSERT (insert or update)
result = self.supabase.table('metas_ventas_2026')\
    .upsert(data, on_conflict='mes,linea_comercial')\
    .execute()

# DELETE
result = self.supabase.table('metas_ventas_2026')\
    .delete()\
    .eq('id', 123)\
    .execute()
```

**Authentication**: API Key (anon key) en headers automáticamente

```python
self.supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')  # Anon key para RLS
)
```

**Row Level Security (RLS)**:
- Configurado en Supabase dashboard
- Políticas para operaciones CRUD basadas en roles
- API key determina permisos

### 8.3 PostgreSQL/SQLite (Analytics)

**Abstraction**: Context manager pattern

```python
@contextmanager
def get_connection(self):
    conn = None
    try:
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
        else:
            conn = psycopg2.connect(self.database_url)
        
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
```

**Usage**:
```python
def registrar_visita(self, user_email, page_url, ...):
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO page_visits (user_email, page_url, ...)
            VALUES (?, ?, ...)
        """, (user_email, page_url, ...))
```

**Database Portability**:
- SQL compatible con ambos: SQLite y PostgreSQL
- Parámetros posicionales (`?` en SQLite, `%s` en psycopg2) - potencial issue
- Schema idéntico en ambas plataformas

---

## 9. Patrones Arquitectónicos de Python (Python Architectural Patterns)

### 9.1 Organización de Módulos (Module Organization)

```
dashboard-ventas/
├── app.py                    # Application entry point
├── src/                      # Business logic modules
│   ├── __init__.py          # Package marker
│   ├── odoo_manager.py      # Odoo integration
│   ├── supabase_manager.py  # Supabase client
│   └── analytics_db.py      # Analytics database
├── templates/               # Jinja2 templates
├── static/                  # Static assets
├── docs/                    # Documentation
└── venv/                    # Virtual environment (gitignored)
```

**Import Structure**:
```python
# Absolute imports
from src.odoo_manager import OdooManager
from src.supabase_manager import SupabaseManager

# Standard library
from datetime import datetime, timedelta
from contextlib import contextmanager

# Third-party
from flask import Flask, render_template, ...
import pandas as pd
```

### 9.2 Patrones de Implementación OOP (OOP Implementation Patterns)

#### **Manager Pattern** (Service Layer)

```python
class OdooManager:
    """
    Encapsula toda la lógica de integración con Odoo ERP.
    
    Responsabilidades:
    - Autenticación JSON-RPC
    - Queries a modelos Odoo
    - Transformación de datos Odoo→Python
    """
    
    def __init__(self):
        # Setup: autenticación y conexión
        self.url = os.getenv('ODOO_URL')
        self.db = os.getenv('ODOO_DB')
        self.username = os.getenv('ODOO_USER')
        self.password = os.getenv('ODOO_PASSWORD')
        self.uid = None
        self.models = None
        
        # Authenticate on instantiation
        self._authenticate()
    
    def _authenticate(self):
        # Private method (convention, no enforcement)
        ...
    
    def get_sales_lines(self, **filters):
        # Public API method
        ...
```

**Design Patterns**:
- ✅ **Facade**: Simplifica API compleja de Odoo
- ✅ **Singleton-like**: Instanciado una vez en app.py
- ✅ **Factory Method**: `_create_jsonrpc_models_proxy()` crea proxy dinámico

#### **Context Manager Pattern**

```python
class AnalyticsDB:
    @contextmanager
    def get_connection(self):
        """
        Garantiza que las conexiones siempre se cierren,
        incluso si ocurre una excepción.
        """
        conn = None
        try:
            conn = self._create_connection()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def registrar_visita(self, ...):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(...)
```

### 9.3 Patrones Específicos de Flask (Flask-Specific Patterns)

#### **Application Factory Pattern** (Simplified)

```python
# app.py no usa factory formal, pero sigue principios similares

# Configuration
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Extensions registration
oauth = OAuth(app)
google = oauth.register(...)

# Manager initialization
data_manager = OdooManager()
supabase_manager = SupabaseManager()
analytics_db = AnalyticsDB()

# Blueprint-like organization (implicit)
# Routes agrupadas por dominio:
#   - Authentication routes
#   - Dashboard routes
#   - Export routes
#   - Analytics routes
```

**Recommendation**: Refactor a Application Factory formal:
```python
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    oauth.init_app(app)
    
    # Register blueprints
    from .dashboards import dashboards_bp
    from .exports import exports_bp
    app.register_blueprint(dashboards_bp)
    app.register_blueprint(exports_bp)
    
    return app
```

#### **Request Lifecycle Hooks**

```python
@app.before_request
def before_request():
    """Ejecutado antes de cada request"""
    g.start_time = datetime.now()

@app.after_request
def after_request(response):
    """Ejecutado después de cada request (si exitoso)"""
    if 'username' in session:
        analytics_db.registrar_visita(...)
    return response

@app.context_processor
def inject_user():
    """Inyecta variables en todos los templates"""
    return {
        'current_user': session.get('name', ''),
        'is_authenticated': session.get('authenticated', False)
    }
```

#### **Route Organization Pattern**

```python
# Pattern: Decorador → Handler → Lógica → Template
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # 1. Authentication check
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # 2. Permission check
    admin_users = [...]
    is_admin = session.get('username') in admin_users
    
    # 3. Data retrieval
    sales_lines = data_manager.get_sales_lines(...)
    metas = supabase_manager.obtener_metas_mes(...)
    
    # 4. Business logic / transformations
    totales = calcular_totales(sales_lines)
    cumplimiento = calcular_cumplimiento(totales, metas)
    
    # 5. Template rendering
    return render_template('dashboard.html',
                         totales=totales,
                         cumplimiento=cumplimiento,
                         is_admin=is_admin)
```

### 9.4 Patrones de Procesamiento de Datos (Data Processing Patterns)

#### **Pandas Integration**

```python
# Conversión Odoo data → DataFrame (no usado extensivamente, pero disponible)
import pandas as pd

def analizar_ventas(sales_lines):
    df = pd.DataFrame(sales_lines)
    
    # Transformations
    df['date_order'] = pd.to_datetime(df['date_order'])
    df['mes'] = df['date_order'].dt.to_period('M')
    
    # Aggregations
    ventas_por_mes = df.groupby('mes')['price_subtotal'].sum()
    
    return ventas_por_mes.to_dict()
```

#### **List Comprehensions & Generators**

```python
# Transformación eficiente de listas
ventas_con_cliente = [
    {
        **line,
        'cliente_nombre': line['partner_id'][1] if line['partner_id'] else 'Sin Cliente'
    }
    for line in sales_lines
    if line['state'] in ['sale', 'done']
]

# Generator para procesamiento bajo memoria (no usado actualmente)
def procesar_ventas_stream(sales_lines):
    for line in sales_lines:
        if line['state'] == 'sale':
            yield transformar_linea(line)
```

### 9.5 Patrones de Manejo de Errores (Error Handling Patterns)

#### **Try-Except-Finally Pattern**

```python
def guardar_meta_venta(self, mes, linea_comercial, meta_total, meta_ipn):
    try:
        data = self._preparar_data(mes, linea_comercial, meta_total, meta_ipn)
        result = self.supabase.table('metas_ventas_2026')\
            .upsert(data, on_conflict='mes,linea_comercial')\
            .execute()
        
        print(f"✅ Meta guardada: {linea_comercial} - {mes}")
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"❌ Error guardando meta: {e}")
        return None
```

#### **Fallback Pattern con Stub Objects**

```python
try:
    data_manager = OdooManager()
except Exception as e:
    print(f"⚠️ No se pudo inicializar OdooManager: {e}")
    
    class _StubManager:
        """
        Stub que implementa la misma interfaz que OdooManager
        pero devuelve datos vacíos en lugar de crashear.
        """
        def get_filter_options(self):
            return {'lineas': [], 'clients': []}
        
        def get_sales_lines(self, *args, **kwargs):
            return []
        
        def get_all_sellers(self):
            return []
    
    data_manager = _StubManager()
```

---

## 10. Patrones de Implementación (Implementation Patterns)

### 10.1 Patrones de Diseño de Interfaces (Interface Design Patterns)

**Implicit Interfaces** (Python duck typing):

```python
# OdooManager y _StubManager comparten interface implícita
class OdooManager:
    def get_sales_lines(self, date_from=None, ...): ...
    def get_filter_options(self): ...
    def get_all_sellers(self): ...

class _StubManager:
    def get_sales_lines(self, *args, **kwargs): return []
    def get_filter_options(self): return {'lineas': [], 'clients': []}
    def get_all_sellers(self): return []

# Ambos son intercambiables sin herencia
data_manager = OdooManager() if odoo_available else _StubManager()
```

**Formal Interfaces** (recommendation para mejorar):
```python
from abc import ABC, abstractmethod

class IDataProvider(ABC):
    @abstractmethod
    def get_sales_lines(self, filters: dict) -> List[dict]:
        pass
    
    @abstractmethod
    def get_filter_options(self) -> dict:
        pass

class OdooManager(IDataProvider):
    def get_sales_lines(self, filters): ...
    def get_filter_options(self): ...
```

### 10.2 Patrones de Implementación de Servicios (Service Implementation Patterns)

#### **Patrón: Inicialización con Validación**

```python
class OdooManager:
    def __init__(self):
        # 1. Load configuration
        self.url = os.getenv('ODOO_URL')
        self.db = os.getenv('ODOO_DB')
        self.username = os.getenv('ODOO_USER')
        self.password = os.getenv('ODOO_PASSWORD')
        
        # 2. Validate required configuration
        if not all([self.url, self.db, self.username, self.password]):
            missing = [var for var, val in [
                ('ODOO_URL', self.url),
                ('ODOO_DB', self.db),
                ('ODOO_USER', self.username),
                ('ODOO_PASSWORD', self.password)
            ] if not val]
            raise ValueError(f"Variables faltantes: {', '.join(missing)}")
        
        # 3. Initialize defaults
        try:
            self.rpc_timeout = int(os.getenv('ODOO_RPC_TIMEOUT', '30'))
        except Exception:
            self.rpc_timeout = 30
        
        # 4. Establish connection
        self._authenticate()
```

#### **Patrón: Método Privado para Setup Complejo**

```python
def _create_jsonrpc_models_proxy(self):
    """
    Factory method que crea un proxy wrapper
    para mantener compatibilidad con API de xmlrpc.client
    """
    class JSONRPCModelsProxy:
        def __init__(self, manager):
            self.manager = manager
        
        def execute_kw(self, db, uid, password, model, method, args, kwargs=None):
            if kwargs is None:
                kwargs = {}
            
            headers = {"Content-Type": "application/json"}
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [db, uid, password, model, method, args, kwargs]
                },
                "id": 1
            }
            
            response = requests.post(
                self.manager.jsonrpc_url,
                json=payload,
                headers=headers,
                timeout=self.manager.rpc_timeout
            )
            result = response.json()
            
            return result.get("result") if "result" in result else None
    
    return JSONRPCModelsProxy(self)
```

### 10.3 Patrones de Implementación de Repositorio (Repository Implementation Patterns)

**Query Builder Pattern** (en OdooManager):

```python
def get_sales_lines(self, date_from=None, date_to=None, 
                    partner_id=None, linea_id=None, limit=1000):
    """
    Construye domain filters dinámicamente basado en parámetros
    """
    # Base domain
    domain = [('state', 'in', ['sale', 'done'])]
    
    # Add filters conditionally
    if date_from:
        domain.append(('date_order', '>=', date_from))
    if date_to:
        domain.append(('date_order', '<=', date_to))
    if partner_id:
        domain.append(('partner_id', '=', int(partner_id)))
    if linea_id:
        domain.append(('commercial_line_national_id', '=', int(linea_id)))
    
    # Execute query
    sales_lines = self.models.execute_kw(
        self.db, self.uid, self.password,
        'sale.order.line', 'search_read',
        [domain],
        {
            'fields': self._get_required_fields(),
            'limit': limit,
            'order': 'date_order desc'
        }
    )
    
    return sales_lines
```

**Active Record Style** (SupabaseManager):

```python
def obtener_meta_especifica(self, mes, linea_comercial):
    """
    Consulta directa con query builder de Supabase
    """
    result = self.supabase.table('metas_ventas_2026')\
        .select('*')\
        .eq('mes', mes)\
        .eq('linea_comercial', linea_comercial.upper())\
        .execute()
    
    return result.data[0] if result.data else None
```

### 10.4 Patrones de Implementación de Controlador/API (Controller/API Implementation Patterns)

**Resource-Oriented Routes**:

```python
# Dashboard resource
@app.route('/dashboard', methods=['GET'])         # READ
@app.route('/dashboard_linea', methods=['GET'])   # READ (filtered)

# Metas resource
@app.route('/meta', methods=['GET'])              # READ (list)
@app.route('/meta', methods=['POST'])             # CREATE/UPDATE
@app.route('/meta/delete', methods=['POST'])      # DELETE

# Export resource (actions on other resources)
@app.route('/export/dashboard/details', methods=['GET'])
@app.route('/export/excel/sales', methods=['GET'])
```

**Patrón: POST-Redirect-GET (PRG)**

```python
@app.route('/meta', methods=['POST'])
def meta_post():
    # 1. Process form submission
    mes = request.form.get('mes')
    linea = request.form.get('linea_comercial')
    meta_total = float(request.form.get('meta_total'))
    
    # 2. Perform action
    result = supabase_manager.guardar_meta_venta(mes, linea, meta_total)
    
    # 3. Flash message
    if result:
        flash('✅ Meta guardada exitosamente', 'success')
    else:
        flash('⚠️ Error al guardar meta', 'warning')
    
    # 4. Redirect (previene duplicate submission en refresh)
    return redirect(url_for('meta'))
```

**Response Formatting** (Excel Export):

```python
@app.route('/export/dashboard/details')
def export_dashboard_details():
    # 1. Permission check
    if not is_admin:
        flash('No tienes permiso', 'warning')
        return redirect(url_for('dashboard'))
    
    # 2. Data retrieval
    sales_lines = data_manager.get_sales_lines(...)
    
    # 3. Transform to DataFrame
    df = pd.DataFrame(sales_lines)
    
    # 4. Generate Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Detalle Ventas', index=False)
        
        # Apply formatting
        workbook = writer.book
        worksheet = writer.sheets['Detalle Ventas']
        _aplicar_formato_odoo(worksheet)
    
    output.seek(0)
    
    # 5. Return file response
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'dashboard_detalle_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )
```

### 10.5 Implementación del Modelo de Dominio (Domain Model Implementation)

**Data Transfer Object (DTO) Pattern** (implicit):

```python
# Odoo devuelve datos como diccionarios
# El sistema los usa directamente sin crear clases
sale_line = {
    'id': 12345,
    'partner_id': [456, 'Cliente ABC'],
    'product_id': [789, 'Producto X'],
    'price_subtotal': 2500.0,
    ...
}

# Transformación para template
sale_line_dto = {
    'id': sale_line['id'],
    'cliente': sale_line['partner_id'][1] if sale_line['partner_id'] else '',
    'producto': sale_line['product_id'][1] if sale_line['product_id'] else '',
    'total': sale_line['price_subtotal'],
}
```

**Recommendation**: Crear dataclasses para tipado fuerte:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SaleLine:
    id: int
    cliente: str
    producto: str
    total: float
    fecha: str
    linea_comercial: Optional[str] = None
    
    @classmethod
    def from_odoo(cls, odoo_data: dict):
        return cls(
            id=odoo_data['id'],
            cliente=odoo_data['partner_id'][1] if odoo_data['partner_id'] else '',
            producto=odoo_data['product_id'][1] if odoo_data['product_id'] else '',
            total=odoo_data['price_subtotal'],
            fecha=odoo_data['date_order'],
            linea_comercial=odoo_data['commercial_line_national_id'][1] 
                if odoo_data.get('commercial_line_national_id') else None
        )
```

---

## 11. Arquitectura de Pruebas (Testing Architecture)

### 11.1 Estado Actual (Current State)

**Test Files Existentes**:
```
test_odoo_jsonrpc.py     # Tests de integración con Odoo JSON-RPC
test_quick.py            # Test rápido de conexión
src/test_*.py            # Tests de componentes individuales
```

**Testing Strategy** (actual):
- ❌ No hay tests unitarios comprehensivos
- ✅ Tests de integración manuales para Odoo
- ✅ Tests de configuración (environment variables)
- ❌ No hay tests automatizados en CI/CD

### 11.2 Arquitectura de Pruebas Recomendada (Recommended Testing Architecture)

#### **Unit Tests** (a implementar)

```python
# tests/unit/test_supabase_manager.py
import unittest
from unittest.mock import Mock, patch
from src.supabase_manager import SupabaseManager

class TestSupabaseManager(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        
    @patch('src.supabase_manager.create_client')
    def test_guardar_meta_venta_success(self, mock_create_client):
        mock_create_client.return_value = self.mock_client
        self.mock_client.table.return_value.upsert.return_value.execute.return_value.data = [
            {'id': 1, 'mes': '2026-01', 'linea_comercial': 'AGROVET'}
        ]
        
        manager = SupabaseManager()
        result = manager.guardar_meta_venta('2026-01', 'agrovet', 100000, 10000)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['linea_comercial'], 'AGROVET')
```

#### **Integration Tests**

```python
# tests/integration/test_odoo_integration.py
import unittest
from src.odoo_manager import OdooManager

class TestOdooIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = OdooManager()
    
    def test_authentication(self):
        self.assertIsNotNone(self.manager.uid)
        self.assertIsNotNone(self.manager.models)
    
    def test_get_sales_lines(self):
        sales = self.manager.get_sales_lines(
            date_from='2026-01-01',
            date_to='2026-01-31',
            limit=10
        )
        
        self.assertIsInstance(sales, list)
        if sales:
            self.assertIn('partner_id', sales[0])
            self.assertIn('price_subtotal', sales[0])
```

#### **End-to-End Tests**

```python
# tests/e2e/test_dashboard_flow.py
import unittest
from flask import session
from app import app

class TestDashboardFlow(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
    
    def test_login_required(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_with_auth(self):
        with self.client.session_transaction() as sess:
            sess['username'] = 'test@agrovetmarket.com'
            sess['authenticated'] = True
        
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
```

### 11.3 Estrategias de Datos de Prueba (Test Data Strategies)

**Fixtures** (recommended):
```python
# tests/fixtures.py
SAMPLE_SALE_LINE = {
    'id': 12345,
    'partner_id': [100, 'Cliente Test'],
    'product_id': [200, 'Producto Test'],
    'price_subtotal': 1500.0,
    'date_order': '2026-01-15',
    'state': 'sale'
}

SAMPLE_META = {
    'mes': '2026-01',
    'linea_comercial': 'AGROVET',
    'meta_total': 1570000.0,
    'meta_ipn': 145000.0
}
```

---

## 12. Arquitectura de Despliegue (Deployment Architecture)

### 12.1 Topología de Despliegue (Deployment Topology)

```
┌─────────────────────────────────────────────────┐
│            Production Environment                │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │    Load Balancer / Reverse Proxy         │  │
│  │           (Nginx/Caddy)                  │  │
│  └────────────────┬─────────────────────────┘  │
│                   │                              │
│  ┌────────────────▼─────────────────────────┐  │
│  │     Gunicorn WSGI Server                 │  │
│  │     Workers: 4                            │  │
│  │     Threads: 2                            │  │
│  └────────────────┬─────────────────────────┘  │
│                   │                              │
│  ┌────────────────▼─────────────────────────┐  │
│  │     Flask Application                     │  │
│  │     (app.py + src/)                       │  │
│  └───┬──────────┬──────────┬────────────┬───┘  │
│      │          │          │            │       │
└──────┼──────────┼──────────┼────────────┼───────┘
       │          │          │            │
       ↓          ↓          ↓            ↓
  ┌────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
  │ Odoo   │ │Supabase │ │PostgreSQL│ │ Google   │
  │ ERP    │ │  API    │ │(Analytics)│ │  OAuth2  │
  └────────┘ └─────────┘ └──────────┘ └──────────┘
```

### 12.2 Configuración de Entornos (Environment Configuration)

**Development** (.env.dev):
```bash
FLASK_ENV=development
ODOO_URL=https://amah-test.odoo.com
DATABASE_URL=  # Empty = SQLite fallback
DEBUG=True
```

**Staging** (.env.staging):
```bash
FLASK_ENV=production
ODOO_URL=https://amah-test.odoo.com
DATABASE_URL=postgresql://user:pass@staging-db:5432/analytics
DEBUG=False
```

**Production** (.env.prod):
```bash
FLASK_ENV=production
ODOO_URL=https://amah.odoo.com
ODOO_DB=amah-main-9110254
DATABASE_URL=postgresql://user:pass@prod-db:5432/analytics
SECRET_KEY=producción_secret_key_32_chars
DEBUG=False
```

### 12.3 Lista de Verificación de Despliegue (Deployment Checklist)

**Pre-Deployment**:
- [ ] All tests passing
- [ ] Environment variables configuradas en servidor
- [ ] `allowed_users.json` actualizado
- [ ] Migraciones de DB ejecutadas
- [ ] Supabase tables creadas
- [ ] Google OAuth2 redirect URIs configurados
- [ ] SSL/TLS certificados instalados

**Deployment Commands** (ejemplo para servidor Linux):
```bash
# 1. Pull latest code
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install/update dependencies
pip install -r requirements.txt

# 4. Run database migrations (si aplica)
# python migrate.py

# 5. Restart Gunicorn service
sudo systemctl restart gunicorn-dashboard-ventas

# 6. Check logs
sudo journalctl -u gunicorn-dashboard-ventas -f
```

**Gunicorn Configuration** (gunicorn.conf.py):
```python
bind = "0.0.0.0:8000"
workers = 4
threads = 2
worker_class = "gthread"
timeout = 120
keepalive = 5
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

### 12.4 Containerización (Docker - Recomendado) (Containerization - Docker Recommended)

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
    env_file:
      - .env
    depends_on:
      - postgres
    volumes:
      - ./allowed_users.json:/app/allowed_users.json:ro
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: analytics
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web

volumes:
  postgres_data:
```

---

## 13. Patrones de Extensión y Evolución (Extension and Evolution Patterns)

### 13.1 Añadir Nuevas Funcionalidades (Adding New Features)

#### **Patrón: Nuevo Dashboard**

1. **Crear Route en app.py**:
```python
@app.route('/dashboard_nuevas_metricas')
def dashboard_nuevas_metricas():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Obtener datos
    data = data_manager.get_nuevas_metricas()
    
    # Renderizar
    return render_template('dashboard_nuevas_metricas.html', data=data)
```

2. **Crear Template en templates/**:
```html
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>Nuevas Métricas</h1>
    <!-- Contenido del dashboard -->
</div>
{% endblock %}
```

3. **Agregar Método en Manager** (si requiere nueva data):
```python
# src/odoo_manager.py
class OdooManager:
    def get_nuevas_metricas(self):
        """
        Nueva funcionalidad para obtener métricas específicas
        """
        domain = [...]  # Filtros Odoo
        metricas = self.models.execute_kw(...)
        return self._transformar_metricas(metricas)
```

4. **Agregar Link en Navigation** (templates/base.html):
```html
<nav>
    <a href="{{ url_for('dashboard') }}">Dashboard</a>
    <a href="{{ url_for('dashboard_nuevas_metricas') }}">Nuevas Métricas</a>
</nav>
```

#### **Patrón: Nueva Entidad de Supabase**

1. **Crear Tabla en Supabase**:
```sql
CREATE TABLE nueva_entidad_2026 (
    id SERIAL PRIMARY KEY,
    campo1 TEXT NOT NULL,
    campo2 NUMERIC,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

2. **Agregar Métodos en SupabaseManager**:
```python
# src/supabase_manager.py
class SupabaseManager:
    def guardar_nueva_entidad(self, campo1, campo2):
        data = {
            'campo1': campo1,
            'campo2': campo2,
            'updated_at': datetime.now().isoformat()
        }
        result = self.supabase.table('nueva_entidad_2026')\
            .insert(data)\
            .execute()
        return result.data[0] if result.data else None
    
    def obtener_nueva_entidad(self, id):
        result = self.supabase.table('nueva_entidad_2026')\
            .select('*')\
            .eq('id', id)\
            .execute()
        return result.data[0] if result.data else None
```

3. **Crear Routes CRUD**:
```python
@app.route('/nueva_entidad', methods=['GET'])
def nueva_entidad_list(): ...

@app.route('/nueva_entidad/<int:id>', methods=['GET'])
def nueva_entidad_detail(id): ...

@app.route('/nueva_entidad/create', methods=['POST'])
def nueva_entidad_create(): ...
```

### 13.2 Patrones de Modificación (Modification Patterns)

#### **Agregar Campo a Dashboard Existente**

1. **Actualizar Query en Manager**:
```python
# src/odoo_manager.py
def get_sales_lines(self, ...):
    fields = [
        'id', 'partner_id', 'product_id',
        'nuevo_campo',  # ← Agregar aquí
        ...
    ]
    
    sales_lines = self.models.execute_kw(..., {'fields': fields})
    return sales_lines
```

2. **Modificar Template para Mostrar Nuevo Campo**:
```html
{% for line in sales_lines %}
<tr>
    <td>{{ line.partner_id[1] }}</td>
    <td>{{ line.product_id[1] }}</td>
    <td>{{ line.nuevo_campo }}</td>  {# ← Agregar aquí #}
</tr>
{% endfor %}
```

#### **Agregar Filtro Adicional**

1. **Agregar Select en Template**:
```html
<form method="get">
    <select name="nuevo_filtro">
        <option value="">Todos</option>
        {% for opcion in opciones_filtro %}
        <option value="{{ opcion.id }}">{{ opcion.nombre }}</option>
        {% endfor %}
    </select>
    <button type="submit">Filtrar</button>
</form>
```

2. **Actualizar Route para Manejar Filtro**:
```python
@app.route('/dashboard')
def dashboard():
    nuevo_filtro = request.args.get('nuevo_filtro')
    
    sales_lines = data_manager.get_sales_lines(
        date_from=date_from,
        date_to=date_to,
        nuevo_filtro=nuevo_filtro  # ← Pasar nuevo parámetro
    )
```

3. **Actualizar Manager para Aplicar Filtro**:
```python
def get_sales_lines(self, ..., nuevo_filtro=None):
    domain = [...]
    
    if nuevo_filtro:
        domain.append(('campo_nuevo', '=', int(nuevo_filtro)))
    
    sales_lines = self.models.execute_kw(..., [domain])
```

### 13.3 Patrones de Integración (Integration Patterns)

#### **Integrar Nuevo Sistema Externo**

1. **Crear Nuevo Manager** (src/nuevo_sistema_manager.py):
```python
import requests

class NuevoSistemaManager:
    def __init__(self):
        self.api_url = os.getenv('NUEVO_SISTEMA_URL')
        self.api_key = os.getenv('NUEVO_SISTEMA_KEY')
        self.enabled = bool(self.api_url and self.api_key)
    
    def obtener_datos(self, filters=None):
        if not self.enabled:
            return []
        
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.get(f'{self.api_url}/data', headers=headers)
        return response.json()
```

2. **Inicializar en app.py**:
```python
from src.nuevo_sistema_manager import NuevoSistemaManager

nuevo_sistema_manager = NuevoSistemaManager()
```

3. **Usar en Routes**:
```python
@app.route('/dashboard_integrado')
def dashboard_integrado():
    # Combinar datos de múltiples fuentes
    odoo_data = data_manager.get_sales_lines(...)
    nuevo_sistema_data = nuevo_sistema_manager.obtener_datos(...)
    
    # Merge/Transform
    combined = merge_data(odoo_data, nuevo_sistema_data)
    
    return render_template('dashboard_integrado.html', data=combined)
```

---

## 14. Ejemplos de Patrones Arquitectónicos (Architectural Pattern Examples)

### 14.1 Ejemplos de Separación de Capas (Layer Separation Examples)

**Correcto ✅: Route delega a Manager**
```python
# app.py
@app.route('/dashboard')
def dashboard():
    # Application layer: sólo orquestación
    sales_lines = data_manager.get_sales_lines(
        date_from='2026-01-01',
        date_to='2026-01-31'
    )
    
    metas = supabase_manager.obtener_metas_mes('2026-01')
    
    # Renderizado
    return render_template('dashboard.html',
                         sales=sales_lines,
                         metas=metas)

# src/odoo_manager.py
class OdooManager:
    def get_sales_lines(self, date_from, date_to):
        # Business logic: construcción de query + transformación
        domain = [
            ('state', 'in', ['sale', 'done']),
            ('date_order', '>=', date_from),
            ('date_order', '<=', date_to)
        ]
        
        raw_data = self.models.execute_kw(...)
        transformed = self._transform_many2one_fields(raw_data)
        
        return transformed
```

**Incorrecto ❌: Lógica de negocio en Route**
```python
# app.py - TODO: Refactorizar
@app.route('/dashboard')
def dashboard():
    # ❌ Construcción de domain filters en route
    domain = [
        ('state', 'in', ['sale', 'done']),
        ('date_order', '>=', date_from),
        ('date_order', '<=', date_to)
    ]
    
    # ❌ Llamada directa a models (bypassing manager)
    sales_lines = data_manager.models.execute_kw(
        data_manager.db,
        data_manager.uid,
        data_manager.password,
        'sale.order.line',
        'search_read',
        [domain],
        {'fields': [...]}
    )
    
    # ❌ Transformación de datos en route
    for line in sales_lines:
        line['cliente'] = line['partner_id'][1] if line['partner_id'] else ''
    
    # ❌ Cálculos de negocio en route
    total = sum(line['price_subtotal'] for line in sales_lines)
```

### 14.2 Ejemplos de Comunicación entre Componentes (Component Communication Examples)

**Dependency Injection via Constructor**:
```python
# Opción actual (singleton global)
data_manager = OdooManager()

@app.route('/dashboard')
def dashboard():
    # Accede globalmente
    sales = data_manager.get_sales_lines(...)

# Mejor: Inyección explícita
class DashboardService:
    def __init__(self, data_manager: OdooManager, 
                 supabase_manager: SupabaseManager):
        self.data_manager = data_manager
        self.supabase_manager = supabase_manager
    
    def get_dashboard_data(self, mes, año):
        sales = self.data_manager.get_sales_lines(...)
        metas = self.supabase_manager.obtener_metas_mes(mes)
        return self._calcular_cumplimiento(sales, metas)

# En app.py
dashboard_service = DashboardService(data_manager, supabase_manager)

@app.route('/dashboard')
def dashboard():
    data = dashboard_service.get_dashboard_data(mes, año)
    return render_template('dashboard.html', **data)
```

**Event-Driven Pattern** (para analytics):
```python
# Current: Middleware implícito
@app.after_request
def after_request(response):
    if 'username' in session:
        analytics_db.registrar_visita(...)
    return response

# Alternativa: Event Publishing
class EventBus:
    listeners = {}
    
    @classmethod
    def subscribe(cls, event_type, handler):
        if event_type not in cls.listeners:
            cls.listeners[event_type] = []
        cls.listeners[event_type].append(handler)
    
    @classmethod
    def publish(cls, event_type, data):
        for handler in cls.listeners.get(event_type, []):
            handler(data)

# Subscriber
def handle_page_visit(data):
    analytics_db.registrar_visita(**data)

EventBus.subscribe('page_visit', handle_page_visit)

# Publisher
@app.after_request
def after_request(response):
    if 'username' in session:
        EventBus.publish('page_visit', {
            'user_email': session['username'],
            'page_url': request.path,
            ...
        })
    return response
```

### 14.3 Ejemplos de Puntos de Extensión (Extension Point Examples)

**Plugin Registration** (ejemplo futuro para exporters):
```python
# src/exporters/__init__.py
class ExporterRegistry:
    _exporters = {}
    
    @classmethod
    def register(cls, name, exporter_class):
        cls._exporters[name] = exporter_class
    
    @classmethod
    def get_exporter(cls, name):
        return cls._exporters.get(name)

# src/exporters/excel_exporter.py
class ExcelExporter:
    def export(self, data, filename):
        df = pd.DataFrame(data)
        output = io.BytesIO()
        df.to_excel(output, engine='openpyxl', index=False)
        return output

ExporterRegistry.register('excel', ExcelExporter)

# src/exporters/csv_exporter.py
class CSVExporter:
    def export(self, data, filename):
        df = pd.DataFrame(data)
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()

ExporterRegistry.register('csv', CSVExporter)

# Usage en route
@app.route('/export/<format>/sales')
def export_sales(format):
    exporter_class = ExporterRegistry.get_exporter(format)
    if not exporter_class:
        return "Formato no soportado", 400
    
    exporter = exporter_class()
    sales = data_manager.get_sales_lines(...)
    output = exporter.export(sales, 'ventas')
    
    return send_file(output, mimetype=..., as_attachment=True)
```

**Configuration-Driven Extensions**:
```python
# config/dashboard_widgets.json
{
    "widgets": [
        {
            "id": "ventas_totales",
            "title": "Ventas Totales",
            "component": "KPIWidget",
            "data_source": "odoo.sales.total",
            "enabled": true
        },
        {
            "id": "cumplimiento_metas",
            "title": "Cumplimiento de Metas",
            "component": "GaugeWidget",
            "data_source": "supabase.metas.cumplimiento",
            "enabled": true
        },
        {
            "id": "top_productos",
            "title": "Top 10 Productos",
            "component": "TableWidget",
            "data_source": "odoo.products.top",
            "enabled": false  # Disabled via config
        }
    ]
}

# app.py
def load_dashboard_config():
    with open('config/dashboard_widgets.json') as f:
        return json.load(f)

@app.route('/dashboard')
def dashboard():
    config = load_dashboard_config()
    enabled_widgets = [w for w in config['widgets'] if w['enabled']]
    
    widget_data = {}
    for widget in enabled_widgets:
        data_source = widget['data_source']
        widget_data[widget['id']] = fetch_data(data_source)
    
    return render_template('dashboard.html',
                         widgets=enabled_widgets,
                         data=widget_data)
```

---

## 15. Registros de Decisiones Arquitectónicas - ADRs (Architectural Decision Records - ADRs)

### ADR-001: Python/Flask como Stack Principal (Python/Flask as Main Stack)

**Context**: Necesidad de dashboard web con integración rápida a Odoo ERP.

**Decision**: Usar Python con Flask framework.

**Rationale**:
- Python es el lenguaje oficial de Odoo → interoperabilidad natural
- Flask es ligero y flexible para dashboards analytics
- Ecosistema rico: pandas, openpyxl para data processing
- Equipo tiene experiencia en Python

**Consequences**:
- ✅ Pros: Desarrollo rápido, integración fluida con Odoo
- ❌ Cons: Performance inferior a frameworks compilados (aceptable para uso interno)
- ⚠️ Implicaciones: Requiere WSGI server (Gunicorn) en producción

**Alternatives Considered**:
- Django: Demasiado pesado para un dashboard simple
- Node.js: Menor experiencia del equipo
- .NET Core: Más complejo de hostear en infraestructura existente

---

### ADR-002: JSON-RPC sobre XML-RPC para Odoo (JSON-RPC over XML-RPC for Odoo)

**Context**: Conexión a Odoo ERP, módulo `cs_login_audit_log` causa `RuntimeError` en XML-RPC.

**Decision**: Migrar de XML-RPC a JSON-RPC para comunicación con Odoo.

**Rationale**:
- XML-RPC tiene problemas con módulos de auditoría customizados
- JSON-RPC es el protocolo moderno recomendado por Odoo (v13+)
- Mejor handling de errores y debugging
- Payload más compacto (JSON vs XML)

**Consequences**:
- ✅ Pros: Evita incompatibilidad con módulos custom, más eficiente
- ❌ Cons: Breaking change, requiere refactor, menos documentación legacy
- ⚠️ Implicaciones: Compatibilidad retroactiva con wrapper pattern

**Implementation**: Commit `a394060` - "feat: Migrar conexión Odoo de XML-RPC a JSON-RPC"

---

### ADR-003: Supabase para Gestión de Metas (Supabase for Goal Management)

**Context**: Sistema legacy de metas en Google Sheets era frágil y lento.

**Decision**: Migrar metas de ventas a Supabase (PostgreSQL managed).

**Rationale**:
- Google Sheets API tiene rate limits estrictos
- Sheets no es una base de datos transaccional
- Supabase ofrece PostgreSQL + REST API + Real-time subscriptions
- Mejor control de datos y versionado por año

**Consequences**:
- ✅ Pros: Performance mejorado, transacciones ACID, escalabilidad
- ✅ Pros: Real-time updates potenciales (no usado aún)
- ❌ Cons: Costo adicional ($25/mes Starter plan)
- ⚠️ Implicaciones: Migración anual de tablas (metas_ventas_YYYY)

**Alternatives Considered**:
- PostgreSQL directo: Más complejo de administrar sin Supabase UI
- MongoDB: No necesitamos schema flexibility extrema
- Mantener Sheets: Rechazado por limitaciones técnicas

---

### ADR-004: SQLite Fallback para Analytics (SQLite Fallback for Analytics)

**Context**: Analytics DB debe funcionar en dev sin PostgreSQL instalado.

**Decision**: Dual-mode analytics: PostgreSQL (prod) / SQLite (dev).

**Rationale**:
- SQLite elimina dependencia externa en desarrollo local
- PostgreSQL necesario en producción para concurrencia
- Abstracción permite cambio transparente

**Consequences**:
- ✅ Pros: Onboarding más rápido (sin setup de DB)
- ❌ Cons: Potenciales diferencias SQL entre motores
- ⚠️ Implicaciones: Tests deben correr en ambos modos

**Implementation**:
```python
if os.getenv('DATABASE_URL'):
    use_postgresql()
else:
    use_sqlite('analytics.db')
```

---

### ADR-005: OAuth2 con Google Workspace (OAuth2 with Google Workspace)

**Context**: Necesidad de SSO corporativo para control de acceso.

**Decision**: Implementar OAuth2 con Google como Identity Provider.

**Rationale**:
- Empresa usa Google Workspace → usuarios ya existen
- Elimina gestión de passwords propios
- Whitelist adicional (`allowed_users.json`) para doble capa de seguridad

**Consequences**:
- ✅ Pros: Seguridad mejorada, UX fluida (login con cuenta corporativa)
- ❌ Cons: Dependencia de Google OAuth2 uptime
- ⚠️ Implicaciones: Redirect URIs deben configurarse en Google Console

**Security Boundaries**:
1. Google OAuth2: Verifica identidad
2. `allowed_users.json`: Lista blanca de emails permitidos
3. Role-based permissions: Listas hardcoded por feature

---

### ADR-006: Server-Side Rendering con Jinja2 (Server-Side Rendering with Jinja2)

**Context**: Decisión entre SPA (React/Vue) vs Server-Side Rendering.

**Decision**: Usar Jinja2 templates (server-side rendering).

**Rationale**:
- Dashboard es consumido por usuarios internos (~40 personas)
- No requiere interactividad compleja tipo spreadsheet
- Menor complejidad: no necesita frontend build process
- Gráficos con ECharts (client-side) suficiente para visualización

**Consequences**:
- ✅ Pros: Simple, rápido de desarrollar, SEO-friendly (no crítico aquí)
- ❌ Cons: Full page refreshes, no real-time updates sin polling
- ⚠️ Implicaciones: Para features real-time futuras, considerar WebSockets

**Alternatives Considered**:
- React SPA: Overhead innecesario para app interna
- HTMX: Prometedor, pero agrega dependencia adicional

---

### ADR-007: Listas de Permisos Hardcoded - Deuda Técnica (Hardcoded Permission Lists - Technical Debt)

**Context**: Sistema de permisos implementado con listas de emails en código.

**Decision**: Mantener listas hardcoded short-term, planear migración a DB.

**Rationale**:
- Velocidad de desarrollo inicial (MVP rápido)
- Usuarios administradores cambian raramente
- Sistema pequeño (~7 admins, ~40 usuarios totales)

**Consequences**:
- ✅ Pros: Implementación rápida, no requiere UI de admin
- ❌ Cons: Cambios requieren deploy, código duplicado en ~10 lugares
- ⚠️ Technical Debt: Prioridad MEDIA para refactor a tabla `user_permissions`

**Migration Plan**:
```sql
CREATE TABLE user_permissions (
    user_email TEXT PRIMARY KEY,
    role TEXT NOT NULL,  -- 'admin_full', 'admin_export', 'user_basic'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE role_permissions (
    role TEXT,
    permission TEXT,
    PRIMARY KEY (role, permission)
);
```

**Status**: ✅ **RESUELTO en Marzo 2026** - Migrado a PermissionsManager con Supabase.

---

### ADR-008: Sistema de Auditoría Completo (Complete Audit System) - **NUEVO Abril 2026**

**Context**: Necesidad de cumplir con estándares de seguridad (ISO 27001, OWASP, PCI-DSS, GDPR, SOC 2) que requieren auditoría de eventos de autenticación y cambios de permisos.

**Decision**: Implementar AuditLogger con registro completo de login/logout y cambios de permisos en Supabase.

**Rationale**:
- **Cumplimiento normativo**: ISO 27001 requiere trazabilidad de accesos
- **OWASP A01**: Broken Authentication - necesita logging de intentos fallidos
- **PCI-DSS Requirement 10**: Logging obligatorio de eventos de seguridad
- **GDPR Art 30**: Registro de actividades de tratamiento de datos
- **SOC 2**: Control de acceso y monitoreo continuo
- **Investigación de incidentes**: Necesidad de histórico completo para análisis forense

**Design Decisions**:
1. **Tabla única** (`audit_log_permissions`) para permisos y autenticación
   - Simplifica queries y vistas consolidadas
   - Evita JOINs complejos para timeline completo
   
2. **Session ID tracking** para correlación login→logout
   - Permite calcular duración real de sesión
   - Facilita detección de sesiones anómalas
   
3. **Dual timeout** (inactividad + absoluto)
   - 15 minutos inactividad: protege contra walk-away
   - 8 horas absoluto: limita ventana de exposición
   
4. **Timezone Peru (UTC-5)** en presentación
   - Datos almacenados en UTC (estándar)
   - Conversión client-side con filtros Jinja2
   - Facilita correlación con eventos externos

**Consequences**:
- ✅ Pros: Cumplimiento normativo completo, trazabilidad total
- ✅ Pros: Dashboard de seguridad con métricas en tiempo real
- ✅ Pros: Detección temprana de ataques (intentos fallidos por IP)
- ❌ Cons: Overhead de storage (~50KB por día con 40 usuarios)
- ❌ Cons: Complejidad adicional en routes (3-5 líneas por endpoint)
- ⚠️ Implicaciones: Retención de datos 1 año (configurable)

**Implementation**:
- Commit `b792f42`: "feat: Dashboard de Seguridad con auditoría completa de login/logout y mejoras UI"
- Archivos: `src/audit_logger.py`, `templates/admin/audit_log.html`
- SQL Migration: `sql/update_audit_constraint_add_login_events.sql`

**Alternatives Considered**:
- **Separar tablas** (auth_events + permission_events): Rechazado por complejidad en queries
- **Third-party SIEM**: Rechazado por costo y overkill para <50 usuarios
- **File-based logging**: Rechazado por dificultad de querying y visualización

---

### ADR-009: Dashboard de Seguridad con Chart.js (Security Dashboard with Chart.js) - **NUEVO Abril 2026**

**Context**: AuditLogger genera datos, pero se necesita visualización para detectar patrones de seguridad.

**Decision**: Crear dashboard de seguridad (`/admin/audit-log`) con métricas 24h, gráficas Chart.js y tablas DataTables.

**Rationale**:
- **Visibilidad**: Admin necesita ver rápidamente estado de seguridad
- **Alertas proactivas**: Detectar >10 intentos fallidos desde misma IP
- **Análisis de tendencias**: Timeline horario revela horarios de ataques
- **UX moderna**: Tabs separan concerns (seguridad vs permisos)

**Design Decisions**:
1. **Tabbed interface** (Bootstrap 5):
   - Tab 1: Seguridad (métricas 24h)
   - Tab 2: Cambios de permisos (histórico filtrable)
   
2. **Chart.js line chart** para timeline:
   - 4 datasets: login_success, login_failed, logout, timeout
   - Agrupación horaria en timezone Peru
   - Colores semáforo: verde (success), rojo (failed), azul (logout), amarillo (timeout)
   
3. **DataTables** para tablas interactivas:
   - Ordenamiento, búsqueda, paginación client-side
   - Exportación CSV/Excel (potencial extensión)
   
4. **Color-coded role badges**:
   - admin_full: Rojo (#dc3545)
   - admin_export: Naranja (#fd7e14)
   - analytics_viewer: Cyan (#0dcaf0)
   - user_basic: Gris (#6c757d)

**Consequences**:
- ✅ Pros: Detección visual rápida de anomalías
- ✅ Pros: No requiere conocimiento técnico (SQL)
- ✅ Pros: Chart.js es ligero (60KB minified)
- ❌ Cons: Client-side rendering (limitado a ~1000 registros)
- ⚠️ Implicaciones: Filtro por período necesario para rendimiento

**Implementation**:
- Template: `templates/admin/audit_log.html` (~1000 líneas)
- Route: `/admin/audit-log` con parámetros `days`, `action`, `admin`
- Assets: Chart.js 4.4.0 CDN, DataTables 1.13.7 CDN

**Alternatives Considered**:
- **Grafana**: Rechazado por complejidad de setup
- **ECharts** (usado en otros dashboards): Chart.js más simple para time series
- **Server-side DataTables**: Innecesario con <100 registros por vista

---

### ADR-010: Migración de PermissionsManager de SQLite a Supabase - **NUEVO Abril 2026**

**Context**: PermissionsManager usaba SQLite local, pero AuditLogger requiere Supabase para audit_log_permissions. Mantener dos DBs crea inconsistencia.

**Decision**: Migrar user_permissions de SQLite a Supabase.

**Rationale**:
- **Consistencia**: Ambos sistemas (permisos + auditoría) en misma DB
- **Transaccionalidad**: Cambio de rol + audit log en misma transacción
- **Producción**: Supabase ya desplegado, SQLite complicaría deployment
- **Backup**: Supabase tiene backups automáticos, SQLite requiere manejo manual

**Migration Strategy**:
1. Crear tabla `user_permissions` en Supabase (mismo schema que SQLite)
2. Migrar datos existentes vía script Python
3. Actualizar `PermissionsManager.__init__()` para usar Supabase client
4. Mantener fallback a lista vacía si Supabase no disponible

**Consequences**:
- ✅ Pros: Single source of truth para datos de usuario
- ✅ Pros: Real-time queries (Supabase PostgREST)
- ❌ Cons: Dependencia absoluta de Supabase (crítico)
- ⚠️ Implicaciones: Desarrollo local requiere Supabase configurado

**Implementation**:
- Schema: `user_permissions` table en Supabase
- Migration: Código actualizado en `src/permissions_manager.py`
- Backward compatibility: Fallback a `enabled=False` si Supabase falla

**Status**: ✅ **COMPLETADO en Abril 2026**

---

## 16. Architecture Governance

### 16.1 Code Review Guidelines

**Pre-Commit Checklist**:
- [ ] Nuevas queries a Odoo usan `data_manager` (no llamadas directas)
- [ ] Variables sensibles en `.env`, no hardcodeadas
- [ ] Nuevas routes tienen check de `session['username']`
- [ ] Managers tienen error handling con fallback
- [ ] Print statements usan prefijos consistentes ([OK], [ERROR])
- [ ] Templates extienden `base.html`
- [ ] Nuevos archivos sensibles agregados a `.gitignore`

**Architecture Review Triggers**:
- Nueva integración externa (requiere nuevo manager)
- Cambios en autenticación/autorización
- Modificaciones a esquemas de Supabase
- Nuevos endpoints públicos

### 16.2 Automated Checks

**Pre-Commit Hooks** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash

# Check for hardcoded secrets
if git diff --cached | grep -iE "(password|secret|api[_-]?key)" | grep -v ".env"; then
    echo "❌ Posible secreto hardcodeado detectado"
    exit 1
fi

# Check import order (dotenv must be first)
if git diff --cached app.py | grep -A5 "^+from dotenv import load_dotenv"; then
    if ! git diff --cached app.py | head -20 | grep "load_dotenv()"; then
        echo "⚠️ Verificar que load_dotenv() se llame antes de imports"
    fi
fi

# Run quick tests
python -m pytest tests/unit/ --fast
if [ $? -ne 0 ]; then
    echo "❌ Tests unitarios fallaron"
    exit 1
fi
```

**CI/CD Pipeline** (GitHub Actions example):
```yaml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run linter
        run: flake8 app.py src/
      
      - name: Run unit tests
        run: pytest tests/unit/
      
      - name: Security check
        run: bandit -r src/
      
      - name: Check for hardcoded secrets
        run: |
          ! git grep -iE "(password|secret|api[_-]?key)" | grep -v ".env"
```

### 16.3 Documentation Standards

**Manager Docstrings** (required):
```python
def get_sales_lines(self, date_from=None, date_to=None, partner_id=None, 
                    linea_id=None, limit=1000):
    """
    Obtiene líneas de venta desde Odoo con filtros opcionales.
    
    Args:
        date_from (str, optional): Fecha inicio formato 'YYYY-MM-DD'
        date_to (str, optional): Fecha fin formato 'YYYY-MM-DD'
        partner_id (int, optional): ID del cliente en Odoo
        linea_id (int, optional): ID de línea comercial
        limit (int): Máximo de registros a devolver (default: 1000)
    
    Returns:
        list[dict]: Lista de líneas de venta con campos transformados.
                   Cada dict contiene: id, partner_id, product_id, 
                   price_subtotal, date_order, etc.
    
    Raises:
        None: Devuelve lista vacía si hay error de conexión.
    
    Example:
        >>> sales = manager.get_sales_lines(
        ...     date_from='2026-01-01',
        ...     date_to='2026-01-31',
        ...     linea_id=5
        ... )
        >>> len(sales)
        245
    """
```

**Route Documentation** (inline comments):
```python
@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Dashboard principal con metas por línea comercial.
    
    Query Params:
        - año (str): Año a visualizar. Default: año actual
        - mes (str): Mes específico. Default: None (todos los meses)
    
    Permissions:
        - Requires: session['username'] (authenticated)
        - Admin features visible si: username in admin_users
    
    Returns:
        - 200: Renderiza dashboard_clean.html
        - 302: Redirect a /login si no autenticado
    """
```

---

## 17. Blueprint for New Development

### 17.1 Development Workflow

#### **Starting a New Feature**

1. **Branch Creation**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

2. **Environment Setup**
   ```bash
   # Activate venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   
   # Install any new dependencies
   pip install -r requirements.txt
   
   # Verify .env is configured
   cat .env  # Check required variables loaded
   ```

3. **Architecture Planning**
   - ¿Requiere nueva data? → Nuevo método en Manager
   - ¿Nueva UI? → Nuevo template + ruta
   - ¿Nueva integración? → Nuevo manager class
   - ¿Cambio en permisos? → Actualizar listas de admin

4. **Implementation Order**
   1. Data Layer: Manager methods
   2. Application Layer: Routes
   3. Presentation Layer: Templates
   4. Testing: Unit + Integration tests

5. **Testing Locally**
   ```bash
   # Run app
   python app.py
   
   # Navigate to http://127.0.0.1:5000
   # Test feature manually
   
   # Run automated tests
   pytest tests/
   ```

6. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: Descripción de nueva funcionalidad"
   git push origin feature/nueva-funcionalidad
   ```

7. **Pull Request**
   - Descripción clara de cambios
   - Screenshots si es UI
   - Checklist de testing
   - Link a issue/ticket

### 17.2 Implementation Templates

#### **Template: Nuevo Manager**

```python
# src/nuevo_manager.py
import os
from dotenv import load_dotenv

load_dotenv()

class NuevoManager:
    """
    Gestor para [descripción del sistema externo].
    
    Responsabilidades:
    - [Responsabilidad 1]
    - [Responsabilidad 2]
    """
    
    def __init__(self):
        """Inicializa conexión al sistema externo"""
        # Load configuration
        self.api_url = os.getenv('NUEVO_SISTEMA_URL')
        self.api_key = os.getenv('NUEVO_SISTEMA_KEY')
        
        # Validate configuration
        self.enabled = bool(self.api_url and self.api_key)
        
        if self.enabled:
            self._authenticate()
            print("[OK] Conexión a [Sistema] establecida")
        else:
            print("[ERROR] [Sistema] no configurado. Modo offline")
    
    def _authenticate(self):
        """Private: Establecer autenticación"""
        # Authentication logic here
        pass
    
    def obtener_datos(self, filters=None):
        """
        Obtiene datos del sistema externo.
        
        Args:
            filters (dict, optional): Filtros a aplicar
        
        Returns:
            list[dict]: Datos obtenidos, o [] si error
        """
        if not self.enabled:
            return []
        
        try:
            # Fetch logic here
            data = []
            return data
        except Exception as e:
            print(f"[ERROR] Error obteniendo datos: {e}")
            return []
```

**Integración en app.py**:
```python
# app.py
from src.nuevo_manager import NuevoManager

# Después de otros managers
nuevo_manager = NuevoManager()
```

#### **Template: Nueva Ruta con Permisos**

```python
@app.route('/nueva_funcionalidad', methods=['GET', 'POST'])
def nueva_funcionalidad():
    """
    [Descripción de la funcionalidad]
    
    Permissions: Requiere admin_full
    """
    # 1. Authentication check
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # 2. Authorization check
    admin_users = [
        "jonathan.cerda@agrovetmarket.com",
        "janet.hueza@agrovetmarket.com",
        # ... lista completa
    ]
    
    is_admin = session.get('username') in admin_users
    if not is_admin:
        flash('No tienes permiso para acceder a esta página.', 'warning')
        return redirect(url_for('dashboard'))
    
    # 3. Handle POST (if applicable)
    if request.method == 'POST':
        # Extract form data
        campo1 = request.form.get('campo1')
        campo2 = request.form.get('campo2')
        
        # Validate
        if not campo1:
            flash('Campo1 es obligatorio', 'danger')
            return redirect(url_for('nueva_funcionalidad'))
        
        # Process
        try:
            result = manager.procesar_algo(campo1, campo2)
            if result:
                flash('✅ Operación exitosa', 'success')
            else:
                flash('⚠️ Operación falló', 'warning')
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'danger')
        
        return redirect(url_for('nueva_funcionalidad'))
    
    # 4. Handle GET
    try:
        # Fetch data
        data = manager.obtener_datos()
        
        # Prepare context
        context = {
            'data': data,
            'is_admin': is_admin,
            'page_title': 'Nueva Funcionalidad'
        }
        
        # Render
        return render_template('nueva_funcionalidad.html', **context)
    
    except Exception as e:
        flash(f'Error cargando datos: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
```

#### **Template: Nuevo Template Jinja2**

```html
{% extends "base.html" %}

{% block title %}Nueva Funcionalidad - Dashboard Ventas{% endblock %}

{% block head_extra %}
<!-- CSS específico de esta página -->
<style>
    .mi-componente {
        /* Estilos aquí */
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Nueva Funcionalidad</h1>
    
    <!-- Breadcrumb -->
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
            <li class="breadcrumb-item active">Nueva Funcionalidad</li>
        </ol>
    </nav>
    
    <!-- Flash messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
            <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <!-- Form (si aplica) -->
    {% if is_admin %}
    <div class="card mb-4">
        <div class="card-body">
            <h5 class="card-title">Formulario</h5>
            <form method="post" action="{{ url_for('nueva_funcionalidad') }}">
                <div class="mb-3">
                    <label for="campo1" class="form-label">Campo 1</label>
                    <input type="text" class="form-control" id="campo1" name="campo1" required>
                </div>
                <button type="submit" class="btn btn-primary">Guardar</button>
            </form>
        </div>
    </div>
    {% endif %}
    
    <!-- Data Display -->
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Datos</h5>
            
            {% if data %}
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Columna 1</th>
                        <th>Columna 2</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in data %}
                    <tr>
                        <td>{{ item.campo1 }}</td>
                        <td>{{ item.campo2 }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="text-muted">No hay datos disponibles.</p>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}

{% block scripts_extra %}
<!-- JavaScript específico -->
<script>
    // Código JS aquí
</script>
{% endblock %}
```

### 17.3 Common Pitfalls

1. **❌ Olvidar `load_dotenv()` Antes de Imports**
   ```python
   # INCORRECTO
   from src.odoo_manager import OdooManager  # ← Usa .env en __init__
   from dotenv import load_dotenv
   load_dotenv()  # ← Demasiado tarde
   
   # CORRECTO
   from dotenv import load_dotenv
   import os
   load_dotenv()  # ← Antes que cualquier import de src/
   from src.odoo_manager import OdooManager
   ```

2. **❌ No Validar Sesión en Routes**
   ```python
   # INCORRECTO
   @app.route('/dashboard')
   def dashboard():
       data = data_manager.get_sales_lines()  # Sin auth check
   
   # CORRECTO
   @app.route('/dashboard')
   def dashboard():
       if 'username' not in session:
           return redirect(url_for('login'))
       data = data_manager.get_sales_lines()
   ```

3. **❌ Hardcodear Credenciales**
   ```python
   # INCORRECTO
   self.api_key = "sk_live_abc123def456"
   
   # CORRECTO
   self.api_key = os.getenv('API_KEY')
   if not self.api_key:
       raise ValueError("API_KEY no configurada en .env")
   ```

4. **❌ No Manejar Errores de Servicios Externos**
   ```python
   # INCORRECTO
   data = self.models.execute_kw(...)  # Puede lanzar exception
   
   # CORRECTO
   try:
       data = self.models.execute_kw(...)
       return data
   except Exception as e:
       print(f"[ERROR] Error llamando a Odoo: {e}")
       return []
   ```

5. **❌ Mutar Variables Globales**
   ```python
   # INCORRECTO
   CACHE = {}
   
   @app.route('/data')
   def get_data():
       CACHE['last_request'] = datetime.now()  # Problema en multi-worker
   
   # CORRECTO
   # Usar Redis o session para estado compartido
   session['last_request'] = datetime.now().isoformat()
   ```

6. **❌ Queries N+1 a Odoo**
   ```python
   # INCORRECTO
   for line in sales_lines:
       # Query individual por cada línea (lento!)
       product = data_manager.get_product(line['product_id'][0])
   
   # CORRECTO
   # Obtener todos los IDs y hacer 1 query bulk
   product_ids = [line['product_id'][0] for line in sales_lines]
   products = data_manager.get_products_bulk(product_ids)
   ```

7. **❌ Olvidar Limpieza de Recursos**
   ```python
   # INCORRECTO
   conn = sqlite3.connect('analytics.db')
   cursor = conn.cursor()
   cursor.execute(...)
   # ← Si hay exception, conexión queda abierta
   
   # CORRECTO
   with analytics_db.get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute(...)
   # ← Context manager garantiza cierre
   ```

---

## 18. Maintenance & Evolution

### 18.1 Keeping Blueprint Updated

**This blueprint was generated**: 17 de marzo de 2026

**Update Triggers**:
- Nueva arquitectura layer o servicio agregado
- Cambio de tecnología core (ej: migrar de Flask a FastAPI)
- Patterns obsoletos reemplazados
- Architectural decisions significativos

**Process**:
1. Modificar secciones relevantes del blueprint
2. Actualizar fecha en Executive Summary
3. Agregar ADR si decision arquitectónica nueva
4. Commit con mensaje: `docs: Actualizar architecture blueprint - [razón]`

**Responsable**: Tech Lead o Arquitecto de Software

### 18.2 Architecture Review Cadence

**Mensual**: Quick review de tech debt identificado  
**Trimestral**: Full architecture review meeting  
**Anual**: Blueprint regeneration y actualización mayor

---

## 19. Appendix

### 19.1 Glossary

- **Odoo**: ERP open-source, fuente de datos transaccionales
- **Supabase**: Backend-as-a-Service basado en PostgreSQL
- **JSON-RPC**: Protocolo de llamada remota sobre JSON/HTTP
- **OAuth2**: Estándar de autorización delegada
- **Many2One**: Tipo de campo Odoo que relaciona un registro con otro
- **Domain**: Expresión de filtro en Odoo (lista de tuplas)
- **Upsert**: INSERT + UPDATE (insert if not exists, update if exists)
- **RLS**: Row Level Security (Supabase)

### 19.2 Key Files Reference

```
app.py                            # Application entry point
src/odoo_manager.py               # Odoo ERP integration
src/supabase_manager.py           # Metas management
src/analytics_db.py               # Usage tracking
templates/dashboard_clean.html    # Main dashboard UI
templates/base.html               # Base template
.env                              # Configuration (gitignored)
allowed_users.json                # User whitelist (gitignored)
requirements.txt                  # Python dependencies
docs/ARQUITECTURA_ALTO_NIVEL.md  # Previous architecture doc
```

### 19.3 External Dependencies Documentation

- **Flask**: https://flask.palletsprojects.com/
- **Odoo API**: https://www.odoo.com/documentation/16.0/developer/reference/external_api.html
- **Supabase Python**: https://supabase.com/docs/reference/python/introduction
- **Authlib**: https://docs.authlib.org/en/latest/
- **Pandas**: https://pandas.pydata.org/docs/
- **ECharts**: https://echarts.apache.org/en/index.html

---

**End of Architecture Blueprint**

*Last Updated: 17 de marzo de 2026*  
*Generated using: architecture-blueprint-generator skill*  
*Project Version: 2.0*
