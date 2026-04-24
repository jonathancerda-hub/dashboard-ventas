# 🎨 Especificación de Diseño Visual - Módulo Administración de Usuarios

> **Documento de referencia para replicar el diseño exacto del módulo de administración de usuarios**  
> **Fecha:** 22 de abril de 2026  
> **Proyecto:** Dashboard Ventas Farmacéuticas  
> **URL de referencia:** `dashboard-ventas-d7ff.onrender.com/admin/users`

---

## 📐 Vista General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  👥 Administración de Usuarios                    [Agregar] [Historial]... │
│  Gestión de permisos y roles de acceso al sistema                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                           │
│  │  👥  44    │  │  🛡️  4     │  │  ✏️  49     │                           │
│  │  Total...  │  │  Admin...  │  │  Cambios.. │                           │
│  └────────────┘  └────────────┘  └────────────┘                           │
│                                                                             │
│  📋 Lista de Usuarios                                                       │
│  ┌─────────────────────────┬──────────────┬───────────┐                    │
│  │ 🔍 Buscar Usuario...    │ Todos roles ▼│ Limpiar  │                    │
│  └─────────────────────────┴──────────────┴───────────┘                    │
│                                                                             │
│  Mostrar [25▼] registros                                                   │
│                                                                             │
│  ┌──────────────────┬─────────────┬──────────┬───────────┬────────────┐   │
│  │ USUARIO          │ ROL         │ PERMISOS │ CREADO POR│ ACCIONES   │   │
│  ├──────────────────┼─────────────┼──────────┼───────────┼────────────┤   │
│  │ ⓐ abner.hoyos@.. │ Usuario Bás.│   🔗     │ sistema.. │[Editar][🗑️]│   │
│  │ ⓐ alan.tauca@... │ Usuario Bás.│   🔗     │ sistema.. │[Editar][🗑️]│   │
│  └──────────────────┴─────────────┴──────────┴───────────┴────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 1. HEADER - Sección Superior

### 1.1 Título Principal
```html
<h1 style="
    font-size: 28px;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
">
    <i class="bi bi-people-fill" style="font-size: 32px; color: #4A5568;"></i>
    Administración de Usuarios
</h1>
```

**Especificaciones:**
- **Icono:** Bootstrap Icons `bi-people-fill` (👥)
- **Tamaño icono:** 32px
- **Color icono:** `#4A5568` (gris oscuro)
- **Texto:** "Administración de Usuarios"
- **Font-size:** 28px
- **Font-weight:** 600 (semi-bold)
- **Color texto:** `#2d3748` (casi negro)
- **Gap entre icono y texto:** 12px

### 1.2 Subtítulo
```html
<p style="
    font-size: 14px;
    color: #718096;
    margin-top: 0;
    margin-bottom: 24px;
">
    Gestión de permisos y roles de acceso al sistema
</p>
```

**Especificaciones:**
- **Texto:** "Gestión de permisos y roles de acceso al sistema"
- **Font-size:** 14px
- **Color:** `#718096` (gris medio)
- **Margin-bottom:** 24px

### 1.3 Botones de Acción (Grupo Superior Derecho)

**Layout:** 4 botones en fila, alineados a la derecha

#### Botón 1: Agregar Usuario (Primario)
```html
<a href="/admin/users/create" class="btn btn-primary" style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
    transition: all 0.3s ease;
">
    <i class="bi bi-plus-circle" style="margin-right: 6px;"></i>
    Agregar Usuario
</a>

<!-- Hover effect -->
<style>
.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
}
</style>
```

**Especificaciones:**
- **Icono:** `bi-plus-circle` (➕)
- **Fondo:** Gradiente `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Border-radius:** 8px
- **Padding:** 10px 20px
- **Font-size:** 14px
- **Font-weight:** 500
- **Box-shadow:** `0 4px 6px rgba(102, 126, 234, 0.3)`
- **Hover:** translateY(-2px) + shadow más fuerte

#### Botón 2: Historial de Cambios (Secundario)
```html
<a href="/admin/users/history" class="btn btn-outline-secondary" style="
    background: white;
    border: 1px solid #e2e8f0;
    color: #4a5568;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s ease;
