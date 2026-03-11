from dotenv import load_dotenv
import os

# Limpiar cualquier variable previa
if 'ODOO_URL' in os.environ:
    del os.environ['ODOO_URL']

# Forzar recarga
load_dotenv(override=True)

print(f"ODOO_URL: [{os.getenv('ODOO_URL')}]")
print(f"ODOO_DB: [{os.getenv('ODOO_DB')}]")
print(f"ODOO_USER: [{os.getenv('ODOO_USER')}]")
print(f"ODOO_PASSWORD: [{os.getenv('ODOO_PASSWORD')}]")
print(f"GOOGLE_CLIENT_ID: [{os.getenv('GOOGLE_CLIENT_ID')}]")

# Verificar contenido del archivo directamente
print("\n--- Contenido directo del .env ---")
with open('.env', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if line.strip() and not line.startswith('#'):
            print(f"Línea {i}: {line.rstrip()}")
        if i >= 10:  # Primeras 10 líneas
            break

