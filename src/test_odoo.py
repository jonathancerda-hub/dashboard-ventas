import os

# Parsear manualmente el .env
env_vars = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
            os.environ[key.strip()] = value.strip()

print("Variables parseadas manualmente:")
print(f"ODOO_URL: [{env_vars.get('ODOO_URL')}]")
print(f"ODOO_DB: [{env_vars.get('ODOO_DB')}]")
print(f"ODOO_USER: [{env_vars.get('ODOO_USER')}]")
print(f"ODOO_PASSWORD: [{env_vars.get('ODOO_PASSWORD')}]")

# Intentar inicializar OdooManager
print("\n--- Intentando conectar a Odoo ---")
try:
    from odoo_manager import OdooManager
    odoo = OdooManager()
    print("✅ Conexión exitosa a Odoo!")
    print(f"URL: {odoo.url}")
    print(f"DB: {odoo.db}")
except Exception as e:
    print(f"❌ Error: {e}")
