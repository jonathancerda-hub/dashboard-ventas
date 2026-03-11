# Code Review Arquitectónico — Dashboard Ventas
## Análisis Senior: SOLID, Seguridad, Rendimiento, Mantenibilidad

---

## Resumen Ejecutivo

**Puntuación General: 6.2/10**

| Área | Puntuación | Estado |
|------|-----------|--------|
| Principios SOLID | 5/10 | ⚠️ Crítico |
| Seguridad OWASP | 6/10 | ⚠️ Mejoras necesarias |
| Legibilidad | 7/10 | ✅ Aceptable |
| Nomenclatura | 7/10 | ✅ Buena |
| Documentación | 6/10 | ⚠️ Incompleta |
| Patrones de Diseño | 5/10 | ⚠️ Débiles |
| APIs REST | 5/10 | ⚠️ No es REST puro |
| Optimización Datos | 4/10 | 🔴 Crítico |
| Validación de Inputs | 4/10 | 🔴 Crítico |
| Caching | 2/10 | 🔴 Inexistente |
| Microservicios | 3/10 | 🔴 No escalable |

---

## 1. Principios SOLID

### 1.1 Single Responsibility Principle (SRP) — 3/10

**❌ CRÍTICO**: `app.py` viola SRP masivamente.

```python
# app.py - una sola clase/archivo de ~2000 líneas con:
# - 15 rutas diferentes
# - Lógica de autenticación
# - Cálculos de KPIs complejos
# - Transformación de datos
# - Manejo de middleware
# - Permisos dispersos
# - Generación de reportes
# - Lógica de validación
```

**Hallazgos específicos**:

- `/dashboard` contiene ~500 líneas de cálculos y transformaciones que deberían estar en servicios.
- Funciones auxiliares (`get_meses_del_año`, `normalizar_linea_comercial`, `limpiar_nombre_atrevia`) deberían estar en módulo separado.
- Lógica de permisos (`admin_users` arrays) aparece en 7 rutas distintas.

**Recomendación**:

```plaintext
Reestructurar a:
app/
  ├── main.py (solo setup Flask)
  ├── routes/
  │   ├── auth.py (login, oauth, logout)
  │   ├── dashboard.py (/, /dashboard, /dashboard_linea)
  │   ├── metas.py (/meta, /metas_vendedor)
  │   ├── exports.py (/export/*)
  │   └── analytics.py (/analytics)
  ├── services/
  │   ├── sales_service.py (KPIs, agregaciones)
  │   ├── permission_service.py (control de acceso)
  │   └── normalization_service.py (limpieza de datos)
  └── middleware/
      └── analytics_middleware.py
```

### 1.2 Open/Closed Principle (OCP) — 4/10

**⚠️ DÉBIL**: Código frágil ante cambios.

```python
# Problema: cambiar lógica de permisos requiere editar múltiples rutas
admin_users = ["jonathan.cerda@agrovetmarket.com", "janet.hueza@agrovetmarket.com", ...]
# Esto aparece literalmente en 7 rutas diferentes
```

**Mejor enfoque**:

```python
# config/roles.py
ROLE_CONFIG = {
    'admin': {
        'emails': ['jonathan.cerda@agrovetmarket.com'],
        'routes': ['sales', 'meta', 'metas_vendedor', 'analytics', 'export_*']
    },
    'viewer': {
        'emails': ['generic_users@company.com'],
        'routes': ['dashboard', 'dashboard_linea']
    }
}

# decorators.py
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not has_role(session.get('username'), required_role):
                flash(f'Requiere rol: {required_role}', 'warning')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# Uso:
@app.route('/sales')
@require_role('admin')
def sales():
    ...
```

### 1.3 Liskov Substitution Principle (LSP) — 6/10

**⚠️ Aceptable pero con deuda**:

- `_StubManager` fallback está bien, pero no implementa contrato claro.
- `AnalyticsDB` tiene duplicación de métodos (SQLite vs PostgreSQL).

**Mejor enfoque**:

```python
from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    @abstractmethod
    def get_sales_lines(self, **kwargs) -> List[Dict]: pass
    
    @abstractmethod
    def get_all_sellers(self) -> List[Dict]: pass

class OdooManager(DataManagerInterface):
    ... # implementación

class StubManager(DataManagerInterface):
    def get_sales_lines(self, **kwargs):
        return []
    ... # implementación stub
```

### 1.4 Interface Segregation Principle (ISP) — 4/10

**❌ CRÍTICO**: Métodos gordos sin segregación clara.

```python
# supabase_manager.py - 513 líneas, 15+ métodos públicos
# Mezcla:
#  - Operaciones de metas (guardar_meta_venta, obtener_metas_mes)
#  - Operaciones de equipos (read_equipos, write_equipos)
#  - Operaciones de vendedores (guardar_meta_vendedor, obtener_metas_vendedor)
#  - Métodos legacy de GoogleSheets (read_metas_por_linea, write_metas_por_linea)
```

**Refactor sugerido**:

