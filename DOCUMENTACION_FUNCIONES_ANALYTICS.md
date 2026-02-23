# 📊 Documentación del Sistema de Analytics

## 📋 Descripción General

Sistema completo de monitoreo y análisis de visitas para dashboards web. Permite rastrear el uso del sistema, analizar patrones de comportamiento de usuarios y generar reportes estadísticos detallados.

## 🏗️ Arquitectura

### Tecnologías Utilizadas
- **Backend**: Python con Flask
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Frontend**: HTML/CSS/JavaScript con Google Charts
- **Gestión de Timezone**: PyTZ (Zona horaria de Perú)

### Estructura de Archivos
```
├── analytics_db.py          # Clase principal de gestión de analytics
├── app.py                   # Rutas y endpoints de Flask
└── templates/
    └── analytics.html       # Interfaz de visualización
```

---

## 🔧 Clase AnalyticsDB

### Constructor
```python
def __init__(self)
```
**Descripción**: Inicializa la conexión a la base de datos y crea las tablas necesarias.

**Características**:
- Detección automática del entorno (desarrollo/producción)
- Fallback a SQLite si PostgreSQL no está disponible
- Configuración de timezone (America/Lima)

### Métodos Principales

#### 1. log_visit()
```python
def log_visit(self, user_email, user_name, page_url, page_title=None, 
              ip_address=None, user_agent=None, referrer=None, method='GET')
```
**Descripción**: Registra una visita de usuario a una página.

**Parámetros**:
- `user_email` (str): Email del usuario
- `user_name` (str): Nombre del usuario
- `page_url` (str): URL de la página visitada
- `page_title` (str, opcional): Título de la página
- `ip_address` (str, opcional): Dirección IP del usuario
- `user_agent` (str, opcional): User-Agent del navegador
- `referrer` (str, opcional): URL de referencia
- `method` (str, opcional): Método HTTP (default: 'GET')

**Uso**:
```python
analytics_db.log_visit(
    user_email='usuario@ejemplo.com',
    user_name='Juan Pérez',
    page_url='/dashboard',
    page_title='Dashboard Principal',
    ip_address='192.168.1.1'
)
```

---

#### 2. get_total_visits()
```python
def get_total_visits(self, days=30)
```
**Descripción**: Obtiene el número total de visitas en un período determinado.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 30)

**Retorna**: `int` - Total de visitas

**Ejemplo**:
```python
total = analytics_db.get_total_visits(days=7)  # Visitas de los últimos 7 días
```

---

#### 3. get_unique_users()
```python
def get_unique_users(self, days=30)
```
**Descripción**: Obtiene el número de usuarios únicos en un período.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 30)

**Retorna**: `int` - Número de usuarios únicos

**Ejemplo**:
```python
usuarios_unicos = analytics_db.get_unique_users(days=30)
```

---

#### 4. get_visits_by_user()
```python
def get_visits_by_user(self, days=30, limit=20)
```
**Descripción**: Obtiene estadísticas de visitas por usuario, ordenadas por frecuencia.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 30)
- `limit` (int): Número máximo de resultados (default: 20)

**Retorna**: `list[dict]` - Lista de diccionarios con:
- `user_email`: Email del usuario
- `user_name`: Nombre del usuario
- `visit_count`: Número de visitas
- `last_visit`: Fecha y hora de última visita

**Ejemplo**:
```python
usuarios_activos = analytics_db.get_visits_by_user(days=7, limit=10)
for usuario in usuarios_activos:
    print(f"{usuario['user_name']}: {usuario['visit_count']} visitas")
```

---

#### 5. get_visits_by_page()
```python
def get_visits_by_page(self, days=30)
```
**Descripción**: Obtiene estadísticas de visitas agrupadas por página.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 30)

**Retorna**: `list[dict]` - Lista de diccionarios con:
- `page_url`: URL de la página
- `page_title`: Título de la página
- `visit_count`: Número de visitas

**Ejemplo**:
```python
paginas = analytics_db.get_visits_by_page(days=30)
for pagina in paginas:
    print(f"{pagina['page_title']}: {pagina['visit_count']} visitas")
```

---

#### 6. get_visits_by_day()
```python
def get_visits_by_day(self, days=30)
```
**Descripción**: Obtiene visitas agrupadas por día.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 30)

**Retorna**: `list[dict]` - Lista de diccionarios con:
- `visit_date`: Fecha
- `visit_count`: Número de visitas en ese día
- `unique_users`: Usuarios únicos en ese día

**Ejemplo**:
```python
visitas_diarias = analytics_db.get_visits_by_day(days=7)
for dia in visitas_diarias:
    print(f"{dia['visit_date']}: {dia['visit_count']} visitas")
```

---

#### 7. get_visits_by_hour()
```python
def get_visits_by_hour(self, days=7)
```
**Descripción**: Obtiene visitas agrupadas por hora del día.

**Parámetros**:
- `days` (int): Número de días hacia atrás (default: 7)

**Retorna**: `list[dict]` - Lista de diccionarios con:
- `hour`: Hora del día (0-23)
- `visit_count`: Número de visitas en esa hora

**Ejemplo**:
```python
horas_pico = analytics_db.get_visits_by_hour(days=7)
for hora in horas_pico:
    print(f"{hora['hour']}:00 - {hora['visit_count']} visitas")
```

---

#### 8. get_recent_visits()
```python
def get_recent_visits(self, limit=50)
```
**Descripción**: Obtiene las visitas más recientes del sistema.

**Parámetros**:
- `limit` (int): Número máximo de visitas a retornar (default: 50)

**Retorna**: `list[dict]` - Lista de diccionarios con:
- `user_email`: Email del usuario
- `user_name`: Nombre del usuario
- `page_url`: URL visitada
- `page_title`: Título de la página
- `visit_timestamp`: Fecha y hora de la visita
- `ip_address`: Dirección IP

**Ejemplo**:
```python
ultimas_visitas = analytics_db.get_recent_visits(limit=20)
for visita in ultimas_visitas:
    print(f"{visita['user_name']} visitó {visita['page_title']} a las {visita['visit_timestamp']}")
```

