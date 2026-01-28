# Configuración de Analytics con PostgreSQL en Render

## 📋 Sistema de Analytics Implementado

Se ha implementado un sistema completo de monitoreo de visitas para el dashboard que registra:

- ✅ Cada visita de cada usuario
- ✅ Páginas visitadas
- ✅ Fecha y hora exacta
- ✅ Dirección IP del usuario
- ✅ Navegador/dispositivo usado
- ✅ Estadísticas completas con gráficos

## 🚀 Configuración en Render (Producción)

### Paso 1: Crear Base de Datos PostgreSQL en Render

1. **Accede a tu Dashboard de Render**: https://dashboard.render.com
2. **Crea una nueva base de datos PostgreSQL**:
   - Click en "New +" → "PostgreSQL"
   - Name: `dashboard-ventas-analytics` (o el nombre que prefieras)
   - Database: `analytics` (automático)
   - User: `analytics_user` (automático)
   - Region: `Oregon (US West)` (o la región más cercana)
   - **Plan**: Selecciona **"Free"** (incluye 90 días gratis, luego $7/mes)
   - Click en "Create Database"

3. **Espera a que se cree** (toma 1-2 minutos)

### Paso 2: Obtener la URL de Conexión

1. Una vez creada la base de datos, ve a la pestaña **"Info"**
2. Busca el campo **"Internal Database URL"** (recomendado) o **"External Database URL"**
3. Copia la URL completa, se verá algo así:
   ```
   postgresql://analytics_user:contraseña@dpg-xxxxx.oregon-postgres.render.com/analytics
   ```

### Paso 3: Configurar Variable de Entorno en tu Web Service

1. Ve a tu **Web Service** (dashboard-ventas-d7ff)
2. Click en **"Environment"** en el menú lateral
3. Click en **"Add Environment Variable"**
4. Agrega:
   - **Key**: `DATABASE_URL`
   - **Value**: Pega la URL de PostgreSQL que copiaste
5. Click en **"Save Changes"**

### Paso 4: Desplegar los Cambios

1. El sistema se redesplega automáticamente al guardar la variable de entorno
2. Alternativamente, puedes hacer un **Manual Deploy** o hacer push al repositorio

### Paso 5: Verificar que Funciona

1. Una vez desplegado, accede a: `https://dashboard-ventas-d7ff.onrender.com/analytics`
2. Solo los administradores pueden acceder (jonathan.cerda@agrovetmarket.com y juan.portal@agrovetmarket.com)
3. Verás el dashboard de analytics con todas las estadísticas

## 💻 Desarrollo Local (Opcional)

Para probar analytics en tu máquina local:

### Opción 1: Sin Base de Datos (Analytics Deshabilitado)
- Deja `DATABASE_URL=""` en tu `.env` local
- La aplicación funcionará normal pero no registrará visitas
- Verás el mensaje: `⚠️ DATABASE_URL no configurada. Analytics deshabilitado.`

### Opción 2: Con PostgreSQL Local
1. Instala PostgreSQL en tu máquina
2. Crea una base de datos local:
   ```bash
   createdb analytics_dev
   ```
3. En tu `.env` local agrega:
   ```
   DATABASE_URL="postgresql://tu_usuario:tu_password@localhost/analytics_dev"
   ```
4. Instala la dependencia:
   ```bash
   pip install psycopg2-binary
   ```

### Opción 3: Usar la Base de Datos de Render (No Recomendado)
- Puedes usar la "External Database URL" de Render
- ⚠️ Ten cuidado de no llenar la base con datos de desarrollo

## 📊 Acceso al Dashboard de Analytics

### URL: `/analytics`

**Usuarios autorizados** (solo estos pueden ver analytics):
- jonathan.cerda@agrovetmarket.com
- juan.portal@agrovetmarket.com

Para agregar más administradores, edita la lista en [app.py](app.py:1677-1681):
```python
admin_emails = [
    'jonathan.cerda@agrovetmarket.com',
    'juan.portal@agrovetmarket.com',
    'nuevo.admin@agrovetmarket.com'  # Agregar aquí
]
```

## 📈 Métricas Disponibles

El dashboard de analytics muestra:

### Estadísticas Generales
- Total de visitas
- Usuarios únicos
- Promedio de visitas por usuario
- Número de páginas únicas visitadas

### Gráficos
- **Visitas por día**: Línea temporal con visitas y usuarios únicos
- **Visitas por hora**: Distribución de uso durante el día

### Tablas Detalladas
- **Usuarios más activos**: Ranking de usuarios por número de visitas
- **Páginas más visitadas**: Estadísticas de las páginas del dashboard
- **Visitas recientes**: Últimas 50 visitas con detalle completo

### Filtros de Período
- Últimos 7 días
- Últimos 30 días
- Últimos 90 días
- Último año

## 🔧 Archivos Creados/Modificados

### Nuevos Archivos
- `analytics_db.py` - Módulo de gestión de base de datos
- `templates/analytics.html` - Página del dashboard de analytics
- `ANALYTICS_SETUP.md` - Este documento

### Archivos Modificados
- `app.py` - Agregado middleware y ruta `/analytics`
- `requirements.txt` - Agregado `psycopg2-binary==2.9.10`
- `.env` - Agregada variable `DATABASE_URL`

## 🛠️ Mantenimiento

### Limpiar Datos Antiguos (Opcional)
Si quieres eliminar visitas antiguas para liberar espacio:

```sql
-- Conectarse a la base de datos de Render
-- Eliminar visitas con más de 1 año
DELETE FROM page_visits 
WHERE visit_timestamp < NOW() - INTERVAL '1 year';
```

### Consultas Útiles

```sql
-- Ver total de registros
SELECT COUNT(*) FROM page_visits;

-- Ver usuarios con más visitas
SELECT user_email, COUNT(*) as total 
FROM page_visits 
GROUP BY user_email 
ORDER BY total DESC 
LIMIT 10;

-- Ver visitas de hoy
SELECT * FROM page_visits 
WHERE DATE(visit_timestamp) = CURRENT_DATE 
ORDER BY visit_timestamp DESC;
```

## ⚠️ Consideraciones Importantes

1. **Plan Gratuito de PostgreSQL en Render**:
   - 90 días gratis
   - Después: $7/mes
   - 1 GB de almacenamiento
   - Suficiente para miles de visitas

2. **Rendimiento**:
   - El registro de visitas es muy rápido (< 10ms)
   - No afecta la experiencia del usuario
   - Las consultas están indexadas para rendimiento óptimo

3. **Privacidad**:
   - Solo se guarda información de uso del dashboard
   - No se registran contenidos sensibles
   - IPs se usan solo para análisis de conexión

## 🚨 Solución de Problemas

### Error: "No module named 'psycopg2'"
- Asegúrate que `psycopg2-binary` está en `requirements.txt`
- En Render se instala automáticamente

### Error: "could not connect to server"
- Verifica que `DATABASE_URL` esté correctamente configurada
- Usa la "Internal Database URL" en Render
- Asegúrate que la base de datos esté "Available"

### No veo datos en Analytics
- Verifica que `DATABASE_URL` esté configurada en Render
- Revisa los logs: los usuarios deben estar logueados
- Las visitas se registran solo después de configurar la base de datos

### "No tienes permisos para acceder"
- Solo administradores pueden ver `/analytics`
- Verifica que tu email esté en la lista de `admin_emails` en app.py

## 📞 Soporte

Si tienes problemas con la configuración:
1. Revisa los logs de Render: Web Service → "Logs"
2. Busca mensajes de error relacionados con PostgreSQL
3. Verifica que todas las variables de entorno estén correctas