">
    <i class="bi bi-clock-history" style="margin-right: 6px;"></i>
    Historial de Cambios
</a>

<style>
.btn-outline-secondary:hover {
    background: #f7fafc;
    border-color: #cbd5e0;
    transform: translateY(-1px);
}
</style>
```

**Especificaciones:**
- **Icono:** `bi-clock-history` (🕐)
- **Fondo:** `white`
- **Border:** `1px solid #e2e8f0`
- **Color texto:** `#4a5568`
- **Border-radius:** 8px
- **Padding:** 10px 20px
- **Hover:** Fondo `#f7fafc`, border `#cbd5e0`

#### Botón 3: Analíticas (Secundario)
```html
<a href="/admin/users/analytics" class="btn btn-outline-secondary" style="
    background: white;
    border: 1px solid #e2e8f0;
    color: #4a5568;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
">
    <i class="bi bi-graph-up" style="margin-right: 6px;"></i>
    Analíticas
</a>
```

**Especificaciones:**
- **Icono:** `bi-graph-up` (📈)
- Resto igual a Historial de Cambios

#### Botón 4: Volver al Dashboard (Secundario)
```html
<a href="/dashboard" class="btn btn-outline-secondary" style="
    background: white;
    border: 1px solid #e2e8f0;
    color: #4a5568;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
">
    <i class="bi bi-arrow-left" style="margin-right: 6px;"></i>
    Volver al Dashboard
</a>
```

**Especificaciones:**
- **Icono:** `bi-arrow-left` (←)
- Resto igual a botones secundarios

**Layout de grupo de botones:**
```html
<div style="
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-bottom: 32px;
">
    <!-- Los 4 botones aquí -->
</div>
```

---

## 📊 2. TARJETAS DE ESTADÍSTICAS (Cards Row)

### Layout Container
```html
<div class="stats-container" style="
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin-bottom: 40px;
">
    <!-- 3 cards aquí -->
</div>
```

### Card 1: Total Usuarios Activos
```html
<div class="stat-card" style="
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
">
    <!-- Icono -->
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        width: 64px;
        height: 64px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    ">
        <i class="bi bi-people-fill" style="
            font-size: 28px;
            color: white;
        "></i>
    </div>
    
    <!-- Contenido -->
    <div>
        <div style="
            font-size: 36px;
            font-weight: 700;
            color: #2d3748;
            line-height: 1;
            margin-bottom: 8px;
        ">44</div>
        <div style="
            font-size: 14px;
            color: #718096;
            font-weight: 500;
        ">Total Usuarios Activos</div>
    </div>
</div>

<style>
.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.12);
    border-color: #cbd5e0;
}
</style>
```

**Especificaciones Card 1:**
- **Icono:** `bi-people-fill` (👥)
- **Fondo icono:** Gradiente morado `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Tamaño icono container:** 64px × 64px
- **Border-radius icono:** 12px
- **Número:** 44 (font-size: 36px, weight: 700, color: `#2d3748`)
- **Label:** "Total Usuarios Activos" (font-size: 14px, color: `#718096`)
- **Hover:** translateY(-4px) + shadow más fuerte

### Card 2: Administradores
```html
<div class="stat-card" style="
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
">
    <!-- Icono -->
    <div style="
        background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);
        width: 64px;
        height: 64px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        <i class="bi bi-shield-check" style="
            font-size: 28px;
            color: white;
        "></i>
    </div>
    
    <!-- Contenido -->
    <div>
        <div style="font-size: 36px; font-weight: 700; color: #2d3748;">4</div>
        <div style="font-size: 14px; color: #718096;">Administradores</div>
    </div>
</div>
```

**Especificaciones Card 2:**
- **Icono:** `bi-shield-check` (🛡️)
- **Fondo icono:** Gradiente rojo `linear-gradient(135deg, #fc8181 0%, #f56565 100%)`
- Resto de specs iguales a Card 1