---

## 🌐 Endpoint de Flask

### Ruta: `/analytics`
```python
@app.route('/analytics')
def analytics()
```

**Descripción**: Endpoint que renderiza el dashboard de analytics.

**Características**:
- Requiere autenticación de usuario
- Restringido a usuarios administradores
- Soporta filtrado por período de tiempo

**Parámetros URL**:
- `period` (int, opcional): Número de días a analizar (default: 30)
  - Ejemplo: `/analytics?period=7`

**Respuesta**: Renderiza `analytics.html` con datos estadísticos

**Datos enviados al template**:
```python
stats = {
    'total_visits': int,                    # Total de visitas
    'unique_users': int,                    # Usuarios únicos
    'total_allowed_users': int,             # Total de usuarios permitidos
    'visits_by_user': list[dict],           # Visitas por usuario
    'visits_by_page': list[dict],           # Visitas por página
    'visits_by_day': list[dict],            # Visitas por día
    'visits_by_hour': list[dict],           # Visitas por hora
    'recent_visits': list[dict]             # Visitas recientes
}
```

**Control de Acceso**:
```python
admin_emails = [
    'jonathan.cerda@agrovetmarket.com',
    'juan.portal@agrovetmarket.com',
    'ena.fernandez@agrovetmarket.com',
    'juana.lobaton@agrovetmarket.com'
]
```

---

## 🎨 Interfaz de Usuario (analytics.html)

### Componentes Visuales

#### 1. Tarjetas de Estadísticas (Stats Cards)
- **Total de Visitas**: Muestra el número total de visitas
- **Usuarios Únicos**: Muestra usuarios únicos y porcentaje de usuarios activos
- **Promedio Visitas/Usuario**: Calcula el promedio de visitas por usuario
- **Páginas Únicas**: Número de páginas diferentes visitadas

#### 2. Selector de Período
```html
<select onchange="changePeriod(this.value)">
    <option value="7">Últimos 7 días</option>
    <option value="30">Últimos 30 días</option>
    <option value="90">Últimos 90 días</option>
</select>
```

#### 3. Gráficos (Google Charts)

**a) Gráfico de Líneas - Visitas por Día**
- Muestra tendencia de visitas diarias
- Incluye línea de usuarios únicos
- Colores: `#875A7B` (visitas), `#00A09D` (usuarios únicos)

**b) Gráfico de Columnas - Visitas por Hora**
- Muestra distribución de visitas por hora del día (0-23)
- Identifica horas pico de uso
- Color: `#875A7B`

#### 4. Tablas de Datos

**a) Usuarios Más Activos**
| Columna | Descripción |
|---------|-------------|
| # | Posición |
| Usuario | Nombre del usuario |
| Email | Correo electrónico |
| Visitas | Número de visitas (badge) |
| Última Visita | Fecha y hora formateada |

**b) Páginas Más Visitadas**
| Columna | Descripción |
|---------|-------------|
| # | Posición |
| Página | Título de la página |
| URL | Ruta de la página (código) |
| Visitas | Número de visitas (badge) |
| % del Total | Porcentaje del total de visitas |

**c) Visitas Recientes**
| Columna | Descripción |
|---------|-------------|
| Fecha y Hora | Timestamp de la visita |
| Usuario | Nombre del usuario |
| Página | Título o URL de la página |
| IP | Dirección IP del visitante |

---

## 🗄️ Modelo de Base de Datos

### Tabla: `page_visits`

```sql
CREATE TABLE page_visits (
    id                  SERIAL PRIMARY KEY,
    user_email          VARCHAR(255) NOT NULL,
    user_name           VARCHAR(255),
    page_url            VARCHAR(500) NOT NULL,
    page_title          VARCHAR(255),
    visit_timestamp     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    session_duration    INTEGER DEFAULT 0,
    ip_address          VARCHAR(50),
    user_agent          TEXT,
    referrer            VARCHAR(500),
    method              VARCHAR(10)
);
```

### Índices
```sql
-- Índice para búsquedas por usuario
CREATE INDEX idx_visits_user ON page_visits(user_email);

-- Índice para búsquedas por fecha (descendente)
CREATE INDEX idx_visits_timestamp ON page_visits(visit_timestamp DESC);

-- Índice para búsquedas por página
CREATE INDEX idx_visits_page ON page_visits(page_url);
```

---

## 🚀 Implementación en Nuevo Proyecto

### Paso 1: Instalación de Dependencias
```bash
pip install flask psycopg2-binary pytz
```

### Paso 2: Configuración de Variables de Entorno
```bash
# Para producción (PostgreSQL)
export DATABASE_URL="postgresql://user:password@host:port/database"

# Para desarrollo (SQLite - automático)
# No requiere configuración
```

### Paso 3: Inicialización en Flask
```python
from analytics_db import AnalyticsDB

# Crear instancia global
analytics_db = AnalyticsDB()

# Registrar visitas en decorador o middleware
@app.before_request
def log_page_visit():
    if 'username' in session:
        analytics_db.log_visit(
            user_email=session.get('username'),
            user_name=session.get('user_name'),
            page_url=request.path,
            page_title=request.endpoint,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            referrer=request.referrer,
            method=request.method
        )
```

### Paso 4: Crear Ruta de Analytics
```python
@app.route('/analytics')
def analytics():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Verificar permisos de administrador
    if not is_admin(session.get('username')):
        flash('No tienes permisos para acceder a esta sección.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener período
    days = request.args.get('period', 30, type=int)
    
    # Recopilar estadísticas
    stats = {
        'total_visits': analytics_db.get_total_visits(days),
        'unique_users': analytics_db.get_unique_users(days),
        'visits_by_user': [dict(row) for row in analytics_db.get_visits_by_user(days)],
        'visits_by_page': [dict(row) for row in analytics_db.get_visits_by_page(days)],
        'visits_by_day': [dict(row) for row in analytics_db.get_visits_by_day(days)],
        'visits_by_hour': [dict(row) for row in analytics_db.get_visits_by_hour(min(days, 7))],
        'recent_visits': [dict(row) for row in analytics_db.get_recent_visits(50)]
    }
    
    return render_template('analytics.html', stats=stats, period=days)
```

