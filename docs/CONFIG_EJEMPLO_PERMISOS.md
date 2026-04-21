# Configuración de Ejemplo para Módulo de Permisos
## Archivo de Referencia para Implementación en Nuevos Proyectos

> 📅 **Creado**: 21 de abril de 2026  
> 🎯 **Propósito**: Guía rápida de configuración para diferentes tipos de proyectos

---

## 1. Configuración Base (config.py)

### Ejemplo Mínimo

```python
# config.py
import os
from pathlib import Path

class Config:
    """Configuración base del módulo de permisos"""
    
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-CHANGE-IN-PRODUCTION'
    CSRF_ENABLED = True
    
    # Base de datos
    BASE_DIR = Path(__file__).parent
    PERMISSIONS_DB_PATH = BASE_DIR / 'permissions.db'
    
    # Email corporativo
    ALLOWED_EMAIL_DOMAINS = os.environ.get(
        'ALLOWED_EMAIL_DOMAINS', 
        '@yourcompany.com'
    ).split(',')
    
    # Rate Limiting
    ADMIN_RATE_LIMIT_PER_HOUR = int(os.environ.get('ADMIN_RATE_LIMIT_PER_HOUR', 10))
    
    # Sesiones
    SESSION_TIMEOUT_MINUTES = int(os.environ.get('SESSION_TIMEOUT_MINUTES', 30))
    PERMANENT_SESSION_LIFETIME = SESSION_TIMEOUT_MINUTES * 60  # en segundos
    
    # Roles y Permisos - PERSONALIZAR SEGÚN PROYECTO
    ROLE_PERMISSIONS = {
        'admin_full': [
            'view_dashboard',
            'view_analytics',
            'edit_targets',
            'export_data',
            'manage_users'
        ],
        'manager': [
            'view_dashboard',
            'view_analytics',
            'export_data'
        ],
        'user': [
            'view_dashboard'
        ]
    }
    
    # Nombres display de roles (para UI)
    ROLE_DISPLAY_NAMES = {
        'admin_full': 'Administrador Completo',
        'manager': 'Gerente',
        'user': 'Usuario'
    }
    
    # Clases CSS para badges de roles
    ROLE_BADGE_CLASSES = {
        'admin_full': 'danger',
        'manager': 'warning',
        'user': 'secondary'
    }


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    PERMISSIONS_DB_PATH = Config.BASE_DIR / 'permissions_dev.db'


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # En producción, usar PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Seguridad estricta
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Configuración para tests"""
    TESTING = True
    PERMISSIONS_DB_PATH = ':memory:'  # SQLite en memoria
    WTF_CSRF_ENABLED = False  # Deshabilitar CSRF en tests


# Seleccionar configuración según entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

## 2. Variables de Entorno (.env)

### Desarrollo (.env.development)

```bash
# Entorno
FLASK_ENV=development
FLASK_DEBUG=True

# Base de datos
PERMISSIONS_DB_PATH=permissions_dev.db

# Email corporativo
ALLOWED_EMAIL_DOMAINS=@test.com,@dev.yourcompany.com,@yourcompany.com

# Seguridad (usar valor real en producción)
SECRET_KEY=dev-secret-key-not-for-production

# Rate Limiting (más permisivo en dev)
ADMIN_RATE_LIMIT_PER_HOUR=100

# Sesión
SESSION_TIMEOUT_MINUTES=60
```

### Producción (.env.production)

```bash
# Entorno
FLASK_ENV=production
FLASK_DEBUG=False

# Base de datos PostgreSQL
DATABASE_URL=postgresql://username:password@host:5432/dbname

# Email corporativo (solo dominios oficiales)
ALLOWED_EMAIL_DOMAINS=@yourcompany.com

# Seguridad (obtener desde gestor de secretos)
SECRET_KEY=${VAULT_SECRET_KEY}

# Rate Limiting (estricto)
ADMIN_RATE_LIMIT_PER_HOUR=10

# Sesión (más corta por seguridad)
SESSION_TIMEOUT_MINUTES=30

# Logs
LOG_LEVEL=INFO
```

---

## 3. Ejemplos por Tipo de Proyecto

### A. E-commerce / Tienda Online

```python
# config.py
ROLE_PERMISSIONS = {
    'super_admin': [
        'manage_users',
        'view_orders',
        'manage_orders',
        'manage_products',
        'manage_inventory',
        'view_analytics',
        'manage_promotions',
        'refund_orders',
        'export_all_data'
    ],
    'warehouse_manager': [
        'view_orders',
        'update_order_status',
        'manage_inventory',
        'manage_shipments',
        'view_products',
        'export_inventory'
    ],
    'customer_support': [
        'view_orders',
        'view_customers',
        'update_order_status',
        'create_refunds',
        'view_products'
    ],
    'marketing': [
        'view_analytics',
        'manage_promotions',
        'view_customers',
        'export_customer_data'
    ],
    'accountant': [
        'view_orders',
        'view_analytics',
        'export_financial_data'
    ],
    'viewer': [
        'view_orders',
        'view_products'
    ]
}

