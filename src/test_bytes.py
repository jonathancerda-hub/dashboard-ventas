import os

# Parsear con análisis de bytes
env_vars = {}
with open('.env', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if 'ODOO_URL' in key:
                print(f"\n--- Análisis de ODOO_URL ---")
                print(f"Key length: {len(key)}")
                print(f"Key repr: {repr(key)}")
                print(f"Key bytes: {key.encode('utf-8')}")
                print(f"Caracteres: {[ord(c) for c in key]}")
            
            env_vars[key] = value

print(f"\nClaves que contienen 'ODOO': {[k for k in env_vars.keys() if 'ODOO' in k]}")