---

## 📊 Métricas y KPIs Disponibles

### Métricas Básicas
- Total de visitas
- Usuarios únicos
- Páginas únicas visitadas
- Promedio de visitas por usuario

### Análisis Temporal
- Visitas por día (tendencias)
- Visitas por hora (patrones de uso)
- Identificación de horas pico

### Análisis de Usuarios
- Usuarios más activos
- Última actividad de cada usuario
- Tasa de usuarios activos vs. total

### Análisis de Páginas
- Páginas más visitadas
- Porcentaje de visitas por página
- Popularidad de contenido

### Monitoreo en Tiempo Real
- Visitas recientes (últimas 50)
- Actividad actual del sistema

---

## � Sistema de Gestión de Equipos de Ventas

### Descripción General
Sistema integrado para organizar vendedores en equipos comerciales y asignar metas individuales por línea de negocio. Permite gestión dinámica de miembros y metas mensuales con almacenamiento en Supabase.

### Arquitectura del Sistema

#### Componentes Principales
1. **Frontend**: `metas_vendedor.html` - Interfaz de gestión
2. **Backend**: Función `metas_vendedor()` en `app.py`
3. **Gestor de Datos**: `SupabaseManager` con métodos específicos
4. **Base de Datos**: Tablas `equipos_vendedores` y `metas_vendedor_2026`

---

### 🎯 Modelo de Datos

#### Tabla: `equipos_vendedores`
```sql
CREATE TABLE equipos_vendedores (
    id                  SERIAL PRIMARY KEY,
    equipo_id           VARCHAR(50) NOT NULL,
    equipo_nombre       VARCHAR(100) NOT NULL,
    vendedor_id         INTEGER NOT NULL,
    vendedor_nombre     VARCHAR(255) NOT NULL
);

-- Índices
CREATE INDEX idx_equipos_equipo_id ON equipos_vendedores(equipo_id);
CREATE INDEX idx_equipos_vendedor_id ON equipos_vendedores(vendedor_id);
```

#### Tabla: `metas_vendedor_2026`
```sql
CREATE TABLE metas_vendedor_2026 (
    id                  SERIAL PRIMARY KEY,
    linea_comercial     VARCHAR(50) NOT NULL,
    vendedor_id         INTEGER NOT NULL,
    mes                 VARCHAR(7) NOT NULL,      -- Formato: 'YYYY-MM'
    meta_total          DECIMAL(15,2) DEFAULT 0,
    meta_ipn            DECIMAL(15,2) DEFAULT 0,  -- IPN: Introducción Productos Nuevos
    UNIQUE(linea_comercial, vendedor_id, mes)
);

-- Índices
CREATE INDEX idx_metas_linea ON metas_vendedor_2026(linea_comercial);
CREATE INDEX idx_metas_mes ON metas_vendedor_2026(mes);
CREATE INDEX idx_metas_vendedor ON metas_vendedor_2026(vendedor_id);
```

---

### 🔧 Funciones de SupabaseManager

#### 1. read_equipos()
```python
def read_equipos(self)
```
**Descripción**: Lee las asignaciones de vendedores a equipos desde Supabase.

**Retorna**: `dict` - Estructura `{equipo_id: [vendedor_id1, vendedor_id2, ...]}`

**Ejemplo de respuesta**:
```python
{
    'petmedica': [123, 456, 789],
    'agrovet': [234, 567],
    'avivet': [890, 123]
}
```

**Uso**:
```python
supabase_manager = SupabaseManager()
equipos = supabase_manager.read_equipos()
vendedores_petmedica = equipos.get('petmedica', [])
```

---

#### 2. write_equipos()
```python
def write_equipos(self, equipos_data, todos_los_vendedores)
```
**Descripción**: Guarda las asignaciones de vendedores a equipos en Supabase. **Operación atómica**: elimina todas las asignaciones existentes y luego inserta las nuevas.

**Parámetros**:
- `equipos_data` (dict): Estructura `{equipo_id: [vendedor_id1, vendedor_id2, ...]}`
- `todos_los_vendedores` (list): Lista de vendedores con estructura `[{id: int, name: str}, ...]`

**Ejemplo**:
```python
equipos_data = {
    'petmedica': [123, 456, 789],
    'agrovet': [234, 567]
}

vendedores = [
    {'id': 123, 'name': 'Juan Pérez'},
    {'id': 456, 'name': 'María García'},
    {'id': 789, 'name': 'Carlos López'},
    {'id': 234, 'name': 'Ana Martínez'},
    {'id': 567, 'name': 'Pedro Sánchez'}
]

supabase_manager.write_equipos(equipos_data, vendedores)
# ✅ Guardadas 5 asignaciones de equipos en Supabase
```

**Nota importante**: Esta operación elimina todas las asignaciones previas antes de insertar las nuevas.

---

#### 3. read_metas()
```python
def read_metas(self)
```
**Descripción**: Lee todas las metas de vendedores desde Supabase.

**Retorna**: `dict` - Estructura anidada `{linea_comercial: {vendedor_id: {mes: {meta, meta_ipn}}}}`

**Ejemplo de respuesta**:
```python
{
    'petmedica': {
        '123': {
            '2026-01': {'meta': 50000.0, 'meta_ipn': 5000.0},
            '2026-02': {'meta': 55000.0, 'meta_ipn': 5500.0}
        },
        '456': {
            '2026-01': {'meta': 40000.0, 'meta_ipn': 4000.0}
        }
    },
    'agrovet': {
        '234': {
            '2026-01': {'meta': 60000.0, 'meta_ipn': 6000.0}
        }
    }
}
```

