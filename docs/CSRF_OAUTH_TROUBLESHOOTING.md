# 🔒 CSRF OAuth2 - Troubleshooting

> **Error:** `mismatching_state: CSRF Warning! State not equal in request and response`  
> **Fecha:** 23 de abril de 2026  
> **Sistema:** Dashboard Ventas - Google OAuth2

---

## 📋 ¿Qué Es Este Error?

**CSRF (Cross-Site Request Forgery) Protection** en OAuth2:
- OAuth2 genera un token aleatorio (`state`) al iniciar el login
- Google devuelve ese mismo token en el callback
- Si no coinciden → **⚠️ WARNING** → Posible ataque o problema de sesión

---

## 🔍 Causas Comunes en Producción

### 1. **Sesión Perdida (Cookie Expirada o Bloqueada)**

**Síntoma:** Usuario tarda mucho en Google, sesión Flask expira antes de volver

**Diagnóstico:**
```python
# app.py - Configuración actual
PERMANENT_SESSION_LIFETIME=timedelta(hours=8)  # Sesión expira en 8 horas
SESSION_COOKIE_SECURE=os.getenv('FLASK_ENV') == 'production'  # True en prod
SESSION_COOKIE_SAMESITE='Lax'  # Permite OAuth redirects
```

**¿Puede pasar?**
- ✅ Usuario se distrae en Google > 8 horas (poco probable)
- ✅ Navegador bloquea cookies de terceros (común en modo incógnito)
- ✅ Extensions de privacidad (uBlock Origin, Privacy Badger)

**Solución:**
```python
# Aumentar timeout solo para OAuth (opcional)
PERMANENT_SESSION_LIFETIME=timedelta(hours=12)

# O verificar cookies en navegador del usuario
# Chrome: F12 → Application → Cookies → buscar "session"
```

---

### 2. **Multiple Tabs/Windows (State Collision)**

**Síntoma:** Usuario abre múltiples tabs de login simultáneamente

**Flujo problemático:**
```
Tab 1: /google-oauth → state="abc123"
Tab 2: /google-oauth → state="xyz789" (SOBRESCRIBE session['state'])
Tab 1: /authorize?state=abc123 → ❌ No coincide con "xyz789"
```

**Solución:**
- Usuario debe cerrar tabs duplicadas
- Limpiar cache del navegador (Ctrl+Shift+Del)

---

### 3. **Redirect URI Mismatch (Configuración Google)**

**Síntoma:** URL de callback no coincide con Google Cloud Console

**Verificar en Google Cloud Console:**
```
https://console.cloud.google.com/apis/credentials

OAuth 2.0 Client IDs → [Tu Cliente] → Authorized redirect URIs

✅ DEBE INCLUIR:
   https://dashboard-ventas-d7ff.onrender.com/authorize
   http://localhost:5000/authorize (desarrollo)

❌ NO DEBE TENER:
   URLs con typos
   URLs sin /authorize al final
   HTTP en producción
```

**Cómo verificar en código:**
```python
# app.py línea 776
redirect_uri = url_for('authorize', _external=True)
# Resultado debe ser: https://dashboard-ventas-d7ff.onrender.com/authorize
```

---

### 4. **Proxy/Load Balancer (Render.com)**

**Síntoma:** Headers HTTP incorrectos en producción

**Problema:** Render.com termina HTTPS, Flask ve HTTP internamente

**Configuración actual (app.py):**
```python
SESSION_COOKIE_SECURE=os.getenv('FLASK_ENV') == 'production'  # True en prod
```

**Puede causar problemas si:** Render.com no envía headers `X-Forwarded-Proto: https`

**Solución (agregar ProxyFix):**
```python
from werkzeug.middleware.proxy_fix import ProxyFix

# Después de crear app
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
```

---

### 5. **Cache del Navegador (Página Cacheada)**

**Síntoma:** Usuario usa botón "Atrás" del navegador después de error

**Flujo:**
```
1. Login fallido → Error CSRF
2. Usuario presiona "Atrás"
3. Página cacheada con state viejo → ❌ Falla de nuevo
```

**Solución:**
```python
# Ya implementado en app.py:
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Sin cache

# Headers de seguridad (@app.after_request):
response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
```

---

### 6. **Navegadores con Privacidad Estricta**

**Síntomas:**
- Safari con "Prevent Cross-Site Tracking" activado
- Brave con Shields UP
- Firefox con Enhanced Tracking Protection

**Diagnóstico:**
```javascript
// Probar en consola del navegador (F12)
document.cookie
// Si está vacío o sin "session=" → cookies bloqueadas
```

**Solución:**
- Pedir al usuario agregar tu dominio a excepciones
- Documentar en manual que debe permitir cookies

---

## 🛠️ Cómo Diagnosticar en Producción

### Paso 1: Ver Logs de Render.com

```bash
# Buscar en logs:
grep "mismatching_state" logs.txt
grep "CSRF Warning" logs.txt
grep "oauth_error" logs.txt
```

### Paso 2: Verificar IP del Usuario