### Card 3: Cambios esta semana
```html
<div class="stat-card" style="
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
">
    <!-- Icono -->
    <div style="
        background: linear-gradient(135deg, #f6ad55 0%, #ed8936 100%);
        width: 64px;
        height: 64px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        <i class="bi bi-pencil-square" style="
            font-size: 28px;
            color: white;
        "></i>
    </div>
    
    <!-- Contenido -->
    <div>
        <div style="font-size: 36px; font-weight: 700; color: #2d3748;">49</div>
        <div style="font-size: 14px; color: #718096;">Cambios esta semana</div>
    </div>
</div>
```

**Especificaciones Card 3:**
- **Icono:** `bi-pencil-square` (✏️)
- **Fondo icono:** Gradiente naranja `linear-gradient(135deg, #f6ad55 0%, #ed8936 100%)`
- Resto de specs iguales a Card 1

---

## 📋 3. SECCIÓN LISTA DE USUARIOS

### 3.1 Título de Sección
```html
<h2 style="
    font-size: 20px;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
">
    <i class="bi bi-table" style="font-size: 22px; color: #4a5568;"></i>
    Lista de Usuarios
</h2>
```

**Especificaciones:**
- **Icono:** `bi-table` (📋)
- **Font-size:** 20px
- **Font-weight:** 600
- **Color:** `#2d3748`

### 3.2 Barra de Controles (Search + Filter + Clear)

```html
<div class="controls-bar" style="
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 16px;
    margin-bottom: 24px;
    align-items: center;
">
    <!-- Search Input -->
    <div style="position: relative;">
        <i class="bi bi-search" style="
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: #a0aec0;
            font-size: 16px;
        "></i>
        <input 
            type="text" 
            placeholder="Buscar Usuario..."
            style="
                width: 100%;
                padding: 12px 16px 12px 42px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                color: #2d3748;
                transition: all 0.3s ease;
            "
        />
    </div>
    
    <!-- Role Filter Dropdown -->
    <select style="
        padding: 12px 16px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-size: 14px;
        color: #4a5568;
        background: white;
        cursor: pointer;
        min-width: 180px;
    ">
        <option>🔽 Todos los roles</option>
        <option>admin_full</option>
        <option>admin_export</option>
        <option>analytics_viewer</option>
        <option>user_basic</option>
    </select>
    
    <!-- Clear Button -->
    <button style="
        padding: 12px 24px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background: white;
        color: #4a5568;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    ">
        <i class="bi bi-x-circle"></i>
        Limpiar
    </button>
</div>

<style>
input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

button:hover {
    background: #f7fafc;
    border-color: #cbd5e0;
}
</style>
```

**Especificaciones Barra de Controles:**
- **Layout:** Grid 3 columnas (1fr auto auto)
- **Gap:** 16px
- **Search input:**
  - Icono `bi-search` posicionado absoluto izquierda
  - Padding-left: 42px (para el icono)
  - Border-radius: 8px
  - Placeholder: "Buscar Usuario..."
- **Dropdown:**
  - Min-width: 180px
  - Icono 🔽 en el texto
- **Botón Limpiar:**
  - Icono `bi-x-circle`
  - Display flex con gap 8px

### 3.3 Selector de Registros por Página
```html
<div style="
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    font-size: 14px;
    color: #4a5568;
">
    <span>Mostrar</span>
    <select style="
        padding: 6px 12px;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        font-size: 14px;
        cursor: pointer;
    ">
        <option>25</option>
        <option>50</option>
        <option>100</option>
    </select>
    <span>registros</span>
</div>
```

---

## 📊 4. TABLA DE USUARIOS (DataTable)