```python
# interfaces.py
class MetasRepository(ABC):
    @abstractmethod
    def save_meta(self, mes: str, linea: str, meta: float) -> None: pass
    @abstractmethod
    def get_metas(self, mes: str) -> Dict: pass

class EquiposRepository(ABC):
    @abstractmethod
    def assign_vendors(self, equipo_id: str, vendor_ids: List[int]) -> None: pass
    @abstractmethod
    def get_equipos(self) -> Dict: pass

# implementations.py
class SupabaseMetasRepository(MetasRepository):
    def __init__(self, supabase_client):
        self.client = supabase_client
    # solo métodos de metas

class SupabaseEquiposRepository(EquiposRepository):
    def __init__(self, supabase_client):
        self.client = supabase_client
    # solo métodos de equipos
```

### 1.5 Dependency Inversion Principle (DIP) — 3/10

**❌ CRÍTICO**: Dependencias hardcodeadas.

```python
# Actual (acoplado):
data_manager = OdooManager()
supabase_manager = SupabaseManager()
analytics_db = AnalyticsDB()

@app.route('/dashboard')
def dashboard():
    sales_data = data_manager.get_sales_lines(...)  # Depende directamente de instancia

# Mejor (inyección):
app.container = {
    'data_manager': OdooManager(),
    'supabase_manager': SupabaseManager(),
    'analytics_db': AnalyticsDB()
}

@app.route('/dashboard')
def dashboard():
    container = current_app.container
    service = SalesService(container['data_manager'], container['supabase_manager'])
    sales_data = service.get_sales_with_metas()
```

---

## 2. Seguridad OWASP Top 10 — Puntuación: 6/10

### 2.1 A01: Broken Authentication — 5/10

**⚠️ MEJORAS NECESARIAS**:

```python
# ✅ Buen: OAuth2 delegado a Google
# ❌ Malo: Whitelist de emails en JSON local y en .env

# Problema 1: hardcoding de admin_users
admin_users = ["jonathan.cerda@agrovetmarket.com", ...]  # Línea 282, 357, 1223...
# Cambiar requiere redeploy

# Problema 2: No hay expiración de sesiones
app.config['PERMANENT_SESSION_LIFETIME'] = ...  # NO CONFIGURADO
app.config['SESSION_COOKIE_SECURE'] = ...      # NO CONFIGURADO
app.config['SESSION_COOKIE_HTTPONLY'] = ...    # NO CONFIGURADO
app.config['SESSION_COOKIE_SAMESITE'] = ...    # NO CONFIGURADO

# Problema 3: Token Google nunca se refresca
token = google.authorize_access_token()  # Línea 210
# Sin refresh mechanism
```

**Recomendaciones**:

```python
# config/security.py
app.config.update(
    SESSION_COOKIE_SECURE=True,      # Solo HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # No accesible desde JS
    SESSION_COOKIE_SAMESITE='Strict', # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    REMEMBER_COOKIE_SECURE=True,
    REMEMBER_COOKIE_HTTPONLY=True
)

# auth_service.py
def verify_session():
    """Validar sesión no ha caducado"""
    if 'login_time' in session:
        elapsed = datetime.now() - session['login_time']
        if elapsed > timedelta(hours=8):
            session.clear()
            return False
    return True

@app.before_request
def check_session():
    if 'username' in session and not verify_session():
        session.clear()
        flash('Tu sesión ha expirado.', 'warning')
        return redirect(url_for('login'))
```

### 2.2 A02: Cryptographic Failures — 7/10

**✅ ACEPTABLE pero con claros**:

```python
# ✅ Buen: OAuth2 usa HTTPS
# ✅ Buen: No guarda passwords
# ⚠️ Débil: Credenciales Odoo en .env sin encriptación
# ⚠️ Débil: Supabase key en .env como texto plano

# Problema: SECRET_KEY puede ser débil
app.secret_key = os.getenv('SECRET_KEY')
# Si SECRET_KEY = "simple_password", es inseguro

# Validación actual de SECRET_KEY:
# NINGUNA - solo confía en .env
```

**Recomendaciones**:

```python
# security/encryption.py
from cryptography.fernet import Fernet
import os

class CredentialManager:
    def __init__(self):
        # En producción, obtener de AWS Secrets Manager / Azure Key Vault
        key = os.getenv('ENCRYPTION_KEY')  # Debe ser base64
        self.cipher = Fernet(key)
    
    def get_odoo_password(self):
        encrypted = os.getenv('ODOO_PASSWORD_ENCRYPTED')
        return self.cipher.decrypt(encrypted).decode()

# En .env solo guardar:
# ENCRYPTION_KEY=<base64_key_from_vault>
# ODOO_PASSWORD_ENCRYPTED=<encrypted_password>
# NO guardar passwords en plaintext
```

### 2.3 A03: Injection — 4/10

**❌ CRÍTICO**:

```python
# SQL Injection risk en analytics_db.py
# Problema: concatenación de strings en SQL

if self.use_sqlite:
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM page_visits
        WHERE visit_timestamp >= datetime('now', '-' || ? || ' days')
    """, (days,))  # ✅ Parametrizado (bien)

else:
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM page_visits
        WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
    """, (days,))  # ❌ Interpolación directa (VULNERABLE)
```

**Fix inmediato**:

```python
# MALO (vulnerable):
cursor.execute(f"SELECT * FROM sales WHERE id = {sale_id}")

# BUENO:
cursor.execute("SELECT * FROM sales WHERE id = %s", (sale_id,))

# Auditar todo analytics_db.py para encontrar interpolaciones:
# - NOW() - INTERVAL '%s days'  ← VULNERABLE
# - EXTRACT(HOUR FROM ...) ← OK
```

### 2.4 A04: Insecure Design — 6/10

**⚠️ MEJORAS NECESARIAS**:

```python
# ❌ No hay rate limiting
# ❌ No hay mecanismo anti-CSRF visible
# ❌ No hay validación de CORS
# ❌ No hay logs de seguridad (solo prints)

# En app.py:
@app.route('/authorize')
def authorize():
    # Ningún rate limiting detectado
    token = google.authorize_access_token()  # Vulnerable a ataques password spray
```

**Recomendaciones**:

```python
# security/rate_limit.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# En app.py
app.register_blueprint(..., url_prefix='/api')

limiter.limit("5 per minute")(authorize)  # Máx 5 intentos/minuto
limiter.limit("5 per day")(login)        # Máx 5 logins/día por IP

# Anti-CSRF
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

### 2.5 A06: Vulnerable & Outdated Components — 10/10

**✅ RESUELTO (11/marzo/2026)**:

**Auditoría realizada con pip-audit**:
```bash
pip-audit  # ✅ No known vulnerabilities found
```

**Componentes actualizados**:

```
# Core Security Updates
Authlib==1.6.7         ✅ (actualizado desde 1.3.1, fixes 5 CVEs)
Flask==3.1.3           ✅ (actualizado desde 3.1.1, fixes CVE-2026-27205)
Werkzeug==3.1.6        ✅ (actualizado desde 3.1.3, fixes 3 CVEs)
urllib3==2.6.3         ✅ (actualizado desde 2.5.0, fixes 3 CVEs)

# Data & Dependencies
pandas==2.2.3          ✅ (downgrade controlado desde 2.3.1 por estabilidad)
pillow==12.1.1         ✅ (actualizado desde 11.3.0, fixes CVE-2026-25990)
pyasn1==0.6.2          ✅ (actualizado desde 0.6.1, fixes CVE-2026-23490)
psycopg2-binary==2.9.10 ⚠️ Mantener por estabilidad (considerar psycopg3 en Q2)

# Build Tools
pip==26.0.1            ✅ (actualizado desde 24.0, fixes 2 CVEs)
setuptools==82.0.1     ✅ (actualizado desde 65.5.0, fixes múltiples PYSEC)
supabase==2.14.0       ✅ Actualizado
```

**Reducción de vulnerabilidades**: 19 CVEs → 0 CVEs ✅

**Mantenimiento continuo**:
- ✅ Auditoría trimestral programada con `pip-audit`
- ✅ Verificación de dependencias con `safety check`
- ⚠️ Considerar migración a psycopg3 en próximo trimestre

### 2.6 A07: Identification & Authentication Failures — 6/10

**⚠️ DETALLES**:

```python
# ❌ PROBLEMA 1: Email verificado de Google, pero no vinculado a LDAP corp
# El sistema confía en que Google validó el email, pero ¿qué si:
# - Usuario deja la empresa pero mantiene Google Account?
# - Email corporativo es tomado por otra persona?

# ❌ PROBLEMA 2: No hay verificación de dominio
# Cualquiera con @anything.com en whitelist puede entrar
if email in allowed_emails:  # allowed_emails podría tener "*@company.com"
    session['username'] = email

# ❌ PROBLEMA 3: Sin MFA
# Recomendación: integrar Google Authenticator o SMS 2FA
```

**Mejor implementación**:

```python
# security/mfa.py
import pyotp
import qrcode
from io import BytesIO

class MFAService:
    def __init__(self):
        self.issuer = "Dashboard Ventas"
    
    def generate_secret(self, email: str) -> str:
        """Genera secret TOTP único"""
        secret = pyotp.random_base32()
        # Guardar en BD:
        # mfa_setup table: email, secret, verified=False
        return secret
    
    def verify_token(self, email: str, token: str) -> bool:
        """Verifica código TOTP"""
        secret = get_mfa_secret(email)
        totp = pyotp.TOTP(secret)
        return totp.verify(token)

# En authorize():
if email in allowed_emails:
    if has_mfa_enabled(email):
        session['temp_email'] = email
        return redirect(url_for('mfa_verify'))
    else:
        session['username'] = email
        return redirect(url_for('dashboard'))
```

### 2.7 A08: Software & Data Integrity Failures — 5/10

**⚠️ CRÍTICO**:

```python
# ❌ No hay verificación de integridad de datos Supabase
# Si un atacante modifica datos en tránsito... no habría forma de detectarlo

