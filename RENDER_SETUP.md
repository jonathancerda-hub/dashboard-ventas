# Configuración de Render.com

## Variables de Entorno Requeridas

En el panel de Render.com, ve a tu servicio > **Environment** y agrega las siguientes variables:

### 1. SECRET_KEY
Tu clave secreta de Flask (ya la tienes configurada)

### 2. ODOO_URL
URL de tu servidor Odoo (ya la tienes configurada)

### 3. ODOO_DB
Nombre de tu base de datos Odoo (ya la tienes configurada)

### 4. GOOGLE_SHEET_NAME
Nombre de tu hoja de Google Sheets (ya la tienes configurada)

### 5. ALLOWED_USERS (NUEVA)
**Nombre de la variable:** `ALLOWED_USERS`

**Valor:** Copia y pega exactamente esta línea (todos los correos separados por comas sin espacios después de cada coma):

```
jean.delacruz@agrovetmarket.com,nicole.bendezu@agrovetmarket.com,karina.guillen@agrovetmarket.com,abner.hoyos@agrovetmarket.com,pedro.calderon@agrovetmarket.com,stephanie.hiyagon@agrovetmarket.com,jose.quea@agrovetmarket.com,ena.fernandez@agrovetmarket.com,orlando.jaimes@agrovetmarket.com,jancarlo.pariasca@agrovetmarket.com,carmen.morales@agrovetmarket.com,erick.arias@agrovetmarket.com,manuel.bravo@agrovetmarket.com,umberto.calderon@agrovetmarket.com,willy.calderon@agrovetmarket.com,stefanny.rios@agrovetmarket.com,michael.vilchez@agrovetmarket.com,deysi.campo@agrovetmarket.com,irvin.tomas@agrovetmarket.com,perci.mondragon@agrovetmarket.com,kattya.barcena@agrovetmarket.com,alan.tauca@agrovetmarket.com,johanna.hurtado@agrovetmarket.com,jimena.delrisco@agrovetmarket.com,miguel.hernandez@agrovetmarket.com,rommel.chinchay@agrovetmarket.com,cotizacionesAM@agrovetmarket.com,yohani.mera@agrovetmarket.com,regina.martinez@agrovetmarket.com,kevin.sanchez@agrovetmarket.com,zaida.rojas@agrovetmarket.com,sharon.francisco@agrovetmarket.com,ivan.ramos@agrovetmarket.com,ximena.beltran@agrovetmarket.com,fernando.paredes@agrovetmarket.com,veronica.campos@agrovetmarket.com,janet.hueza@agrovetmarket.com,jose.garcia@agrovetmarket.com,jonathan.cerda@agrovetmarket.com,AMAHOdoo@agrovetmarket.com
```

## Pasos para Configurar en Render

1. Ve a tu dashboard de Render: https://dashboard.render.com/
2. Selecciona tu servicio "dashboard-ventas"
3. Ve a la pestaña **Environment**
4. Click en **Add Environment Variable**
5. Agrega:
   - **Key:** `ALLOWED_USERS`
   - **Value:** Pega la cadena de correos de arriba
6. Click en **Save Changes**
7. Render automáticamente redesplegará tu aplicación con la nueva configuración

## Nota Importante

- El archivo `allowed_users.json` NO se sube al repositorio (está en .gitignore)
- En desarrollo local, la app seguirá usando el archivo `allowed_users.json`
- En producción (Render), la app usará la variable de entorno `ALLOWED_USERS`
- Para agregar nuevos usuarios, actualiza la variable de entorno en Render

## Verificación

Después de configurar, verifica que:
1. El despliegue se complete sin errores
2. Puedas iniciar sesión con alguno de los correos autorizados
3. Los usuarios no autorizados vean el mensaje "No tienes permiso para acceder"