### 4.1 Estructura de Tabla
```html
<div style="
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
">
    <table class="table" style="
        width: 100%;
        margin-bottom: 0;
    ">
        <thead style="
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-bottom: 2px solid #e2e8f0;
        ">
            <tr>
                <th style="
                    padding: 16px 20px;
                    font-size: 12px;
                    font-weight: 700;
                    color: #4a5568;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    border-bottom: none;
                ">USUARIO ▲</th>
                <th style="padding: 16px 20px; ...">ROL</th>
                <th style="padding: 16px 20px; ...">PERMISOS</th>
                <th style="padding: 16px 20px; ...">CREADO POR</th>
                <th style="padding: 16px 20px; ...">ACCIONES</th>
            </tr>
        </thead>
        <tbody>
            <!-- Filas de usuarios aquí -->
        </tbody>
    </table>
</div>
```

**Especificaciones Cabecera:**
- **Fondo:** Gradiente `linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)`
- **Border-bottom:** `2px solid #e2e8f0`
- **Font-size:** 12px
- **Font-weight:** 700
- **Color:** `#4a5568`
- **Text-transform:** uppercase
- **Letter-spacing:** 0.5px
- **Padding:** 16px 20px
- **Icono ordenamiento:** ▲ (en columna activa)

### 4.2 Fila de Usuario (Row Template)

```html
<tr style="
    border-bottom: 1px solid #f7fafc;
    transition: all 0.2s ease;
">
    <!-- COLUMNA 1: USUARIO -->
    <td style="padding: 16px 20px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <!-- Avatar -->
            <div style="
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 16px;
                font-weight: 600;
                flex-shrink: 0;
            ">A</div>
            
            <!-- Info -->
            <div>
                <div style="
                    font-size: 14px;
                    font-weight: 500;
                    color: #2d3748;
                    margin-bottom: 4px;
                ">abner.hoyos@agrovetmarket.com</div>
                <div style="
                    font-size: 12px;
                    color: #a0aec0;
                ">Actualizado 24 Mar 2026 10:07</div>
            </div>
        </div>
    </td>
    
    <!-- COLUMNA 2: ROL -->
    <td style="padding: 16px 20px;">
        <span style="
            background: #edf2f7;
            color: #4a5568;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            display: inline-block;
        ">Usuario Básico</span>
    </td>
    
    <!-- COLUMNA 3: PERMISOS -->
    <td style="padding: 16px 20px; text-align: center;">
        <a href="#" style="
            color: #667eea;
            font-size: 18px;
            text-decoration: none;
        ">
            <i class="bi bi-link-45deg"></i>
        </a>
    </td>
    
    <!-- COLUMNA 4: CREADO POR -->
    <td style="padding: 16px 20px;">
        <span style="
            font-size: 13px;
            color: #718096;
        ">sistema_migracion</span>
    </td>
    
    <!-- COLUMNA 5: ACCIONES -->
    <td style="padding: 16px 20px;">
        <div style="display: flex; gap: 8px;">
            <!-- Botón Editar -->
            <a href="/admin/users/edit/{{ email }}" style="
                padding: 8px 16px;
                background: white;
                border: 1px solid #667eea;
                color: #667eea;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                text-decoration: none;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 6px;
            ">
                <i class="bi bi-pencil"></i>
                Editar
            </a>
            
            <!-- Botón Eliminar -->
            <button style="
                padding: 8px 12px;
                background: white;
                border: 1px solid #fc8181;
                color: #fc8181;
                border-radius: 6px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.3s ease;
            ">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    </td>
</tr>

<style>
tr:hover {
    background: #f7fafc;
}

.btn-edit:hover {
    background: #667eea;
    color: white;
}

.btn-delete:hover {
    background: #fc8181;
    color: white;
}
</style>
```

**Especificaciones Fila Usuario:**

**Avatar:**
- Tamaño: 40px × 40px
- Border-radius: 50% (círculo perfecto)
- Fondo: Gradiente morado `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Letra: Primera letra del email en MAYÚSCULA
- Font-size letra: 16px
- Font-weight: 600
- Color letra: white

**Email:**
- Font-size: 14px
- Font-weight: 500
- Color: `#2d3748`

**Fecha actualización:**
- Font-size: 12px
- Color: `#a0aec0` (gris muy claro)
- Formato: "Actualizado DD MMM YYYY HH:mm"

