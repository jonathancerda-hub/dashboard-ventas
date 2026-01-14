"""
EJECUTAR ESTE SCRIPT EN EL OTRO PROYECTO
Para identificar qué filtros tiene y por qué obtiene más registros
"""
from dotenv import load_dotenv
load_dotenv()  # Cargar variables de entorno del .env

import inspect
from odoo_manager import OdooManager

print("="*80)
print("DIAGNÓSTICO DE FILTROS - OTRO PROYECTO")
print("="*80)

om = OdooManager()

# 1. Obtener el código fuente de get_sales_lines
try:
    source = inspect.getsource(om.get_sales_lines)
    print("\n📄 CÓDIGO FUENTE DE get_sales_lines():")
    print("="*80)
    print(source[:2000])  # Primeros 2000 caracteres
    print("="*80)
except Exception as e:
    print(f"❌ No se pudo obtener el código: {e}")

# 2. Buscar líneas específicas relacionadas con filtros
print("\n🔍 BÚSQUEDA DE FILTROS ESPECÍFICOS:")
print("="*80)

lines = source.split('\n')
filtros_encontrados = {
    'categ_id': False,
    'VENTA INTERNACIONAL': False,
    'NACIONAL': False,
    'move_type': False,
    'posted': False
}

for i, line in enumerate(lines, 1):
    # Buscar filtro de categorías
    if 'categ_id' in line and 'not in' in line:
        print(f"✅ Línea {i}: {line.strip()}")
        filtros_encontrados['categ_id'] = True
    
    # Buscar filtro de VENTA INTERNACIONAL
    if 'VENTA INTERNACIONAL' in line.upper() or 'commercial_line_national_id' in line:
        print(f"✅ Línea {i}: {line.strip()}")
        filtros_encontrados['VENTA INTERNACIONAL'] = True
    
    # Buscar filtro de canal NACIONAL
    if 'NACIONAL' in line and 'sales_channel' in line:
        print(f"✅ Línea {i}: {line.strip()}")
        filtros_encontrados['NACIONAL'] = True
    
    # Buscar move_type
    if 'move_type' in line:
        print(f"✅ Línea {i}: {line.strip()}")
        filtros_encontrados['move_type'] = True
    
    # Buscar state posted
    if "'posted'" in line or '"posted"' in line:
        print(f"✅ Línea {i}: {line.strip()}")
        filtros_encontrados['posted'] = True

print("\n" + "="*80)
print("RESUMEN DE FILTROS ENCONTRADOS:")
print("="*80)

if not filtros_encontrados['categ_id']:
    print("❌ NO EXCLUYE categorías [315, 333, 304, 314, 318, 339]")
    print("   → Esta podría ser la diferencia principal (+5,160 registros)")
else:
    print("✅ SÍ excluye categorías específicas")

if not filtros_encontrados['VENTA INTERNACIONAL']:
    print("❌ NO filtra 'VENTA INTERNACIONAL'")
    print("   → Incluye ventas internacionales")
else:
    print("✅ SÍ filtra 'VENTA INTERNACIONAL'")

if not filtros_encontrados['NACIONAL']:
    print("❌ NO filtra por canal NACIONAL")
    print("   → Incluye todos los canales")
else:
    print("✅ SÍ filtra por canal NACIONAL")

if not filtros_encontrados['move_type']:
    print("❌ NO filtra move_type")
else:
    print("✅ SÍ filtra move_type")

if not filtros_encontrados['posted']:
    print("❌ NO filtra state = posted")
else:
    print("✅ SÍ filtra state = posted")

print("\n" + "="*80)
print("COMPARACIÓN CON EL PROYECTO PRINCIPAL:")
print("="*80)
print("Este proyecto (26,822 registros) tiene estos filtros:")
print("   1. ✅ move_type in ['out_invoice', 'out_refund']")
print("   2. ✅ state = 'posted'")
print("   3. ✅ sales_channel_id.name = 'NACIONAL'")
print("   4. ✅ categ_id not in [315, 333, 304, 314, 318, 339]")
print("   5. ✅ commercial_line_national_id.name not ilike 'VENTA INTERNACIONAL'")

print("\n" + "="*80)
print("CONCLUSIÓN:")
print("="*80)
if not filtros_encontrados['categ_id']:
    print("⚠️ EL OTRO PROYECTO NO EXCLUYE LAS CATEGORÍAS [315, 333, 304, 314, 318, 339]")
    print("   Por eso obtiene 5,160 registros más (19% adicional)")
    print("\n   Opciones:")
    print("   A) Modificar ESTE proyecto para NO excluir esas categorías")
    print("   B) Modificar el OTRO proyecto para excluir esas categorías")
    print("   C) Mantener ambos con diferentes reglas de negocio")
else:
    print("🤔 Ambos proyectos tienen los mismos filtros aparentemente.")
    print("   La diferencia podría estar en:")
    print("   - Valores diferentes en las listas de exclusión")
    print("   - Filtros adicionales no visibles en get_sales_lines()")
    print("   - Procesamiento posterior que elimina registros")