# ❌ No hay versionamiento de datos sensibles
# Si alguien edita metas maliciosamente, no hay auditoría

# ❌ No hay firma de datos
```

**Recomendaciones**:

```python
# models/audit.py
class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(Integer, PK)
    table_name = Column(String)
    resource_id = Column(String)
    action = Column(String)  # INSERT, UPDATE, DELETE
    old_values = Column(JSON)
    new_values = Column(JSON)
    user_email = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)

def log_audit(table, resource_id, action, old, new):
    entry = AuditLog(
        table_name=table,
        resource_id=resource_id,
        action=action,
        old_values=old,
        new_values=new,
        user_email=session.get('username'),
        ip_address=request.remote_addr
    )
    db.session.add(entry)
    db.session.commit()

# En metas_vendedor
def guardar_meta_vendedor(...):
    old = get_current_meta(vendedor_id, mes)
    # ... guardar nueva meta
    log_audit('metas_vendedor', f"{vendedor_id}_{mes}", 'UPDATE', old, new)
```

### 2.8 A09: Logging & Monitoring Failures — 4/10

**❌ CRÍTICO**:

```python
# Actual:
print(f"⚠️ No se pudo inicializar OdooManager: {e}")  # print() no es logging
print(f"❌ Error en la conexión a Odoo: {e}")        # se pierde si no está en consola

# Mejor:
import logging
logger = logging.getLogger(__name__)

try:
    data_manager = OdooManager()
except Exception as e:
    logger.error(f"OdooManager init failed: {e}", exc_info=True)

# Sin logs centralizados, sin alertas, sin trazabilidad
```

**Implementación recomendada**:

```python
# config/logging.py
import logging
from logging.handlers import RotatingFileHandler
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.name,
            'user': session.get('username', 'anonymous'),
            'ip': request.remote_addr if has_request_context() else 'N/A'
        })

# Setup
handler = RotatingFileHandler('logs/app.log', maxBytes=10MB, backupCount=10)
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)

# En producción: enviar a ELK Stack, Datadog, o CloudWatch
```

### 2.9 A10: Server-Side Request Forgery — 6/10

**⚠️ DÉBIL pero mitigado**:

```python
# El riesgo es bajo porque:
# - No hace requests a URLs controladas por usuario
# - Usa credenciales fijas para Odoo y Supabase

# Pero si en el futuro alguien añade algo como:
@app.route('/export-from-url')
def export_from_url():
    url = request.args.get('url')  # VULNERABLE: SSRF
    data = requests.get(url).json()  # Podría hacer request a localhost:5432
```

**Prevención general**:

```python
# security/ssrf_protection.py
import requests
from urllib.parse import urlparse

ALLOWED_HOSTS = ['api.example.com', 'odoo.example.com']
BLOCKED_RANGES = [
    '127.0.0.0/8',    # localhost
    '10.0.0.0/8',     # private
    '172.16.0.0/12',  # private
    '192.168.0.0/16'  # private
]

def safe_request(url: str, **kwargs):
    parsed = urlparse(url)
    
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"Host {parsed.hostname} not whitelisted")
    
    # Check IP range
    ip = socket.gethostbyname(parsed.hostname)
    if is_private_ip(ip):
        raise ValueError(f"Private IP detected: {ip}")
    
    return requests.get(url, **kwargs, timeout=5)
```

---

## 3. Validación de Inputs — Puntuación: 4/10

### 3.1 Ejemplos de vulnerabilidades actuales:

```python
# ❌ PROBLEMA 1: Sin validación de tipos en request.args
mes_seleccionado = request.args.get('mes', fecha_actual.strftime('%Y-%m'))
año_seleccionado = request.args.get('año', str(fecha_actual.year))
try:
    año_seleccionado = int(año_seleccionado)  # Validación tardía
except (ValueError, TypeError):
    año_seleccionado = fecha_actual.year

# ❌ PROBLEMA 2: Sin límites de valores
limit=1000  # ¿Qué si usuario envía ?limit=999999999?
linea_id = None
if linea_id:
    try:
        linea_id = int(linea_id)  # Sin validación de rango
    except (ValueError, TypeError):
        linea_id = None

# ❌ PROBLEMA 3: Confianza ciega en datos de Odoo
for sale in sales_data:
    nombre_linea_original = linea_comercial[1].upper()  # ¿Qué si [1] no existe?
    linea_nombre = normalizar_linea_comercial(nombre_linea_original)
    if not linea_nombre:  # Sin validación
        nombre_linea_venta = 'DESCONOCIDA'

# ❌ PROBLEMA 4: Sin sanitización en render
<td>{{ linea.nombre }}</td>  # Vulnerable si viene HTML desde DB
# Aunque Jinja2 por defecto escapa, es mejor ser explícito

# ❌ PROBLEMA 5: Excel injection
# Si datos Odoo contienen "=cmd|'/c calc'!A1", Excel lo ejecuta
for row in sales_data:
    df[row] = row.get('name')  # Sin sanitización