**Uso**:
```python
metas = supabase_manager.read_metas()
meta_vendedor_enero = metas.get('petmedica', {}).get('123', {}).get('2026-01', {})
meta_total = meta_vendedor_enero.get('meta', 0)
meta_ipn = meta_vendedor_enero.get('meta_ipn', 0)
print(f"Meta Total: ${meta_total:,.2f}, Meta IPN: ${meta_ipn:,.2f}")
```

---

#### 4. write_metas()
```python
def write_metas(self, metas_anidadas)
```
**Descripción**: Guarda las metas de vendedores en Supabase utilizando operación UPSERT (actualiza si existe, inserta si no).

**Parámetros**:
- `metas_anidadas` (dict): Estructura anidada `{linea_comercial: {vendedor_id: {mes: {meta, meta_ipn}}}}`

**Ejemplo**:
```python
metas = {
    'petmedica': {
        '123': {
            '2026-03': {
                'meta': 52000.0,
                'meta_ipn': 5200.0
            }
        }
    }
}

supabase_manager.write_metas(metas)
# ✅ Guardadas 1 metas de vendedores en Supabase (upsert)
```

**Comportamiento UPSERT**:
- Si ya existe un registro con la misma combinación `(linea_comercial, vendedor_id, mes)`, se actualiza
- Si no existe, se crea un nuevo registro

---

### 🌐 Endpoint de Flask: `/metas_vendedor`

```python
@app.route('/metas_vendedor', methods=['GET', 'POST'])
def metas_vendedor()
```

**Descripción**: Endpoint para gestión completa de equipos y metas de vendedores.

#### Control de Acceso
```python
admin_users = [
    "jonathan.cerda@agrovetmarket.com",
    "janet.hueza@agrovetmarket.com",
    "juan.portal@agrovetmarket.com",
    "AMAHOdoo@agrovetmarket.com",
    "juana.lobaton@agrovetmarket.com",
    "jimena.delrisco@agrovetmarket.com"
]
```

#### Equipos Definidos
```python
equipos_definidos = [
    {'id': 'petmedica', 'nombre': 'PETMEDICA'},
    {'id': 'agrovet', 'nombre': 'AGROVET'},
    {'id': 'pet_nutriscience', 'nombre': 'PET NUTRISCIENCE'},
    {'id': 'avivet', 'nombre': 'AVIVET'},
    {'id': 'otros', 'nombre': 'OTROS'},
    {'id': 'terceros', 'nombre': 'TERCEROS'},
    {'id': 'interpet', 'nombre': 'INTERPET'}
]
```

#### Método GET
Renderiza la interfaz con:
- Lista de equipos con sus vendedores asignados
- Metas guardadas de todos los vendedores
- Meses disponibles del año actual
- Líneas comerciales para filtrar

**Datos enviados al template**:
```python
{
    'meses_disponibles': [{'mes': '2026-01', 'nombre': 'Enero'}, ...],
    'lineas_comerciales': [...],
    'equipos_con_vendedores': [
        {
            'id': 'petmedica',
            'nombre': 'PETMEDICA',
            'vendedores_ids': ['123', '456'],
            'vendedores': [
                {'id': 123, 'name': 'Juan Pérez'},
                {'id': 456, 'name': 'María García'}
            ]
        },
        ...
    ],
    'todos_los_vendedores': [...],
    'metas_guardadas': {...},
    'is_admin': True
}
```

#### Método POST
Procesa dos tipos de operaciones:

**1. Guardar Asignaciones de Equipos**
```python
# Campos del formulario: vendedores_{equipo_id}
# Ejemplo: vendedores_petmedica = "123,456,789"

equipos_guardados = {}
for equipo in equipos_definidos:
    vendedores_str = request.form.get(f'vendedores_{equipo["id"]}', '')
    if vendedores_str:
        vendedores_ids = [int(vid) for vid in vendedores_str.split(',')]
        equipos_guardados[equipo['id']] = vendedores_ids

supabase_manager.write_equipos(equipos_guardados, todos_los_vendedores)
```

**2. Guardar Metas del Mes Seleccionado**
```python
# Campos del formulario: 
# meta_{equipo_id}_{vendedor_id}_{mes}
# meta_ipn_{equipo_id}_{vendedor_id}_{mes}
# Ejemplo: meta_petmedica_123_2026-01 = "50000.00"

metas_solo_mes_actual = {}
for equipo in equipos_definidos:
    for vendedor_id in equipos_guardados.get(equipo['id'], []):
        meta_str = request.form.get(f'meta_{equipo_id}_{vendedor_id}_{mes}')
        meta_ipn_str = request.form.get(f'meta_ipn_{equipo_id}_{vendedor_id}_{mes}')
        
        # Limpiar formato (1.000,50 -> 1000.50)
        meta = float(meta_str.replace('.', '').replace(',', '.'))
        meta_ipn = float(meta_ipn_str.replace('.', '').replace(',', '.'))
        
        metas_solo_mes_actual[equipo_id][vendedor_id_str] = {
            mes: {'meta': meta, 'meta_ipn': meta_ipn}
        }

supabase_manager.write_metas(metas_solo_mes_actual)
```

---

### 🎨 Interfaz de Usuario

#### Componente: Selector de Vendedores (Tom-Select)
**Biblioteca**: Tom-Select v2.3.1

**Características**:
- Búsqueda en tiempo real
- Selección múltiple
- Botón de eliminación en cada item
- Estilo personalizado con colores corporativos

**Inicialización**:
```javascript
new TomSelect(`#select-${equipo.id}`, {
    plugins: ['remove_button'],
    create: false,
    placeholder: 'Buscar y agregar vendedores...',
    options: todosLosVendedores,
    valueField: 'value',
    labelField: 'text',
    searchField: 'text',
    openOnFocus: false,
    maxOptions: 7
});
```

#### Tabla de Gestión
Cada equipo muestra:
- Nombre del equipo con icono
- Selector multi-vendedores
- Descripción de la función

**Estructura HTML**:
```html
<table class="team-table">
    <thead>
        <tr>
            <th>Equipo de Venta</th>
            <th>Vendedores Asignados</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td class="team-name-cell">
                <strong><i class="bi bi-people-fill"></i> PETMEDICA</strong>
                <p>Asigna los vendedores para este equipo.</p>
            </td>
            <td class="team-selector-cell">
                <input id="select-petmedica" 
                       name="vendedores_petmedica" 
                       value="123,456,789">
            </td>
        </tr>
    </tbody>