ROLE_DISPLAY_NAMES = {
    'super_admin': 'Super Administrador',
    'warehouse_manager': 'Gerente de Almacén',
    'customer_support': 'Atención al Cliente',
    'marketing': 'Marketing',
    'accountant': 'Contador',
    'viewer': 'Solo Lectura'
}
```

### B. CRM / Sistema de Ventas

```python
# config.py
ROLE_PERMISSIONS = {
    'admin_full': [
        'manage_users',
        'view_all_leads',
        'manage_all_leads',
        'view_all_contacts',
        'view_analytics',
        'edit_forecasts',
        'manage_territories',
        'export_all_data'
    ],
    'sales_director': [
        'view_all_leads',
        'manage_team_leads',
        'view_analytics',
        'edit_forecasts',
        'export_team_data',
        'view_all_contacts'
    ],
    'sales_manager': [
        'view_team_leads',
        'manage_team_leads',
        'view_team_analytics',
        'view_team_contacts',
        'export_team_data'
    ],
    'sales_rep': [
        'view_own_leads',
        'create_leads',
        'update_own_leads',
        'view_own_contacts',
        'create_contacts',
        'view_own_analytics'
    ],
    'analyst': [
        'view_all_leads',
        'view_all_contacts',
        'view_analytics',
        'export_reports'
    ],
    'viewer': [
        'view_assigned_leads',
        'view_assigned_contacts'
    ]
}
```

### C. Sistema de Reportes / Analytics

```python
# config.py
ROLE_PERMISSIONS = {
    'admin_full': [
        'manage_users',
        'create_reports',
        'edit_all_reports',
        'delete_reports',
        'publish_reports',
        'manage_datasources',
        'export_all'
    ],
    'report_creator': [
        'create_reports',
        'edit_own_reports',
        'publish_own_reports',
        'view_all_reports',
        'export_own'
    ],
    'analyst': [
        'view_all_reports',
        'export_all_reports',
        'create_queries'
    ],
    'business_user': [
        'view_assigned_reports',
        'export_assigned_reports'
    ],
    'viewer': [
        'view_public_reports'
    ]
}
```

### D. Sistema de Gestión de Contenido (CMS)

```python
# config.py
ROLE_PERMISSIONS = {
    'admin': [
        'manage_users',
        'manage_all_content',
        'publish_content',
        'delete_content',
        'manage_categories',
        'view_analytics'
    ],
    'editor_chief': [
        'view_all_content',
        'edit_all_content',
        'publish_content',
        'manage_authors',
        'view_analytics'
    ],
    'editor': [
        'create_content',
        'edit_own_content',
        'edit_team_content',
        'publish_own'
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
    ],
    'contributor': [
        'create_content',
        'view_own_content'
    ]
}
```

### E. Sistema de Recursos Humanos (HR)

```python
# config.py
ROLE_PERMISSIONS = {
    'hr_admin': [
        'manage_users',
        'view_all_employees',
        'edit_all_employees',
        'manage_payroll',
        'view_sensitive_data',
        'export_hr_data'
    ],
    'hr_manager': [
        'view_department_employees',
        'edit_department_employees',
        'manage_department_payroll',
        'approve_leaves',
        'view_department_reports'
    ],
    'department_manager': [
        'view_team_employees',
        'approve_team_leaves',
        'view_team_reports'
    ],
    'employee': [
        'view_own_profile',
        'edit_own_profile',
        'request_leave',
        'view_own_payslips'
    ],
    'contractor': [
        'view_own_profile',
        'update_timesheets'
    ]
}
```

---

## 4. Configuración de Integración con Frontend

### JavaScript Config (static/js/config.js)

```javascript
// config.js - Configuración del frontend
const APP_CONFIG = {
    // API Endpoints
    api: {
        users: {
            list: '/admin/users',
            add: '/admin/users/add',
            edit: (email) => `/admin/users/edit/${encodeURIComponent(email)}`,
            delete: (email) => `/admin/users/delete/${encodeURIComponent(email)}`
        },
        audit: '/admin/audit-log'
    },
    
    // Validaciones
    validation: {
        emailDomains: window.ALLOWED_EMAIL_DOMAINS || ['@yourcompany.com'],
        minPasswordLength: 8
    },
    
    // DataTables config
    dataTables: {
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json'
        },
        pageLength: 25,
        lengthMenu: [10, 25, 50, 100]
    },
    
    // Mensajes
    messages: {
        deleteConfirm: '¿Estás seguro de eliminar este usuario?',
        success: 'Operación completada exitosamente',
        error: 'Ocurrió un error. Por favor intenta nuevamente.'
    }
};