**Badge de Rol:**
- Background: `#edf2f7` (gris muy claro)
- Color texto: `#4a5568`
- Padding: 6px 12px
- Border-radius: 6px
- Font-size: 13px
- Font-weight: 500

**Icono Permisos:**
- Icono: `bi-link-45deg` (🔗)
- Color: `#667eea` (morado)
- Font-size: 18px
- Text-align: center

**Botón Editar:**
- Background: white
- Border: `1px solid #667eea`
- Color: `#667eea`
- Padding: 8px 16px
- Border-radius: 6px
- Icono: `bi-pencil`
- Hover: Background `#667eea`, color white

**Botón Eliminar:**
- Background: white
- Border: `1px solid #fc8181`
- Color: `#fc8181`
- Padding: 8px 12px
- Border-radius: 6px
- Icono: `bi-trash`
- Hover: Background `#fc8181`, color white

**Row Hover:**
- Background: `#f7fafc`

---

## 🎨 5. PALETA DE COLORES EXACTA

### Colores Principales
```css
:root {
    /* Morado principal (gradiente) */
    --primary-start: #667eea;
    --primary-end: #764ba2;
    
    /* Rojo (administradores, eliminar) */
    --danger-start: #fc8181;
    --danger-end: #f56565;
    
    /* Naranja (cambios) */
    --warning-start: #f6ad55;
    --warning-end: #ed8936;
    
    /* Grises (texto y borders) */
    --gray-900: #2d3748;  /* Títulos */
    --gray-700: #4a5568;  /* Texto oscuro */
    --gray-600: #718096;  /* Texto medio */
    --gray-400: #cbd5e0;  /* Borders hover */
    --gray-300: #e2e8f0;  /* Borders */
    --gray-200: #edf2f7;  /* Fondos */
    --gray-100: #f7fafc;  /* Hover rows */
    --gray-500: #a0aec0;  /* Texto claro */
    
    /* Blanco */
    --white: #ffffff;
}
```

### Gradientes
```css
/* Gradiente Morado (botón principal, avatares) */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Gradiente Rojo (card administradores) */
background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);

/* Gradiente Naranja (card cambios) */
background: linear-gradient(135deg, #f6ad55 0%, #ed8936 100%);

/* Gradiente Gris Claro (thead tabla) */
background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
```

---

## 📏 6. TIPOGRAFÍA Y ESPACIADO

### Font Sizes
```css
/* Títulos */
--title-h1: 28px;        /* Administración de Usuarios */
--title-h2: 20px;        /* Lista de Usuarios */

/* Stats */
--stat-number: 36px;     /* 44, 4, 49 */
--stat-label: 14px;      /* Total Usuarios... */

/* Tabla */
--table-header: 12px;    /* USUARIO, ROL... (uppercase) */
--table-email: 14px;     /* abner.hoyos@... */
--table-date: 12px;      /* Actualizado 24... */
--table-badge: 13px;     /* Usuario Básico */
--table-creador: 13px;   /* sistema_migracion */

/* Botones */
--btn-text: 14px;        /* Agregar Usuario */
--btn-small: 13px;       /* Editar en tabla */

/* Inputs y controles */
--input-text: 14px;      /* Buscar Usuario... */
--subtitle: 14px;        /* Gestión de permisos... */
```

### Font Weights
```css
--fw-regular: 400;
--fw-medium: 500;
--fw-semibold: 600;
--fw-bold: 700;
```

### Espaciado (Margin/Padding)
```css
/* Margins */
--mb-xs: 8px;
--mb-sm: 16px;
--mb-md: 24px;
--mb-lg: 32px;
--mb-xl: 40px;

/* Paddings Cards */
--card-padding: 24px;

/* Paddings Tabla */
--table-padding: 16px 20px;

/* Paddings Botones */
--btn-padding-lg: 10px 20px;
--btn-padding-md: 8px 16px;
--btn-padding-sm: 6px 12px;

/* Gaps */
--gap-xs: 6px;
--gap-sm: 8px;
--gap-md: 12px;
--gap-lg: 16px;
--gap-xl: 20px;
--gap-xxl: 24px;
```