</table>
```

#### Tabla de Metas (metas_vendedor.html)
Permite asignar metas por:
- Equipo
- Vendedor
- Mes (12 columnas, una por mes)
- Tipo de meta (Total y IPN)

**Campos dinámicos**:
```html
<input type="number" 
       name="meta_petmedica_123_2026-01" 
       value="50000.00"
       step="0.01">

<input type="number" 
       name="meta_ipn_petmedica_123_2026-01" 
       value="5000.00"
       step="0.01">
```

---

### 📊 Integración con Dashboard

#### Dashboard Principal
Utiliza equipos para:
- Filtrar ventas por línea comercial
- Calcular metas de equipo vs. ventas reales
- Mostrar rendimiento de vendedores específicos

**Ejemplo de uso en dashboard**:
```python
equipos_guardados = supabase_manager.read_equipos()
vendedores_petmedica = equipos_guardados.get('petmedica', [])

# Filtrar ventas del equipo
for sale in sales_data:
    vendedor_id = sale.get('invoice_user_id', [None])[0]
    if vendedor_id in vendedores_petmedica:
        # Procesar venta del equipo PETMEDICA
        ventas_petmedica += sale.get('balance', 0)
```

#### Dashboard por Línea
Muestra tabla detallada de vendedores con:
- Meta asignada
- Venta realizada
- Porcentaje de avance
- Meta IPN (Introducción Productos Nuevos)
- Ventas por vencimiento

```python
metas_guardadas = supabase_manager.read_metas()
metas_linea = metas_guardadas.get('petmedica', {})

for vendedor_id in vendedores_petmedica:
    meta_info = metas_linea.get(str(vendedor_id), {}).get(mes_actual, {})
    meta_total = meta_info.get('meta', 0)
    meta_ipn = meta_info.get('meta_ipn', 0)
```

---

### 🔄 Flujo de Trabajo Completo

#### 1. Configuración Inicial de Equipos
```python
# Administrador accede a /metas_vendedor
# 1. Selecciona vendedores para cada equipo
# 2. Hace clic en "Guardar Cambios"
# 3. Sistema ejecuta write_equipos()
# 4. Flash message: "Equipos y metas guardados correctamente"
```

#### 2. Asignación de Metas
```python
# 1. Sistema carga equipos con read_equipos()
# 2. Renderiza tabla con todos los vendedores del equipo
# 3. Administrador ingresa metas para cada vendedor-mes
# 4. Envía formulario
# 5. Sistema ejecuta write_metas() con UPSERT
# 6. Redirección a la misma página con datos actualizados
```

#### 3. Visualización en Dashboard
```python
# 1. Usuario accede a /dashboard_linea?linea_nombre=PETMEDICA
# 2. Sistema carga:
#    - read_equipos() para obtener vendedores del equipo
#    - read_metas() para obtener metas del mes
#    - get_sales_lines() para obtener ventas del período
# 3. Calcula KPIs por vendedor
# 4. Renderiza tabla comparativa
```

---

### 💡 Casos de Uso

#### Caso 1: Agregar Vendedor a Equipo
```python
# Administrador en interfaz:
# 1. Selecciona equipo PETMEDICA
# 2. Busca vendedor "Carlos Ramírez" en Tom-Select
# 3. Hace clic en el vendedor
# 4. Guarda cambios

# Backend:
equipos_guardados['petmedica'].append(999)  # ID de Carlos
supabase_manager.write_equipos(equipos_guardados, todos_los_vendedores)
```

#### Caso 2: Actualizar Meta de Vendedor
```python
# Administrador en interfaz:
# 1. Navega a vendedor específico
# 2. En columna "Enero 2026", ingresa: 60000
# 3. En fila IPN, ingresa: 6000
# 4. Guarda

# Backend:
metas['petmedica']['999'] = {
    '2026-01': {'meta': 60000.0, 'meta_ipn': 6000.0}
}
supabase_manager.write_metas(metas)
# UPSERT: actualiza si existe, crea si no
```

#### Caso 3: Transferir Vendedor Entre Equipos
```python
# Mover vendedor 123 de PETMEDICA a AGROVET

# Paso 1: Remover de PETMEDICA
equipos_guardados['petmedica'].remove(123)

# Paso 2: Agregar a AGROVET
equipos_guardados['agrovet'].append(123)

# Paso 3: Guardar
supabase_manager.write_equipos(equipos_guardados, todos_los_vendedores)

# Nota: Las metas del vendedor se mantienen en ambas líneas
```

#### Caso 4: Consultar Rendimiento de Equipo
```python
# En dashboard por línea
equipos = supabase_manager.read_equipos()
metas = supabase_manager.read_metas()

vendedores_equipo = equipos.get('petmedica', [])
total_meta_equipo = 0
total_venta_equipo = 0

for vendedor_id in vendedores_equipo:
    meta_info = metas.get('petmedica', {}).get(str(vendedor_id), {}).get('2026-01', {})
    total_meta_equipo += meta_info.get('meta', 0)
    
    # Calcular ventas del vendedor...
    total_venta_equipo += ventas_vendedor

porcentaje_cumplimiento = (total_venta_equipo / total_meta_equipo * 100) if total_meta_equipo > 0 else 0
```

---

### 🔧 Formato de Datos

#### Formato de Metas
- **Meta Total**: Monto en USD sin símbolo (`50000.00`)
- **Meta IPN**: Monto en USD sin símbolo (`5000.00`)
- **Mes**: Formato ISO `YYYY-MM` (`2026-01`)

#### Limpieza de Entrada
El sistema maneja diferentes formatos de entrada:
```python
# Entrada del usuario
"1.000,50"  # Formato latino (miles con punto, decimales con coma)
"1,000.50"  # Formato anglo (miles con coma, decimales con punto)
"1000.50"   # Formato limpio