Si el usuario reporta el error, buscar su IP en Analytics:

```sql
-- En Supabase (tabla page_visits_ventas_locales)
SELECT * FROM page_visits_ventas_locales
WHERE ip_address = '10.31.69.132'
ORDER BY visit_timestamp DESC
LIMIT 10;

-- Ver si tiene visitas exitosas antes/después
```

### Paso 3: Reproducir Escenario

**Test 1: Login Normal**
```
1. Abrir https://dashboard-ventas-d7ff.onrender.com/login
2. Click "Iniciar con Google"
3. Autenticar
4. ¿Funciona? → ✅ OAuth OK
```

**Test 2: Sesión Expirada**
```
1. Abrir /login
2. Click "Iniciar con Google"
3. ESPERAR 10 minutos en página de Google
4. Completar autenticación
5. ¿Error CSRF? → ⚠️ Timeout de sesión
```

**Test 3: Multiple Tabs**
```
1. Abrir 2 tabs de /login
2. Click "Iniciar con Google" en AMBAS tabs (rápido)
3. Completar en una tab
4. ¿Error CSRF? → ⚠️ State collision
```

---

## ✅ Soluciones Implementadas

### 1. Error Logging Mejorado

```python
# app.py línea 881-893 (ya implementado)
except Exception as e:
    logger.error(f"Error en autenticación OAuth: {e}", exc_info=True)
    
    audit_logger.log_login_failed(
        attempted_email=None,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        failure_reason='oauth_error',
        error_message=str(e)  # Incluye "mismatching_state: CSRF Warning..."
    )
```

### 2. Correlación de IP para Debug

```python
# src/audit_logger.py (recién agregado)
def _get_user_by_ip_correlation(self, ip_address: str):
    """Identifica usuario por IP en analytics"""
    # Si ves "mismatching_state", puedes buscar:
    # ¿Quién intentó desde esta IP? → Verónica Campos Facundo
```

---

## 🚀 Mejoras Recomendadas

### 1. Agregar ProxyFix para Render.com

```python
# app.py - Después de crear Flask app
from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app, 
    x_proto=1,  # Confiar en X-Forwarded-Proto
    x_host=1    # Confiar en X-Forwarded-Host
)
```

**Beneficio:** Render.com puede enviar headers correctos para HTTPS

---

### 2. Mensaje de Error Más Claro

```python
# app.py línea 881-893 - MEJORAR
except Exception as e:
    error_msg = str(e)
    
    # Detectar error CSRF específico
    if 'mismatching_state' in error_msg.lower() or 'csrf' in error_msg.lower():
        flash('Sesión expirada o cookies bloqueadas. Por favor:\n'
              '1. Cierre todas las pestañas del dashboard\n'
              '2. Limpie el cache del navegador\n'
              '3. Asegúrese de permitir cookies de terceros\n'
              '4. Intente nuevamente', 'warning')
    else:
        flash('Error en la autenticación. Por favor, intente nuevamente.', 'danger')
```

---

### 3. Retry Automático con State Fresh

```python
# app.py - NUEVA RUTA
@app.route('/oauth-retry')
def oauth_retry():
    """Reintentar OAuth con sesión limpia"""
    # Limpiar session state viejo
    session.pop('_state', None)
    
    # Redirigir a OAuth fresco
    return redirect(url_for('google_oauth'))
```

---

### 4. Health Check de Sesiones

```python
# app.py - NUEVA RUTA
@app.route('/check-session')
def check_session():
    """Endpoint para debug de sesiones"""
    if os.getenv('FLASK_ENV') != 'production':
        return jsonify({
            'cookies_enabled': request.cookies.get('session') is not None,
            'session_vars': list(session.keys()),
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        })
    return "Not available in production", 403
```

---

## 📚 Referencias

**Authlib Docs:**
- https://docs.authlib.org/en/latest/client/flask.html#flask-oauth2-client

**OAuth2 RFC6749:**
- https://tools.ietf.org/html/rfc6749#section-10.12 (CSRF Protection)

**Google OAuth2:**
- https://developers.google.com/identity/protocols/oauth2/web-server

---

## 🎯 Acción Inmediata para Usuario

Si un usuario reporta este error **AHORA**:

1. **Preguntarle:**
   - ¿Está usando modo incógnito?
   - ¿Tiene extensions de privacidad activas?
   - ¿Abrió múltiples tabs de login?

2. **Pedirle que pruebe:**
   ```
   a) Ctrl+Shift+Del → Limpiar cache y cookies
   b) Cerrar TODAS las pestañas del dashboard
   c) Abrir navegador normal (no incógnito)
   d) Ir a /login de nuevo
   e) Click "Iniciar con Google"
   f) Completar login SIN distraerse
   ```

3. **Si persiste:**
   - Buscar su IP en Audit Log (`/admin/audit-log`)
   - Verificar con correlación si es usuario conocido
   - Revisar logs de Render.com para ese timestamp exacto

---

**FIN DEL DOCUMENTO**