### Border Radius
```css
--radius-sm: 6px;       /* Badges, botones pequeños */
--radius-md: 8px;       /* Inputs, botones */
--radius-lg: 12px;      /* Cards, tabla, iconos stats */
--radius-full: 50%;     /* Avatares */
```

---

## 🎭 7. EFECTOS Y TRANSICIONES

### Sombras (Box Shadows)
```css
/* Sombra suave (cards, tabla) */
box-shadow: 0 1px 3px rgba(0,0,0,0.08);

/* Sombra media (hover cards) */
box-shadow: 0 8px 16px rgba(0,0,0,0.12);

/* Sombra botón primario */
box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);

/* Sombra botón primario hover */
box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);

/* Sombra focus input */
box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
```

### Transiciones
```css
/* Transición estándar (botones, cards) */
transition: all 0.3s ease;

/* Transición rápida (rows) */
transition: all 0.2s ease;

/* Transición focus input */
transition: border-color 0.3s ease, box-shadow 0.3s ease;
```

### Transforms (Hover)
```css
/* Hover botón primario */
transform: translateY(-2px);

/* Hover botón secundario */
transform: translateY(-1px);

/* Hover card */
transform: translateY(-4px);
```

---

## 📱 8. RESPONSIVE BREAKPOINTS

```css
/* Desktop (por defecto) */
@media (min-width: 1024px) {
    .stats-container {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .controls-bar {
        grid-template-columns: 1fr auto auto;
    }
}

/* Tablet */
@media (max-width: 1023px) {
    .stats-container {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .controls-bar {
        grid-template-columns: 1fr;
    }
    
    .btn-group {
        flex-direction: column;
    }
}

/* Mobile */
@media (max-width: 767px) {
    .stats-container {
        grid-template-columns: 1fr;
    }
    
    /* Ocultar columnas menos importantes */
    .table td:nth-child(4),  /* Creado por */
    .table th:nth-child(4) {
        display: none;
    }
    
    /* Botones acciones en vertical */
    .table td:last-child > div {
        flex-direction: column;
    }
}
```

---

## 🔤 9. ICONOS BOOTSTRAP ICONS

### Iconos Utilizados
```html
<!-- Header -->
<i class="bi bi-people-fill"></i>          <!-- Título principal -->
<i class="bi bi-plus-circle"></i>          <!-- Agregar Usuario -->
<i class="bi bi-clock-history"></i>        <!-- Historial -->
<i class="bi bi-graph-up"></i>             <!-- Analíticas -->
<i class="bi bi-arrow-left"></i>           <!-- Volver -->

<!-- Stats Cards -->
<i class="bi bi-people-fill"></i>          <!-- Total usuarios -->
<i class="bi bi-shield-check"></i>         <!-- Administradores -->
<i class="bi bi-pencil-square"></i>        <!-- Cambios -->

<!-- Controles -->
<i class="bi bi-search"></i>               <!-- Search input -->
<i class="bi bi-table"></i>                <!-- Lista de Usuarios -->
<i class="bi bi-x-circle"></i>             <!-- Limpiar -->

<!-- Tabla -->
<i class="bi bi-link-45deg"></i>           <!-- Permisos -->
<i class="bi bi-pencil"></i>               <!-- Editar -->
<i class="bi bi-trash"></i>                <!-- Eliminar -->
```

**CDN Bootstrap Icons:**
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
```

---

## 🎯 10. BADGES DE ROLES (Variantes de Color)

### admin_full
```html
<span style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
">Admin Full</span>
```

### admin_export
```html
<span style="
    background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
">Admin Export</span>
```

### analytics_viewer
```html
<span style="
    background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
">Analytics Viewer</span>
```

### user_basic
```html
<span style="
    background: #edf2f7;
    color: #4a5568;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