# Limpieza
clean_value = input_str.replace('.', '').replace(',', '.')
# Resultado: "1000.50"

meta = float(clean_value)
# Resultado: 1000.5
```

---

### 🚨 Validaciones y Manejo de Errores

#### Validación de Permisos
```python
if not is_admin:
    flash('No tienes permiso para acceder a esta página.', 'warning')
    return redirect(url_for('dashboard'))
```

#### Validación de Entrada Numérica
```python
try:
    meta = float(clean_meta) if clean_meta else None
except (ValueError, TypeError):
    meta = None  # Valor inválido se trata como None
```

#### Validación de IDs
```python
vendedores_ids = [int(vid) for vid in vendedores_str.split(',') if vid.isdigit()]
# Solo procesa IDs numéricos válidos
```

#### Manejo de Vendedores No Encontrados
```python
vendedores_de_equipo = [
    vendedores_por_id[vid] 
    for vid in vendedores_ids 
    if vid in vendedores_por_id  # Solo incluye vendedores existentes
]
```

---

### 📦 Dependencias del Sistema

#### Python
```txt
flask>=2.0.0
supabase>=1.0.0
python-dotenv>=0.19.0
```

#### JavaScript (CDN)
```html
<!-- Tom-Select para selección múltiple -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tom-select@2.3.1/dist/css/tom-select.bootstrap5.min.css">
<script src="https://cdn.jsdelivr.net/npm/tom-select@2.3.1/dist/js/tom-select.complete.min.js"></script>
```

---

### 🎯 Mejores Prácticas

#### 1. Asignación de Equipos
- Revisar equipos mensualmente para reflejar cambios organizacionales
- Mantener un vendedor en solo un equipo principal
- Usar el equipo "OTROS" para vendedores multi-línea

#### 2. Asignación de Metas
- Establecer metas al inicio de cada mes
- Considerar estacionalidad en las metas
- Meta IPN típicamente 10% de meta total
- Revisar metas trimestralmente

#### 3. Monitoreo
- Revisar avance semanal en dashboard por línea
- Identificar vendedores con bajo rendimiento tempranamente
- Ajustar estrategias según análisis de datos

#### 4. Datos Históricos
- Conservar metas anteriores para análisis comparativo
- No eliminar registros, solo actualizar
- Usar UPSERT para mantener historial completo

---

## �🔒 Características de Seguridad

### Control de Acceso
- Autenticación requerida para acceder
- Lista blanca de administradores
- Redirección automática si no hay permisos

### Privacidad de Datos
- Exclusión automática de usuarios administradores en estadísticas
- Almacenamiento seguro de IPs
- Gestión de timezones para correcta atribución temporal

### Manejo de Errores
- Try-catch en todas las operaciones de BD
- Logging de errores con emojis descriptivos
- Fallback automático a SQLite si PostgreSQL falla

---

## 🎯 Casos de Uso

### 1. Monitoreo de Adopción
Medir cuántos usuarios están usando activamente el sistema.
```python
usuarios_activos = analytics_db.get_unique_users(days=30)
tasa_adopcion = (usuarios_activos / total_usuarios) * 100
```

### 2. Identificación de Funcionalidades Populares
Determinar qué páginas son más visitadas.
```python
paginas_populares = analytics_db.get_visits_by_page(days=7)
top_3 = paginas_populares[:3]
```

### 3. Análisis de Patrones de Uso
Identificar horas pico para planificar mantenimiento.
```python
horas = analytics_db.get_visits_by_hour(days=7)
hora_menor_uso = min(horas, key=lambda x: x['visit_count'])
```

### 4. Detección de Usuarios Inactivos
Identificar usuarios que no han ingresado recientemente.
```python
usuarios_recientes = analytics_db.get_visits_by_user(days=7)
emails_activos = [u['user_email'] for u in usuarios_recientes]
# Comparar con lista total de usuarios
```

---

## 📈 Extensiones Futuras

### Funcionalidades Sugeridas
1. **Duración de Sesión**: Calcular tiempo promedio en cada página
2. **Dashboards Personalizados**: Filtros por usuario, departamento, rol
3. **Alertas**: Notificaciones cuando métricas superen umbrales
4. **Exportación**: Descargar reportes en PDF/Excel
5. **Comparación de Períodos**: Comparar semana actual vs. anterior
6. **Funnel de Conversión**: Seguimiento de secuencias de páginas
7. **Mapas de Calor**: Visualización de clics y áreas de interés
8. **A/B Testing**: Comparación de variantes de UI

### Mejoras de Rendimiento
- Implementar caché Redis para consultas frecuentes
- Agregaciones pre-calculadas para períodos largos
- Particionamiento de tablas por fecha
- Índices adicionales según patrones de consulta

---

## 📝 Notas de Implementación

### Timezone
- Sistema configurado para **America/Lima (UTC-5)**
- Todos los timestamps se convierten automáticamente
- Compatible con horarios de verano

### Compatibilidad
- **SQLite**: Para desarrollo local
- **PostgreSQL**: Para producción
- Detección automática según `DATABASE_URL`

### Rendimiento
- Índices optimizados para consultas frecuentes
- Context managers para gestión correcta de conexiones
- Rollback automático en caso de error

### Exclusiones
- Usuario `jonathan.cerda@agrovetmarket.com` excluido de estadísticas
- Configurable para excluir otros usuarios de prueba

---

## 🛠️ Troubleshooting

### Problema: "psycopg2 no disponible"
```bash
pip install psycopg2-binary
```

### Problema: Timezone incorrecto
Verificar configuración:
```python
import pytz
PERU_TZ = pytz.timezone('America/Lima')
```

### Problema: Tablas no se crean
Verificar permisos de base de datos y ejecutar:
```python
analytics_db = AnalyticsDB()
# Las tablas se crean automáticamente en __init__
```

---

---

## 🔗 Integración de Sistemas Analytics + Equipos de Ventas

### Visión General
El sistema combina dos módulos complementarios que trabajan en conjunto:

1. **Analytics**: Monitorea el **uso** del sistema (quién, cuándo, qué página)
2. **Equipos de Ventas**: Gestiona la **organización** y **metas** del equipo comercial

### Puntos de Integración

#### 1. Control de Acceso Compartido
Ambos sistemas utilizan listas de administradores permitidos:

```python
# Analytics
admin_emails = [
    'jonathan.cerda@agrovetmarket.com',
    'juan.portal@agrovetmarket.com',
    'ena.fernandez@agrovetmarket.com',
    'juana.lobaton@agrovetmarket.com'
]

