import os

# Parsear manualmente el .env con debugging
env_vars = {}
with open('.env', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            env_vars[key] = value
            print(f"Línea {i}: Key=[{key}] Value=[{value[:30] if value else ''}...]")

print("\n--- Todas las claves en env_vars ---")
for key in env_vars.keys():
    print(f"  '{key}'")

print(f"\n¿'ODOO_URL' está en env_vars? {('ODOO_URL' in env_vars)}")
print(f"ODOO_URL value: [{env_vars.get('ODOO_URL')}]")
