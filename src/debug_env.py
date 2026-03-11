import os
from pathlib import Path

env_file = Path('c:/Users/jcerda/Desktop/Dashboard-Ventas-Backup/.env')

print('Leyendo línea por línea:')
with open(env_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'ODOO_URL' in line:
            print(f'Linea {i}: {repr(line)}')
            line_clean = line.strip()
            print(f'  After strip: {repr(line_clean)}')
            if '=' in line_clean:
                key, val = line_clean.split('=', 1)
                key = key.strip()
                val = val.strip()
                print(f'  Key: {repr(key)}')
                print(f'  Val: {repr(val)}')
                os.environ[key] = val

print(f'\nODOO_URL en environ: {repr(os.getenv("ODOO_URL"))}')
print(f'Todas las keys que contienen ODOO:')
for k in os.environ:
    if 'ODOO' in k:
        print(f'  {k} = {os.environ[k][:50]}')