# Equipos de Ventas (más amplio)
admin_users = [
    "jonathan.cerda@agrovetmarket.com",
    "janet.hueza@agrovetmarket.com",
    "juan.portal@agrovetmarket.com",
    "AMAHOdoo@agrovetmarket.com",
    "juana.lobaton@agrovetmarket.com",
    "jimena.delrisco@agrovetmarket.com"
]
```

#### 2. Tracking de Navegación
Analytics registra automáticamente visitas a páginas de gestión de equipos:

```python
# En app.py - after_request()
page_titles = {
    '/metas-vendedor': 'Metas por Vendedor',
    '/dashboard-linea': 'Dashboard por Línea',
    '/equipo-ventas': 'Equipo de Ventas',
    # ...
}

# Cada visita a estas páginas se registra en analytics
analytics_db.log_visit(
    user_email=session.get('username'),
    page_url=request.path,
    page_title=page_titles.get(request.path)
)
```

#### 3. Dashboard Unificado
El dashboard principal consume datos de ambos sistemas:

```python
# En /dashboard
# Datos de Equipos
equipos_guardados = supabase_manager.read_equipos()
metas_del_mes = supabase_manager.read_metas()

# Datos de Analytics (si es admin)
if is_admin:
    usuarios_activos = analytics_db.get_unique_users(days=30)
    paginas_mas_visitadas = analytics_db.get_visits_by_page(days=30)
```

### Casos de Uso Combinados

#### Análisis de Adopción por Equipo
Combinar datos de equipos con analytics para identificar patrones:

```python
# Obtener equipos
equipos = supabase_manager.read_equipos()

# Obtener visitas por usuario
visitas = analytics_db.get_visits_by_user(days=30)

# Análisis: ¿Qué equipos usan más el sistema?
uso_por_equipo = {}
for equipo_id, vendedores_ids in equipos.items():
    uso_por_equipo[equipo_id] = {
        'total_visitas': 0,
        'usuarios_activos': 0
    }
    
    for visita in visitas:
        if get_vendedor_id(visita['user_email']) in vendedores_ids:
            uso_por_equipo[equipo_id]['total_visitas'] += visita['visit_count']
            uso_por_equipo[equipo_id]['usuarios_activos'] += 1

# Resultado: Equipos más activos en el sistema
```

#### Alertas de Inactividad
Detectar vendedores con metas asignadas pero sin actividad:

```python
# Vendedores con metas
metas = supabase_manager.read_metas()
vendedores_con_metas = set()
for linea in metas.values():
    vendedores_con_metas.update(linea.keys())

# Usuarios activos en últimos 7 días
visitas_recientes = analytics_db.get_visits_by_user(days=7)
usuarios_activos = {v['user_email'] for v in visitas_recientes}

# Vendedores inactivos
vendedores_inactivos = vendedores_con_metas - usuarios_activos
# Enviar alertas o notificaciones
```

#### Reportes Ejecutivos
Generar reportes que combinen rendimiento y uso:

```python
def generar_reporte_ejecutivo(mes):
    reporte = {
        'periodo': mes,
        'equipos': []
    }
    
    equipos = supabase_manager.read_equipos()
    metas = supabase_manager.read_metas()
    
    for equipo_id, vendedores_ids in equipos.items():
        equipo_info = {
            'nombre': equipo_id.upper(),
            'total_vendedores': len(vendedores_ids),
            'meta_total': 0,
            'usuarios_activos_sistema': 0,
            'tasa_adopcion': 0
        }
        
        # Calcular metas
        metas_equipo = metas.get(equipo_id, {})
        for vendedor_id in vendedores_ids:
            meta_info = metas_equipo.get(str(vendedor_id), {}).get(mes, {})
            equipo_info['meta_total'] += meta_info.get('meta', 0)
        
        # Calcular adopción del sistema
        visitas = analytics_db.get_visits_by_user(days=30)
        for vendedor_id in vendedores_ids:
            # Verificar si el vendedor ha usado el sistema
            for visita in visitas:
                if get_vendedor_id(visita['user_email']) == vendedor_id:
                    equipo_info['usuarios_activos_sistema'] += 1
                    break
        
        equipo_info['tasa_adopcion'] = (
            equipo_info['usuarios_activos_sistema'] / 
            equipo_info['total_vendedores'] * 100
        ) if equipo_info['total_vendedores'] > 0 else 0
        
        reporte['equipos'].append(equipo_info)
    
    return reporte
```

### Arquitectura de Datos Completa

```
┌─────────────────────────────────────────────────────────┐
│                  SISTEMA COMPLETO                        │
└─────────────────────────────────────────────────────────┘

┌──────────────────────┐          ┌──────────────────────┐
│   ANALYTICS DB       │          │   SUPABASE           │
│   (PostgreSQL/SQLite)│          │   (PostgreSQL)       │
├──────────────────────┤          ├──────────────────────┤
│ • page_visits        │          │ • equipos_vendedores │
│   - user_email       │          │   - equipo_id        │
│   - page_url         │          │   - vendedor_id      │
│   - visit_timestamp  │          │                      │
│   - ip_address       │          │ • metas_vendedor_2026│
│   - user_agent       │          │   - linea_comercial  │
│                      │          │   - vendedor_id      │
└──────────────────────┘          │   - mes              │
                                  │   - meta_total       │
                                  │   - meta_ipn         │
                                  └──────────────────────┘

           │                                │
           └────────────┬───────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │   FLASK APP     │
              ├─────────────────┤
              │ • /analytics    │
              │ • /metas_vendedor│
              │ • /dashboard    │
              │ • /dashboard_linea│
              └─────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  FRONTEND       │
              ├─────────────────┤
              │ • Analytics UI  │
              │ • Equipos UI    │
              │ • Dashboards    │
              └─────────────────┘