">Usuario Básico</span>
```

---

## 📦 11. CÓDIGO HTML COMPLETO EJEMPLO

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Administración de Usuarios</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    
    <style>
        :root {
            --primary-start: #667eea;
            --primary-end: #764ba2;
            --gray-900: #2d3748;
            --gray-700: #4a5568;
            --gray-600: #718096;
            --gray-300: #e2e8f0;
            --gray-100: #f7fafc;
        }
        
        body {
            background: #f7fafc;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }
        
        .container-main {
            max-width: 1400px;
            margin: 40px auto;
            padding: 32px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        /* ... resto de estilos según especificaciones arriba ... */
    </style>
</head>
<body>
    <div class="container-main">
        <!-- HEADER -->
        <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
                <h1 class="mb-2">
                    <i class="bi bi-people-fill me-3"></i>
                    Administración de Usuarios
                </h1>
                <p class="text-muted mb-0">
                    Gestión de permisos y roles de acceso al sistema
                </p>
            </div>
            
            <div class="d-flex gap-3">
                <a href="/admin/users/create" class="btn btn-primary">
                    <i class="bi bi-plus-circle me-2"></i>Agregar Usuario
                </a>
                <a href="/admin/users/history" class="btn btn-outline-secondary">
                    <i class="bi bi-clock-history me-2"></i>Historial de Cambios
                </a>
                <a href="/admin/users/analytics" class="btn btn-outline-secondary">
                    <i class="bi bi-graph-up me-2"></i>Analíticas
                </a>
                <a href="/dashboard" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left me-2"></i>Volver al Dashboard
                </a>
            </div>
        </div>
        
        <!-- STATS CARDS -->
        <div class="row g-4 mb-5">
            <div class="col-md-4">
                <div class="stat-card">
                    <div class="stat-icon stat-icon-primary">
                        <i class="bi bi-people-fill"></i>
                    </div>
                    <div>
                        <div class="stat-number">44</div>
                        <div class="stat-label">Total Usuarios Activos</div>
                    </div>
                </div>
            </div>
            <!-- ... otras cards ... -->
        </div>
        
        <!-- LISTA DE USUARIOS -->
        <h2 class="mb-4">
            <i class="bi bi-table me-2"></i>
            Lista de Usuarios
        </h2>
        
        <!-- CONTROLES -->
        <div class="controls-bar mb-4">
            <!-- Search, Filter, Clear -->
        </div>
        
        <!-- TABLA -->
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>USUARIO ▲</th>
                        <th>ROL</th>
                        <th>PERMISOS</th>
                        <th>CREADO POR</th>
                        <th>ACCIONES</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Rows según template -->
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## ✅ 12. CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: HTML Structure
- [ ] Header con título e icono `bi-people-fill`
- [ ] Subtítulo "Gestión de permisos..."
- [ ] 4 botones de acción superiores
- [ ] 3 cards de estadísticas
- [ ] Título sección "Lista de Usuarios"
- [ ] Barra de controles (search, filter, clear)
- [ ] Selector "Mostrar X registros"
- [ ] Tabla con 5 columnas

### Fase 2: Estilos CSS
- [ ] Paleta de colores (variables CSS)
- [ ] Gradientes morados, rojos, naranjas
- [ ] Tipografía (font-sizes y weights)
- [ ] Espaciado (margins, paddings, gaps)
- [ ] Border-radius consistente
- [ ] Box-shadows sutiles

### Fase 3: Interactividad
- [ ] Hover effects en botones (translateY)
- [ ] Hover effects en cards (translateY + shadow)
- [ ] Hover en rows de tabla (background)
- [ ] Focus state en input (border + shadow)
- [ ] Transiciones suaves (0.3s ease)

### Fase 4: Componentes Dinámicos
- [ ] Avatares con inicial del email
- [ ] Badges de roles con colores específicos
- [ ] Fechas en formato "Actualizado DD MMM YYYY HH:mm"
- [ ] Icono de permisos clickeable
- [ ] Botones Editar/Eliminar funcionales

### Fase 5: Responsive
- [ ] Grid 3 columnas en desktop
- [ ] Grid 2 columnas en tablet
- [ ] Grid 1 columna en mobile
- [ ] Ocultar columna "Creado por" en mobile
- [ ] Botones acciones en vertical en mobile

### Fase 6: Integración DataTables (Opcional)
- [ ] Inicializar DataTables con español
- [ ] Paginación personalizada
- [ ] Ordenamiento por columnas
- [ ] Búsqueda en tiempo real
- [ ] Export a Excel/PDF

---

## 🎨 13. VARIANTES DE AVATAR (Colores por Inicial)

Para diversificar los avatares según la inicial del email:

```javascript
function getAvatarColor(email) {
    const colors = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', // A-E (morado)
        'linear-gradient(135deg, #4299e1 0%, #3182ce 100%)', // F-J (azul)
        'linear-gradient(135deg, #48bb78 0%, #38a169 100%)', // K-O (verde)
        'linear-gradient(135deg, #f6ad55 0%, #ed8936 100%)', // P-T (naranja)
        'linear-gradient(135deg, #fc8181 0%, #f56565 100%)', // U-Z (rojo)
    ];
    
    const firstLetter = email.charAt(0).toUpperCase();
    const index = Math.floor((firstLetter.charCodeAt(0) - 65) / 5);
    return colors[Math.min(index, 4)];
}
```

---

## 📚 14. DEPENDENCIAS EXTERNAS

### CDN Links
```html
<!-- Bootstrap 5.3.3 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

