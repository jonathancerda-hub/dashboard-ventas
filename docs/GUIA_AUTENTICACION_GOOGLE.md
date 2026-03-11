# Guía: Autenticación con Google OAuth2 en Flask (Authlib)

Esta guía resume la implementación usada en este proyecto para que la puedas replicar en otro.

## 1) Requisitos

- Python 3.10+
- Flask
- Authlib
- python-dotenv

Instalación mínima:

```bash
pip install Flask Authlib python-dotenv
```

## 2) Configurar OAuth en Google Cloud

1. Entra a [Google Cloud Console](https://console.cloud.google.com/).
2. Crea (o selecciona) un proyecto.
3. Configura la pantalla de consentimiento OAuth.
4. Crea credenciales de tipo **OAuth client ID** para **Web application**.
5. Agrega los URI autorizados:
   - **Authorized JavaScript origins** (ejemplo):
     - `http://localhost:5000`
   - **Authorized redirect URIs** (ejemplo):
     - `http://localhost:5000/authorize`
6. Guarda el `Client ID` y `Client Secret`.

## 3) Variables de entorno

Crea un archivo `.env` en tu proyecto:

```dotenv
SECRET_KEY=tu_clave_flask_larga_y_segura
GOOGLE_CLIENT_ID=tu_google_client_id
GOOGLE_CLIENT_SECRET=tu_google_client_secret
ALLOWED_USERS=usuario1@empresa.com,usuario2@empresa.com
```

> Recomendado: nunca subir `.env` al repositorio.

## 4) Configuración base en Flask

```python
import os
from flask import Flask, redirect, render_template, session, url_for, flash
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
```

## 5) Rutas de autenticación

### Login

```python
@app.route("/login")
def login():
    return render_template("login.html")
```

### Iniciar OAuth con Google

```python
@app.route("/google-oauth")
def google_oauth():
    redirect_uri = url_for("authorize", _external=True)
    return google.authorize_redirect(redirect_uri)
```

### Callback (`/authorize`)

```python
@app.route("/authorize")
def authorize():
    try:
        token = google.authorize_access_token()
        user_info = token.get("userinfo")

        if not user_info:
            flash("No se pudo obtener información del usuario.", "danger")
            return redirect(url_for("login"))

        email = user_info.get("email")
        name = user_info.get("name")

        allowed_raw = os.getenv("ALLOWED_USERS", "")
        allowed_emails = [e.strip() for e in allowed_raw.split(",") if e.strip()]

        if email and email in allowed_emails:
            session["username"] = email
            session["user_name"] = name
            session["user_info"] = user_info
            flash("¡Inicio de sesión exitoso!", "success")
            return redirect(url_for("dashboard"))

        flash(f"El correo {email} no tiene permiso para acceder.", "warning")
        return redirect(url_for("login"))

    except Exception as e:
        flash(f"Error en autenticación: {str(e)}", "danger")
        return redirect(url_for("login"))
```

### Logout

```python
@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("login"))
```

## 6) Proteger rutas privadas

```python
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")
```

## 7) Botón en plantilla HTML

```html
<a href="{{ url_for('google_oauth') }}">Sign in with Google</a>
```

## 8) Opción de whitelist con archivo JSON (fallback)

Si no quieres depender de `ALLOWED_USERS` en `.env`, puedes usar un JSON local.

Archivo `allowed_users.json`:

```json
{
  "allowed_emails": [
    "usuario1@empresa.com",
    "usuario2@empresa.com"
  ]
}
```

Y en tu callback, si `ALLOWED_USERS` está vacío, leer ese archivo.

## 9) Checklist de pruebas

1. Abre `/login`.
2. Click en **Sign in with Google**.
3. Valida que Google redirige a `/authorize` sin error.
4. Verifica que usuario permitido entra y crea sesión.
5. Verifica que usuario no permitido regresa a login con mensaje.
6. Prueba `/logout` y confirma sesión limpia.

## 10) Buenas prácticas de seguridad

- No hardcodear `GOOGLE_CLIENT_SECRET` en código.
- Usar `SECRET_KEY` robusta y única por entorno.
- Mantener `.env` fuera de Git.
- Restringir `ALLOWED_USERS` a correos corporativos.
- En producción, usar HTTPS y registrar URI de callback HTTPS.

---

## Referencia en este proyecto

Implementación actual en:

- `app.py`: configuración OAuth y rutas `/google-oauth`, `/authorize`, `/logout`.
- `templates/login.html`: botón para iniciar sesión con Google.
- `.env`: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `ALLOWED_USERS`, `SECRET_KEY`.