```

### Métricas Clave Combinadas

#### KPIs del Sistema
1. **Adopción del Sistema**
   - `usuarios_activos / total_vendedores * 100`
   
2. **Eficiencia de Uso**
   - `visitas_promedio_por_usuario / ventanas_disponibles`
   
3. **Rendimiento Comercial**
   - `ventas_reales / metas_asignadas * 100`
   
4. **Correlación Uso-Ventas**
   - ¿Los equipos que más usan el sistema venden más?

#### Queries Útiles

**1. Vendedores más activos en el sistema por equipo**
```python
def vendedores_activos_por_equipo(dias=30):
    equipos = supabase_manager.read_equipos()
    visitas = analytics_db.get_visits_by_user(days=dias)
    
    resultado = {}
    for equipo_id, vendedores_ids in equipos.items():
        resultado[equipo_id] = []
        for visita in visitas:
            vendedor_id = get_vendedor_id(visita['user_email'])
            if vendedor_id in vendedores_ids:
                resultado[equipo_id].append({
                    'vendedor': visita['user_name'],
                    'visitas': visita['visit_count'],
                    'ultima_visita': visita['last_visit']
                })
        # Ordenar por visitas
        resultado[equipo_id].sort(key=lambda x: x['visitas'], reverse=True)
    
    return resultado
```

**2. Páginas más consultadas por línea comercial**
```python
def paginas_por_linea(linea_comercial, dias=30):
    equipos = supabase_manager.read_equipos()
    vendedores_linea = equipos.get(linea_comercial, [])
    
    todas_visitas = analytics_db.get_recent_visits(limit=1000)
    
    visitas_linea = [
        v for v in todas_visitas 
        if get_vendedor_id(v['user_email']) in vendedores_linea
    ]
    
    # Agrupar por página
    paginas = {}
    for visita in visitas_linea:
        pagina = visita['page_url']
        paginas[pagina] = paginas.get(pagina, 0) + 1
    
    return sorted(paginas.items(), key=lambda x: x[1], reverse=True)
```

**3. Tendencia de uso vs. tendencia de ventas**
```python
def correlacion_uso_ventas(equipo_id, meses=6):
    # Obtener visitas mensuales
    visitas_por_mes = analytics_db.get_visits_by_day(days=meses*30)
    
    # Obtener ventas mensuales
    metas = supabase_manager.read_metas()
    ventas_por_mes = obtener_ventas_reales(equipo_id, meses)
    
    # Calcular correlación
    correlacion = calcular_correlacion(
        [v['visit_count'] for v in visitas_por_mes],
        [v['venta'] for v in ventas_por_mes]
    )
    
    return {
        'equipo': equipo_id,
        'correlacion': correlacion,
        'interpretacion': 'positiva' if correlacion > 0.5 else 'negativa'
    }
```

---

### 📋 Checklist de Implementación Completa

#### Fase 1: Infraestructura
- [ ] Crear base de datos PostgreSQL/SQLite para analytics
- [ ] Configurar tablas de Supabase (equipos y metas)
- [ ] Configurar variables de entorno (`DATABASE_URL`, `SUPABASE_URL`, etc.)
- [ ] Instalar dependencias Python y JavaScript

#### Fase 2: Backend
- [ ] Implementar `AnalyticsDB` con todos los métodos
- [ ] Implementar métodos de `SupabaseManager` para equipos/metas
- [ ] Crear ruta `/analytics`
- [ ] Crear ruta `/metas_vendedor`
- [ ] Configurar middleware de tracking

#### Fase 3: Frontend
- [ ] Diseñar interfaz de analytics con Google Charts
- [ ] Implementar selector de vendedores con Tom-Select
- [ ] Crear tablas de metas con inputs dinámicos
- [ ] Estilizar con CSS corporativo

#### Fase 4: Integración
- [ ] Conectar dashboards con datos de equipos
- [ ] Implementar filtros por equipo en dashboards
- [ ] Agregar analytics a páginas de gestión

#### Fase 5: Testing
- [ ] Probar registro de visitas
- [ ] Probar asignación de equipos
- [ ] Probar asignación de metas
- [ ] Probar dashboards integrados

#### Fase 6: Monitoreo
- [ ] Configurar alertas de inactividad
- [ ] Implementar reportes ejecutivos
- [ ] Establecer KPIs de adopción

---

## 📞 Soporte

Para soporte técnico o preguntas sobre implementación, contactar al equipo de desarrollo.

**Autor**: Sistema desarrollado para Dashboard de Ventas Agrovet Market  
**Versión**: 2.0 (Analytics + Equipos de Ventas)  
**Última Actualización**: Febrero 2026

---

## 📄 Licencia

Sistema interno de uso exclusivo del proyecto.

---

## 📚 Índice de Contenidos

### Sistema de Analytics
1. Clase `AnalyticsDB`
2. Métodos de análisis (8 funciones principales)
3. Endpoint `/analytics`
4. Interfaz de visualización
5. Modelo de base de datos

### Sistema de Equipos de Ventas
6. Modelo de datos (equipos y metas)
7. Funciones de `SupabaseManager` (4 métodos)
8. Endpoint `/metas_vendedor`
9. Interfaz de gestión con Tom-Select
10. Integración con dashboards

### Integración
11. Puntos de integración
12. Casos de uso combinados
13. Métricas y KPIs unificados
14. Queries útiles
15. Checklist de implementación

---

**Fin del documento**
