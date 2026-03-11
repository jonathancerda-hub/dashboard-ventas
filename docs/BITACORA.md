# Bitácora de Cambios del Proyecto - Dashboard de Ventas

Este documento registra los cambios y funcionalidades más importantes implementadas a lo largo del desarrollo del proyecto.

---

### Versión 3.0: Actualización de Seguridad - A06 OWASP (11/marzo/2026)

**🔒 ACTUALIZACIÓN CRÍTICA DE SEGURIDAD**

- **Auditoría de Componentes:** Realizada con `pip-audit` detectando 19 vulnerabilidades conocidas (CVEs)
- **Componentes Actualizados:**
  - `Authlib`: 1.3.1 → 1.6.7 (fixes 5 CVEs)
  - `Flask`: 3.1.1 → 3.1.3 (fixes CVE-2026-27205)
  - `Werkzeug`: 3.1.3 → 3.1.6 (fixes 3 CVEs)
  - `urllib3`: 2.5.0 → 2.6.3 (fixes 3 CVEs)
  - `pillow`: 11.3.0 → 12.1.1 (fixes CVE-2026-25990)
  - `pyasn1`: 0.6.1 → 0.6.2 (fixes CVE-2026-23490)
  - `pandas`: 2.3.1 → 2.2.3 (downgrade controlado por estabilidad)
  - `pip`: 24.0 → 26.0.1 (fixes 2 CVEs)
  - `setuptools`: 65.5.0 → 82.0.1 (fixes múltiples PYSEC)
- **Resultado:** 19 CVEs → 0 CVEs ✅
- **Puntuación OWASP A06:** 7/10 → 10/10 ✅
- **Auditoría Trimestral:** Implementada con `pip-audit` y `safety check`

---

### Versión 1.0: Funcionalidad Inicial

- **Conexión con Odoo:** Establecimiento de la conexión con la base de datos de Odoo para la extracción de datos de ventas.
- **Dashboard General:** Creación del dashboard principal con:
  - KPIs de rendimiento (Meta, Venta, Avance, etc.).
  - Tabla de avance por línea comercial.
  - Gráficos de "Venta por Tipo de Producto", "Top 7 Productos" y "Venta por Línea Comercial".
- **Gestión de Metas por Línea:** Interfaz para establecer las metas mensuales para cada línea comercial.
- **Vista de Líneas de Venta:** Tabla detallada con todas las líneas de venta y filtros por fecha, cliente y línea.

---

### Versión 2.0: Gestión de Equipos y Metas Individuales

- **Dashboard por Vendedor:** Creación de un dashboard detallado por línea comercial, mostrando el rendimiento de cada vendedor.
- **Gestión de Equipos y Metas:** Implementación de una nueva interfaz unificada para:
  - Asignar vendedores a equipos de venta.
  - Establecer metas individuales (Total e IPN) para cada vendedor en una vista de tabla dinámica anual.
- **Mejoras de UI:**
  - Formateo de números con separadores de miles en los campos de metas.
  - Optimización del diseño de las tablas para una mejor visualización.

---

### Versión 3.0: Integración con Google Sheets y Mejoras de UI

- **Integración con Google Sheets:** Migración completa de la gestión de metas (por línea y por vendedor) y equipos desde archivos locales (`.json`) a una única hoja de cálculo de Google Sheets, centralizando la fuente de datos.
- **Mejoras en Dashboard de Vendedor:**
  - Se añadió la columna **"Vencimiento < 6 Meses"** para un análisis más completo.
  - Se incorporó un nuevo **gráfico de barras "Meta vs. Venta por Vendedor"**.
  - Se estandarizó el formato de números en las ventanas emergentes (tooltips) de todos los gráficos para no mostrar decimales.
- **Preparación para Despliegue:** Se añadió `gunicorn` y se limpió el archivo `requirements.txt` para asegurar la compatibilidad con servicios de despliegue como Render.com.

---

### Versión 3.1: Mejoras de Flujo y Usabilidad

- **Flujo de Usuario Optimizado:**
  - La página de inicio después del login es ahora el **Dashboard Principal**.
  - La página de "Ventas" ya no carga datos por defecto, mejorando la velocidad de carga inicial. Los datos se obtienen al presionar "Buscar".
- **Interfaz de Ventas Simplificada:**
  - Se eliminó el filtro por "Cliente".
  - El botón "Buscar" ahora carga los datos de los últimos 30 días si no se especifican fechas.
- **Personalización de UI:** Se muestra el nombre del usuario que ha iniciado sesión debajo del título principal en los dashboards.
- **Corrección de Errores:** Solucionado un error que impedía la carga de los filtros en la página de "Ventas".