// Hacer accesible globalmente
window.APP_CONFIG = APP_CONFIG;
```

---

## 5. Configuración de Base de Datos

### SQLite (Desarrollo)

```sql
-- migrations/001_create_permissions_tables.sql

-- Tabla de usuarios y roles
CREATE TABLE IF NOT EXISTS user_permissions (
    user_email TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    department TEXT DEFAULT 'General',
    location TEXT DEFAULT 'HQ',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Tabla de auditoría
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_email TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('CREATE', 'UPDATE', 'DELETE')),
    target_user_email TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_user_role ON user_permissions(role);
CREATE INDEX IF NOT EXISTS idx_user_active ON user_permissions(is_active);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_admin ON audit_log(admin_email);
CREATE INDEX IF NOT EXISTS idx_audit_target ON audit_log(target_user_email);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);

-- Triggers para updated_at
CREATE TRIGGER IF NOT EXISTS update_user_timestamp 
AFTER UPDATE ON user_permissions
BEGIN
    UPDATE user_permissions 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE user_email = NEW.user_email;
END;
```

### PostgreSQL (Producción)

```sql
-- migrations/001_create_permissions_tables_postgres.sql

-- Tabla de usuarios y roles
CREATE TABLE IF NOT EXISTS user_permissions (
    user_email VARCHAR(255) PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(100) DEFAULT 'General',
    location VARCHAR(100) DEFAULT 'HQ',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Tabla de auditoría
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    admin_email VARCHAR(255) NOT NULL,
    action VARCHAR(10) NOT NULL CHECK(action IN ('CREATE', 'UPDATE', 'DELETE')),
    target_user_email VARCHAR(255) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_user_role ON user_permissions(role);
CREATE INDEX idx_user_active ON user_permissions(is_active);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_admin ON audit_log(admin_email);
CREATE INDEX idx_audit_target ON audit_log(target_user_email);
CREATE INDEX idx_audit_action ON audit_log(action);

-- Function para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para updated_at
CREATE TRIGGER update_user_timestamp 
BEFORE UPDATE ON user_permissions 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();
```

---

## 6. Configuración de Testing

### pytest.ini

```ini
[pytest]
# Configuración de pytest para el módulo de permisos

# Directorios de tests
testpaths = tests

# Patrones de archivos de test
python_files = test_*.py

# Patrones de clases de test
python_classes = Test*

# Patrones de funciones de test
python_functions = test_*

# Opciones de verbosidad
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing

# Markers personalizados
markers =
    unit: Tests unitarios
    integration: Tests de integración
    slow: Tests que tardan más tiempo
    security: Tests de seguridad

# Ignorar warnings específicos
filterwarnings =
    ignore::DeprecationWarning
```

### conftest.py (Fixtures compartidas)

```python
# tests/conftest.py
import pytest
from src.permissions_manager import PermissionsManager
from src.audit_logger import AuditLogger

@pytest.fixture
def permissions_manager():
    """Fixture con DB de prueba en memoria"""
    pm = PermissionsManager(db_path=':memory:')
    yield pm

@pytest.fixture
def audit_logger():
    """Fixture con audit logger de prueba"""
    al = AuditLogger(db_path=':memory:')
    yield al

@pytest.fixture
def sample_users():
    """Datos de usuarios de ejemplo para tests"""
    return [
        {'email': 'admin@test.com', 'role': 'admin_full'},
        {'email': 'manager@test.com', 'role': 'manager'},
        {'email': 'user@test.com', 'role': 'user'}
    ]
```

---

## 7. Configuración de Logging

### logging_config.py

```python
# src/logging_config.py
import logging
import logging.handlers
from pathlib import Path

def setup_logging(log_level='INFO'):
    """Configurar sistema de logging"""
    
    # Crear directorio de logs si no existe
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Formato de logs
    log_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo (rotación diaria)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / 'permissions.log',
        when='midnight',
        interval=1,
        backupCount=30
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.DEBUG if log_level == 'DEBUG' else logging.INFO)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

def get_logger(name):
    """Obtener logger para un módulo específico"""
    return logging.getLogger(name)
```

---

## 8. Resumen de Archivos de Configuración

```
your-project/
├── .env                        # Variables de entorno (NO commitear)
├── .env.example                # Ejemplo de variables de entorno
├── config.py                   # Configuración principal
├── pytest.ini                  # Configuración de tests
├── logging_config.py           # Configuración de logs
│
├── migrations/
│   ├── 001_create_tables.sql   # Script de creación de tablas
│   └── 002_add_indexes.sql     # Optimizaciones
│
└── static/js/
    └── config.js               # Configuración del frontend
```

**Próximos pasos**:
1. Copiar archivos de configuración apropiados
2. Personalizar roles según tu proyecto
3. Configurar variables de entorno
4. Ejecutar migraciones de base de datos
5. Iniciar implementación según plan principal

---

**📌 Nota**: Estos son ejemplos de referencia. Adapta según las necesidades específicas de tu proyecto.
