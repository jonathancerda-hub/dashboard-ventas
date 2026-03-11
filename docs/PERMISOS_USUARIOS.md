# Permisos de Usuarios - Dashboard de Ventas

Este documento detalla los permisos y niveles de acceso de los usuarios en el sistema de Dashboard de Ventas.

---

## 📊 Niveles de Permisos

### 1. **Usuario Básico**
Acceso estándar al dashboard principal con visualización de datos.

**Permisos:**
- ✅ Acceso al Dashboard Principal (`/dashboard`)
- ✅ Visualización de datos de ventas
- ✅ Uso de filtros (año, mes, vendedor, línea comercial)
- ✅ Visualización de gráficos y estadísticas
- ✅ Acceso a Dashboard por Línea (`/dashboard_linea`)
- ✅ Acceso a Equipo de Ventas (`/equipo_ventas`)
- ✅ Acceso a Metas de Vendedor (`/metas_vendedor`)
- ❌ No puede exportar datos
- ❌ No puede acceder a Ventas Farmacéuticas
- ❌ No puede ver Analytics

---

### 2. **Administrador - Ventas Farmacéuticas**
Usuarios con acceso a la sección especializada de ventas farmacéuticas.

**Usuarios con este permiso:**
- jonathan.cerda@agrovetmarket.com
- janet.hueza@agrovetmarket.com
- juan.portal@agrovetmarket.com
- juana.lobaton@agrovetmarket.com

**Permisos adicionales:**
- ✅ Todos los permisos de Usuario Básico
- ✅ Acceso a Ventas Farmacéuticas (`/sales`)
- ✅ Visualización de datos farmacéuticos detallados
- ✅ Filtros avanzados por cliente, línea y fechas
- ❌ No pueden exportar (solo visualizar)

---

### 3. **Administrador - Exportación de Datos**
Usuarios autorizados para exportar datos a Excel.

**Usuarios con este permiso:**

#### Exportación de Dashboard Principal:
- jonathan.cerda@agrovetmarket.com
- janet.hueza@agrovetmarket.com
- juan.portal@agrovetmarket.com
- AMAHOdoo@agrovetmarket.com
- miguel.hernandez@agrovetmarket.com
- juana.lobaton@agrovetmarket.com
- jimena.delrisco@agrovetmarket.com

#### Exportación de Ventas Farmacéuticas:
- jonathan.cerda@agrovetmarket.com
- janet.hueza@agrovetmarket.com
- juan.portal@agrovetmarket.com
- AMAHOdoo@agrovetmarket.com
- miguel.hernandez@agrovetmarket.com
- juana.lobaton@agrovetmarket.com
- jimena.delrisco@agrovetmarket.com

**Permisos adicionales:**
- ✅ Exportar Detalle de Dashboard (`/export/dashboard/details`)
- ✅ Exportar Ventas Farmacéuticas (`/export/excel/sales`)
- ✅ Descargar archivos Excel con datos completos
- ✅ Exportación con formato profesional (colores Odoo, bordes, autoajuste)

---

### 4. **Administrador - Analytics**
Usuarios con acceso al sistema de monitoreo y estadísticas de uso del dashboard.

**Usuarios con este permiso:**
- jonathan.cerda@agrovetmarket.com
- juan.portal@agrovetmarket.com
- ena.fernandez@agrovetmarket.com
- juana.lobaton@agrovetmarket.com

**Permisos adicionales:**
- ✅ Acceso al Dashboard de Analytics (`/analytics`)
- ✅ Visualización de estadísticas de uso:
  - Total de visitas al sistema
  - Usuarios únicos activos
  - Ratio de adopción (usuarios activos / total permitidos)
  - Visitas por usuario
  - Visitas por página
  - Gráficos de visitas por día
  - Gráficos de visitas por hora
  - Tabla de visitas recientes
- ✅ Filtrado por período (7, 30, 60, 90 días)
- ✅ Visualización con Google Charts

---

## 👥 Listado de Usuarios por Nivel de Acceso

### **Superadministradores** (Todos los permisos)
Usuarios con acceso completo a todas las funcionalidades del sistema.

| Usuario | Email | Permisos |
|---------|-------|----------|
| Jonathan Cerda | jonathan.cerda@agrovetmarket.com | Usuario Básico + Ventas Farmacéuticas + Exportación + Analytics |
| Juan Portal | juan.portal@agrovetmarket.com | Usuario Básico + Ventas Farmacéuticas + Exportación + Analytics |
| Juana Lobatón | juana.lobaton@agrovetmarket.com | Usuario Básico + Ventas Farmacéuticas + Exportación + Analytics |

---

### **Administradores Especializados**