<!-- Bootstrap Icons 1.11.3 -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">

<!-- DataTables 1.13.7 (opcional) -->
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/dataTables.bootstrap5.min.css">
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/dataTables.bootstrap5.min.js"></script>

<!-- Fuente (opcional) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

---

## 🚀 15. TIPS DE IMPLEMENTACIÓN

### 1. **Usar Variables CSS**
Define todas las variables en `:root` para facilitar cambios globales:
```css
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --danger-gradient: linear-gradient(135deg, #fc8181 0%, #f56565 100%);
    /* ... */
}
```

### 2. **Componentes Reutilizables**
Crea clases CSS para componentes comunes:
```css
.stat-card { /* estilos base */ }
.btn-primary { /* estilos base */ }
.badge-role { /* estilos base */ }
```

### 3. **Hover States Consistentes**
Todos los elementos interactivos deben tener feedback visual:
- Botones: translateY + shadow
- Cards: translateY + shadow + border
- Rows: background color

### 4. **Accesibilidad**
- Labels para inputs ocultos
- ARIA labels para botones con solo iconos
- Contraste mínimo 4.5:1 (WCAG AA)

### 5. **Performance**
- Lazy load de avatares si hay muchos usuarios
- Pagination para tablas grandes (25 registros default)
- Debounce en search input (300ms)

---

## 📸 CAPTURA DE REFERENCIA

**URL:** `https://dashboard-ventas-d7ff.onrender.com/admin/users`

**Características visuales clave:**
1. Gradiente morado principal (todo el sistema)
2. Cards con iconos grandes (64px) en gradiente
3. Tabla limpia con hover sutil
4. Avatares circulares con iniciales
5. Badges de roles con colores distintivos
6. Botones con bordes redondeados (8px)
7. Sombras sutiles en todos los elementos
8. Espaciado generoso (no apretado)

---

## 🎯 RESULTADO ESPERADO

Al implementar esta especificación, deberías obtener:

✅ **Interfaz moderna y profesional** con gradientes y sombras sutiles  
✅ **Navegación intuitiva** con botones claramente identificados  
✅ **Estadísticas visuales** con cards atractivas  
✅ **Tabla limpia y legible** con hover states  
✅ **Responsive design** que funciona en todos los dispositivos  
✅ **Consistencia visual** con el resto del dashboard  
✅ **Accesibilidad** con contrastes adecuados  
✅ **Performance** con transiciones suaves

---

**FIN DEL DOCUMENTO**

📝 Para dudas o aclaraciones, referirse a:
- `templates/admin/users_list.html` (implementación real)
- `static/css/admin_styles.css` (estilos completos)
- `docs/GUIA_IMPLEMENTACION_MODULO_ADMIN.md` (guía de implementación)
