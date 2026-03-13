import os
import sys
import requests
from pathlib import Path

# Cargar .env desde el directorio raíz del proyecto
root_dir = Path(__file__).parent.parent
env_path = root_dir / '.env'

print("=== Test de Conexión Odoo JSON-RPC ===\n")
print(f"📁 Buscando .env en: {env_path}")
print(f"📁 ¿Existe el archivo?: {env_path.exists()}")

# Leer manualmente el archivo .env para debug
if env_path.exists():
    print(f"\n📋 Contenido del .env (primeras 10 líneas):")
    with open(env_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 10:
                if 'PASSWORD' not in line.upper():
                    print(f"   {line.rstrip()}")
                else:
                    print(f"   {line.split('=')[0]}=***")

# Ahora cargar con dotenv
from dotenv import load_dotenv, dotenv_values
load_status = load_dotenv(dotenv_path=env_path, override=True)  # Forzar sobreescritura
print(f"\n🔧 load_dotenv() retornó: {load_status}")

# Debug adicional: leer directamente con dotenv_values
print(f"\n🔍 Debug con dotenv_values():")
env_vars = dotenv_values(env_path)
for key in ['ODOO_URL', 'ODOO_DB', 'ODOO_USER']:
    print(f"   {key}: {env_vars.get(key, 'NO ENCONTRADA')}")

# Cargar manualmente si es necesario
if not os.getenv('ODOO_URL') and env_vars.get('ODOO_URL'):
    print(f"\n⚠️ Warning: ODOO_URL no cargada, forzando manualmente...")
    os.environ['ODOO_URL'] = env_vars['ODOO_URL']

print(f"\n🔑 Variables de entorno cargadas:")
print(f"   ODOO_URL: {os.getenv('ODOO_URL', 'NO DEFINIDA')}")
print(f"   ODOO_DB: {os.getenv('ODOO_DB', 'NO DEFINIDA')}")
print(f"   ODOO_USER: {os.getenv('ODOO_USER', 'NO DEFINIDA')}")
print(f"   ODOO_PASSWORD: {'***' if os.getenv('ODOO_PASSWORD') else 'NO DEFINIDA'}\n")

# 1. Test de autenticación directa con JSON-RPC
print("1️⃣ Probando conexión directa JSON-RPC...")
try:
    url = f"{os.getenv('ODOO_URL')}/jsonrpc"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "authenticate",
            "args": [os.getenv('ODOO_DB'), os.getenv('ODOO_USER'), os.getenv('ODOO_PASSWORD'), {}]
        },
        "id": 1
    }
    
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
    result = response.json()
    
    if "result" in result and result["result"]:
        print(f"   ✅ Conexión exitosa! UID: {result['result']}")
        uid = result['result']
    else:
        print(f"   ❌ Error en autenticación: {result}")
        uid = None
except Exception as e:
    print(f"   ❌ Error de conexión: {e}")
    uid = None

# 2. Test del OdooManager
print("\n2️⃣ Probando OdooManager...")
try:
    from odoo_manager import OdooManager
    odoo = OdooManager()
    
    if odoo.uid:
        print(f"   ✅ OdooManager inicializado correctamente")
        print(f"   URL: {odoo.url}")
        print(f"   DB: {odoo.db}")
        print(f"   UID: {odoo.uid}")
    else:
        print(f"   ❌ OdooManager no pudo autenticar")
except Exception as e:
    print(f"   ❌ Error al inicializar OdooManager: {e}")

print("\n✨ Test completado")