| Usuario | Email | Permisos |
|---------|-------|----------|
| Janet Hueza | janet.hueza@agrovetmarket.com | Usuario Básico + Ventas Farmacéuticas + Exportación |
| Ena Fernández | ena.fernandez@agrovetmarket.com | Usuario Básico + Analytics |
| Miguel Hernández | miguel.hernandez@agrovetmarket.com | Usuario Básico + Exportación |
| AMAHOdoo | AMAHOdoo@agrovetmarket.com | Usuario Básico + Exportación |
| Jimena del Risco | jimena.delrisco@agrovetmarket.com | Usuario Básico + Exportación |

---

### **Usuarios Básicos** (Solo visualización)
Todos los demás usuarios en el archivo `allowed_users.json` tienen acceso básico:

- jean.delacruz@agrovetmarket.com
- nicole.bendezu@agrovetmarket.com
- karina.guillen@agrovetmarket.com
- abner.hoyos@agrovetmarket.com
- pedro.calderon@agrovetmarket.com
- stephanie.hiyagon@agrovetmarket.com
- jose.quea@agrovetmarket.com
- orlando.jaimes@agrovetmarket.com
- jancarlo.pariasca@agrovetmarket.com
- carmen.morales@agrovetmarket.com
- erick.arias@agrovetmarket.com
- manuel.bravo@agrovetmarket.com
- umberto.calderon@agrovetmarket.com
- willy.calderon@agrovetmarket.com
- stefanny.rios@agrovetmarket.com
- michael.vilchez@agrovetmarket.com
- deysi.campo@agrovetmarket.com
- irvin.tomas@agrovetmarket.com
- perci.mondragon@agrovetmarket.com
- kattya.barcena@agrovetmarket.com
- alan.tauca@agrovetmarket.com
- johanna.hurtado@agrovetmarket.com
- jimena.delrisco@agrovetmarket.com
- rommel.chinchay@agrovetmarket.com
- cotizacionesAM@agrovetmarket.com
- yohani.mera@agrovetmarket.com
- regina.martinez@agrovetmarket.com
- kevin.sanchez@agrovetmarket.com
- zaida.rojas@agrovetmarket.com
- sharon.francisco@agrovetmarket.com
- ivan.ramos@agrovetmarket.com
- ximena.beltran@agrovetmarket.com
- fernando.paredes@agrovetmarket.com
- veronica.campos@agrovetmarket.com
- jose.garcia@agrovetmarket.com
- maria.angulo@agrovetmarket.com

---

## 🔧 Gestión de Permisos

### Cómo modificar permisos:

#### 1. **Agregar usuario al sistema**
Editar el archivo `allowed_users.json`:
```json
{
    "allowed_emails": [
        "nuevo.usuario@agrovetmarket.com"
    ]
}
```

#### 2. **Otorgar permisos especiales**
Editar el archivo `app.py` en las secciones correspondientes:

**Para Ventas Farmacéuticas** (línea ~232):
```python
admin_users = ["usuario@agrovetmarket.com", ...]
```

**Para Exportación de Dashboard** (líneas ~318, ~793, ~1174, ~1539):
```python
admin_users = ["usuario@agrovetmarket.com", ...]
```

**Para Exportación de Ventas** (línea ~1319):
```python
admin_users = ["usuario@agrovetmarket.com", ...]
```

**Para Analytics** (línea ~1734):
```python
admin_emails = [
    'usuario@agrovetmarket.com',
    ...
]
```

#### 3. **Desplegar cambios**
```bash
git add -A
git commit -m "Actualizar permisos de usuario"
git push
```

Los cambios se desplegarán automáticamente en Render.

---

## 📋 Notas Importantes

1. **Seguridad**: Todos los usuarios deben autenticarse con Google OAuth 2.0 usando su cuenta @agrovetmarket.com
2. **Auditoría**: El sistema de Analytics registra todas las visitas y accesos
3. **Confidencialidad**: Todos los datos están protegidos por el disclaimer del footer
4. **Total de usuarios permitidos**: 43 usuarios en el sistema
5. **Última actualización**: 30 de enero de 2026

---

## 🔄 Historial de Cambios Recientes

| Fecha | Usuario | Cambio |
|-------|---------|--------|
| 30/01/2026 | juana.lobaton@agrovetmarket.com | ➕ Agregada como superadministradora (todos los permisos) |
| 29/01/2026 | miguel.hernandez@agrovetmarket.com | ➕ Agregado permiso de exportación |
| 29/01/2026 | ena.fernandez@agrovetmarket.com | ➕ Agregado permiso de analytics |

---

## 📞 Contacto para Permisos

Para solicitar cambios en permisos o accesos, contactar a:
- **Jonathan Cerda**: jonathan.cerda@agrovetmarket.com
- **Juan Portal**: juan.portal@agrovetmarket.com
- **Juana Lobatón**: juana.lobaton@agrovetmarket.com