```

### 3.2 Esquema de validación recomendado:

```python
# validation/schemas.py
from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import datetime

class DashboardFilterSchema(BaseModel):
    mes: str = Field(..., regex=r'^\d{4}-\d{2}$')
    año: int = Field(..., ge=2020, le=2100)
    dia_fin: Optional[int] = Field(None, ge=1, le=31)
    
    @field_validator('mes')
    def validate_mes_exists(cls, v):
        year, month = map(int, v.split('-'))
        if not (1 <= month <= 12):
            raise ValueError('Invalid month')
        return v

class MetaVentasSchema(BaseModel):
    mes: str = Field(..., regex=r'^\d{4}-\d{2}$')
    linea_comercial: str = Field(..., min_length=1, max_length=100)
    meta_total: float = Field(..., ge=0, le=10_000_000)
    meta_ipn: Optional[float] = Field(None, ge=0)

# En rutas:
@app.route('/dashboard')
def dashboard():
    try:
        filters = DashboardFilterSchema(
            mes=request.args.get('mes'),
            año=request.args.get('año'),
            dia_fin=request.args.get('dia_fin')
        )
    except ValidationError as e:
        flash(f'Parámetros inválidos: {e}', 'danger')
        return redirect(url_for('dashboard'))
    
    # Uso seguro de filters
    sales_data = data_manager.get_sales_lines(
        date_from=f"{filters.año}-{filters.mes}-01",
        ...
    )
```

---

## 4. Optimización de Consultas de Datos — Puntuación: 4/10

### 4.1 Problemas identificados:

```python
# ❌ PROBLEMA 1: N+1 Queries
for sale in sales_data:
    user_info = sale.get('invoice_user_id')  # Ya viene en sale
    # Pero si queremos detalles del vendedor...
    vendedor = get_vendedor_details(user_info[0])  # N queries!

# ❌ PROBLEMA 2: Sin paginación
def get_sales_lines(self, limit=10000):  # Trae TODOS los registros
    sales = self.models.execute_kw(
        self.db, self.uid, self.password, 'sale.order.line', 'search_read',
        [filters],
        {'fields': [...], 'limit': 10000}  # Hardcoded 10000
    )
    return sales

# ❌ PROBLEMA 3: Sin índices de BD
# En analytics_db.py se crean índices pero hay queries sin ellos
cursor.execute("""
    SELECT ... FROM page_visits
    WHERE visit_timestamp >= datetime('now', '-' || ? || ' days')
    AND user_email != '...'
""")  # No hay índice en (visit_timestamp, user_email)

# ❌ PROBLEMA 4: Múltiples llamadas a la misma data
# En /dashboard:
# 1. supabase_manager.read_metas_por_linea()  ← Llamada 1
# 2. data_manager.get_sales_lines(...)        ← Llamada 2
# 3. data_manager.get_all_sellers()           ← Llamada 3
# Si hay 100 usuarios viendo dashboard simultáneamente = 300 queries
# Sin cache, sin dedup

# ❌ PROBLEMA 5: pandas cargando DataFrames grandes en memoria
df = pd.DataFrame(sales_data)  # Si sales_data = 1M registros
df.rename(columns={...})
df.to_excel(...)  # Todo en RAM
```

### 4.2 Optimización inmediata:

```python
# database/query_optimize.py
class QueryCache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get_or_fetch(self, key, fetcher):
        """Fetch data o devolver del cache"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
        
        data = fetcher()
        self.cache[key] = (data, time.time())
        return data

# Usage:
query_cache = QueryCache(ttl_seconds=600)

@app.route('/dashboard')
def dashboard():
    meses = request.args.get('mes')
    
    # Cache con clave: mes + año actual
    cache_key = f"metas_mes_{meses}"
    metas = query_cache.get_or_fetch(
        cache_key,
        lambda: supabase_manager.read_metas_por_linea()
    )
    
    sellers_cache_key = "all_sellers"
    sellers = query_cache.get_or_fetch(
        sellers_cache_key,
        lambda: data_manager.get_all_sellers()
    )

# Invalidar cache cuando cambian datos
def guardar_metas(...):
    supabase_manager.write_metas(...)
    query_cache.invalidate(f"metas_mes_*")  # Patrón wildcard
```

### 4.3 Índices necesarios en Supabase:

```sql
-- metas_ventas_2026
CREATE INDEX IF NOT EXISTS idx_metas_mes ON metas_ventas_2026(mes);
CREATE INDEX IF NOT EXISTS idx_metas_linea ON metas_ventas_2026(linea_comercial);
CREATE INDEX IF NOT EXISTS idx_metas_mes_linea ON metas_ventas_2026(mes, linea_comercial);

-- metas_vendedor_2026
CREATE INDEX IF NOT EXISTS idx_meta_vendedor_mes ON metas_vendedor_2026(mes, vendedor_id);
CREATE INDEX IF NOT EXISTS idx_meta_vendedor_linea ON metas_vendedor_2026(mes, linea_comercial);

-- equipos_vendedores
CREATE INDEX IF NOT EXISTS idx_equipos_equipo ON equipos_vendedores(equipo_id);
CREATE INDEX IF NOT EXISTS idx_equipos_vendedor ON equipos_vendedores(vendedor_id);

-- page_visits (analytics)
CREATE INDEX IF NOT EXISTS idx_visits_email_timestamp ON page_visits(user_email, visit_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_visits_page_date ON page_visits(page_url, DATE(visit_timestamp));
```

---

## 5. Caching Estratégico — Puntuación: 2/10

### 5.1 Estado actual:

```python
# ❌ config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  ← Deshabilita cache
# ❌ config['TEMPLATES_AUTO_RELOAD'] = True    ← Recompila templates siempre
# ❌ Sin Cache-Control headers
# ❌ Sin ETags
# ❌ Sin Redis/Memcached
```

### 5.2 Estrategia recomendada:

```python
# config/caching.py
from flask_caching import Cache
from functools import wraps
import hashlib

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'dashboard_'
})

# Decorador custom para cachear respuestas de rutas
def cached_route(timeout=300):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Generar cache key de parámetros
            cache_key = f"{f.__name__}_{hash_args(request.args)}"
            
            # Validar que es GET y no es admin
            if request.method != 'GET' or is_admin_user():
                return f(*args, **kwargs)
            
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            return result
        
        return decorated
    return decorator

# Uso:
@app.route('/dashboard')
@cached_route(timeout=600)
def dashboard():
    # Cached por 10 minutos
    ...

# En handlers de POST (cambios de datos)
@app.route('/meta', methods=['POST'])
def meta():
    # ... guardar datos
    cache.delete_pattern(f"dashboard_*")  # Invalidar caché relacionado
    cache.delete_pattern(f"sales_*")
    flash('Metastados', 'success')
    return redirect(url_for('dashboard'))

# HTTP Cache Headers
@app.after_request
def set_cache_headers(response):
    if request.path.startswith('/static/'):
        response.cache_control.max_age = 31536000  # 1 año para assets
        response.cache_control.public = True
        response.set_etag(hashlib.md5(response.get_data()).hexdigest())
    elif request.method == 'GET' and response.status_code == 200:
        response.cache_control.max_age = 300  # 5 minutos para content
        response.cache_control.private = True  # No cachear en proxies
    else:
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
    
    return response
```

---

## 6. Headers de Seguridad — Puntuación: 3/10

### 6.1 Headers faltantes críticos:

```python
# ❌ Sin X-Frame-Options
# ❌ Sin X-Content-Type-Options
# ❌ Sin Strict-Transport-Security
# ❌ Sin Content-Security-Policy
# ❌ Sin X-XSS-Protection
# ❌ Sin Referrer-Policy
```

### 6.2 Implementación completa:

```python
# middleware/security_headers.py
@app.after_request
def set_security_headers(response):
    """Añade headers de seguridad a todas las respuestas"""
    
    # Prevenir clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Prevenir MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # HSTS: fuerza HTTPS por 1 año
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains; preload'
    
    # CSP: especifica origen de scripts
    response.headers['Content-Security-Policy'] = "; ".join([
        "default-src 'self'",
        "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "style-src 'self' https://cdn.jsdelivr.net",
        "img-src 'self' data: https:",
        "font-src 'self' https:",
        "connect-src 'self' https://accounts.google.com",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'"
    ])
    
    # Evitar que navegador infiera tipos
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS protection (legacy, pero recomendado)
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Controlar Referer
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permisos de Features (Permissions Policy)
    response.headers['Permissions-Policy'] = \
        'geolocation=(), microphone=(), camera=()'
    
    return response
```

---

## 7. Patrones de Diseño — Puntuación: 5/10

### 7.1 Patrones identificados (mal implementados):

```python
# ❌ Strategy Pattern (incompleto)
# Hay adaptadores Odoo/Supabase pero sin interfaz clara

# ❌ Factory Pattern (ausente)
# No hay factory para crear managers

# ❌ Repository Pattern (parcial)
# SupabaseManager actúa como repo pero sin abstracción

# ❌ Service Locator (anti-patrón)
# data_manager global en app.py
data_manager = OdooManager()  # Acoplamiento global
```

### 7.2 Refactor a patrones SOLID:

```python
# patterns/factory.py
class ManagerFactory:
    @staticmethod
    def create_data_manager() -> DataManagerInterface:
        strategy = os.getenv('DATA_SOURCE', 'odoo')
        
        if strategy == 'odoo':
            return OdooManager()
        elif strategy == 'mock':
            return MockDataManager()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    @staticmethod
    def create_persistence_manager() -> PersistenceInterface:
        return SupabaseManager()

# patterns/service_locator.py (MEJOR: Dependency Injection)
from typing import Dict
from abc import ABC

class Container:
    """Simple DI Container"""
    def __init__(self):
        self._services: Dict[str, any] = {}
    
    def register(self, name: str, service):
        self._services[name] = service
    
    def get(self, name: str):
        if name not in self._services:
            raise KeyError(f"Service '{name}' not registered")
        return self._services[name]

# app.py setup
container = Container()
container.register('data_manager', OdooManager())
container.register('persistence', SupabaseManager())
container.register('analytics', AnalyticsDB())

# En rutas
@app.route('/dashboard')
def dashboard():
    data_manager = container.get('data_manager')
    persistence = container.get('persistence')
    
    service = SalesService(data_manager, persistence)
    kpis = service.calculate_kpis(mes_seleccionado)
```

---

## 8. APIs REST vs Monolito Server-Side — Puntuación: 5/10

### 8.1 Análisis actual:

```
Arquitectura actual:
Flask → Jinja2 templates → HTML → JS (mínimo)

Problemas:
- No es API REST puro
- Render server-side ralentiza inicialización
- Difícil de escalar frontend
- Sin separación clara backend/frontend
```

### 8.2 Recomendación: API GraphQL/REST + SPA

```python
# Para mantener monolito pero mejorar:

# 1. Crear API REST interna
from flask_restful import Api, Resource

api = Api(app)

class SalesAPI(Resource):
    @require_auth
    @require_role('viewer')
    def get(self):
        """GET /api/sales?mes=2026-03&linea=PETMEDICA"""
        mes = request.args.get('mes')
        linea = request.args.get('linea')
        
        return {
            'data': sales_service.get_sales(mes, linea),
            'meta': {
                'total': sales_service.get_total(mes, linea),
                'cached': False
            }
        }, 200

class MetasAPI(Resource):
    @require_auth
    @require_role('admin')
    def post(self):
        """POST /api/metas"""
        data = request.get_json()
        
        # Validar
        try:
            schema = MetaVentasSchema(**data)
        except ValidationError as e:
            return {'error': e.errors()}, 422
        
        # Guardar
        persistence.save_meta(schema.dict())
        return {'status': 'ok'}, 201

api.add_resource(SalesAPI, '/api/sales')
api.add_resource(MetasAPI, '/api/metas')

# 2. API documentation
from flasgger import Swagger
swagger = Swagger(app)

# Anotación en endpoints
@app.route('/api/sales')
def get_sales():
    """
    ---
    get:
      summary: Obtener ventas
      parameters:
        - in: query
          name: mes
          schema:
            type: string
            pattern: '^\d{4}-\d{2}$'
      responses:
        200:
          description: Ventas obtenidas
          schema:
            type: object
            properties:
              data:
                type: array
              meta:
                type: object
    """
```

---

## 9. Nomenclatura y Convenciones — Puntuación: 7/10

### 9.1 ✅ BUEN: Nombres claros generalmente

```python
PERU_TZ = pytz.timezone(...)  # Claro
get_meses_del_año()           # Descriptivo
normalizar_linea_comercial()  # Propósito obvio
```

### 9.2 ⚠️ MEJORABLE:

```python
# Malo:
metas_ventas_2026
metas_vendedor_2026
metas_por_linea
metas_ipn_del_mes_raw
# Confuso: ¿por qué "_2026" está hardcoded?

# Mejor:
sales_goals        # o sales_targets
sales_goals_raw    # si es sin procesar
sales_goals_by_line
new_product_goals  # mejor que meta_ipn

# Malo:
datos_lineas
datos_ecommerce
datos_productos
# Poco específico

# Mejor:
line_sales_summary
ecommerce_team_performance
top_products_by_revenue

# Malo en variables globales:
admin_users = [...]  # aparece 7 veces con contenidos diferentes

# Mejor:
ADMIN_EMAILS = {...}  # una sola fuente
ALLOWED_EMAILS = {...}

# Malo:
def limpiar_nombre_atrevia(nombre_producto):
    # Función muy específica de dominio
    
# Mejor:
class ProductNameNormalizer:
    def normalize(self, name: str, product_line: str) -> str:
        # Genérico, reutilizable
```

---

## 10. Documentación — Puntuación: 6/10

### 10.1 ✅ Buen:

```python
def guardar_meta_venta(self, mes: str, linea_comercial: str, 
                       meta_total: float, meta_ipn: float = None):
    """
    Guarda o actualiza una meta de venta general por línea comercial
    
    Args:
        mes: Formato 'YYYY-MM' (ej: '2026-01')
        linea_comercial: Nombre de la línea comercial
        meta_total: Meta total del mes
        meta_ipn: Meta de productos nuevos (opcional)
    
    Returns:
        Dict con los datos guardados o None si hay error
    """
    # BIEN: Docstring con Args, Returns
```

### 10.2 ❌ Falta:

```python
# Sin docstring/comentarios
def normalizar_linea_comercial(nombre_linea):
    # No explica por qué GENVET → TERCEROS
    if 'GENVET' in nombre_upper or 'MARCA BLANCA' in nombre_upper:
        return 'TERCEROS'

# Sin README.md
# Sin CONTRIBUTING.md
# Sin API docs
# Sin architecture decision log (ADR)

# Recomendación: añadir
* README.md con setup/deploy
* docs/API.md con endpoints
* docs/ARCHITECTURE.md (ya hecho)
* docs/SECURITY.md con checklist OWASP
* docs/PERFORMANCE.md con índices, caching
* docs/DEVELOPMENT.md con local setup
```

---

## 11. Microservicios vs Monolito — Puntuación: 3/10

### 11.1 ¿Debe ser microservicios?

**Análisis**:

```
Criterio                          | Estado
----------------------------------|----------------------------
Número de desarrolladores         | 1-3: Monolito está bien
Requisitos de escalability        | ALGUNOS (Odoo lento)
Ciclos de release independientes  | NO: mismo ritmo
Requisitos de disponibilidad      | MEDIUM: 8-5
Complejidad del dominio           | MEDIUM: 5 bounded contexts
Tecnologías heterogéneas          | NO: Python puro
Latencia entre servicios          | SÍ: Odoo ~ 1-2s

VEREDICTO: Monolito es correcto AHORA, pero considerar
           desacoplamiento en: Odoo adapter, Analytics
```

### 11.2 Si escala en futuro:

```plaintext
dashboard-monolith (hoy)
    ↓ Refactor
├── api-gateway (Flask)
├── sales-service (Odoo wrapper)
├── metas-service (Supabase)
├── analytics-service (PostgreSQL)
└── auth-service (OAuth)

Beneficios:
- sales-service puede escalarse independientemente (caché, queue)
- analytics-service puede tener BD separada
- auth-service puede ser más restrictivo

Costos:
- Network overhead (ms adicionales)
- Complejidad de deployment
- Data consistency (eventual)
```

---

## 12. Recomendaciones Priorizadas

### 🔴 CRÍTICO (semanas 1-2):

1. **Seguridad**:
   - [ ] Implementar rate limiting en /authorize
   - [ ] Fijar session cookies (SECURE, HTTPONLY, SAMESITE)
   - [ ] Audit y fix SQL injection en analytics (NOW() - INTERVAL)
   - [ ] Añadir validación de inputs con Pydantic

2. **Datos**:
   - [ ] Crear índices en Supabase
   - [ ] Implementar Redis cache para metas/vendedores
   - [ ] Implementar query cache para Odoo

### 🟠 IMPORTANTE (semanas 3-4):

3. **Arquitectura**:
   - [ ] Extraer managers a directorios separados
   - [ ] Centralizar autorización en decorators
   - [ ] Crear supabase_manager por interfaz (Metas, Equipos)
   - [ ] Modularizar app.py con blueprints

4. **Observabilidad**:
   - [ ] Reemplazar print() por logging
   - [ ] Añadir JSON logging para ELK
   - [ ] Implementar auditoría de cambios sensibles

### 🟡 IMPORTANTE (mes 2):

5. **Frontend**:
   - [ ] Añadir rate limiting en formularios
   - [ ] CSRF tokens en todos los forms
   - [ ] Validación en cliente + servidor (duplicación intencionada)

6. **Testing**:
   - [ ] Tests de seguridad (OWASP)
   - [ ] Tests de queries (performance)
   - [ ] Tests de validación

---

## 13. Checklist de Auditoría Final

```markdown
# SOLID
- [ ] Cada clase tiene una responsabilidad
- [ ] Código abierto para extensión, cerrado para modificación
- [ ] Interfaces bien definidas
- [ ] Inyección de dependencias (no singletons globales)

# Seguridad
- [ ] Sin SQL injection
- [ ] Rate limiting
- [ ] Input validation (Pydantic)
- [ ] Sessions seguras (SECURE, HTTPONLY)
- [ ] Headers OWASP (CSP, HSTS, X-Frame-Options)
- [ ] Auditoría de cambios sensibles
- [ ] Encriptación de secretos (no plaintext en .env)

# Performance
- [ ] Índices de BD
- [ ] Cache de relaciones N+1
- [ ] Compresión de responses (gzip)
- [ ] Lazy loading de datos

# Mantenibilidad
- [ ] Nombres claros
- [ ] Docstrings en métodos públicos
- [ ] Logging estructurado (JSON)
- [ ] Tests unitarios (>60%)
- [ ] CI/CD pipeline

# Escala
- [ ] Separación backend/frontend
- [ ] API versioning si ya es REST
- [ ] Pagination en endpoints
- [ ] Observabilidad (métricas, trazas)
```

---

## Conclusión

Este codebase es **funcional pero frágil**. Está bien para un MVP interno, pero necesita refactoring serio antes de exponerlo o añadir 10+ usuarios. Las vulnerable de seguridad son corregibles rápidamente; el reto estructural (SRP, DIP) requiere 4-6 semanas de trabajo disciplinado.

**Próximos pasos recomendados**:

1. Semana 1: Seguridad (rate limiting, validación, SQL injection fixes)
2. Semana 2: Caching + Índices
3. Semanas 3-4: Modularizar app.py y centralizar autorización
4. Semana 5: Logging e instrumentación
5. Semana 6: Tests básicos + documentación
