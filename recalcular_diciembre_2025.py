"""
Script para recalcular ventas de diciembre 2025 con límite corregido
"""
from dotenv import load_dotenv
load_dotenv()

from odoo_manager import OdooManager
from datetime import datetime

print("="*80)
print("RECÁLCULO DICIEMBRE 2025 - CON LÍMITE CORREGIDO (10,000)")
print("="*80)

om = OdooManager()

# Diciembre 2025
print("\n🔍 Consultando diciembre 2025 con límite de 10,000...")
sales = om.get_sales_lines(date_from='2025-12-01', date_to='2025-12-31', limit=10000)

print(f"\n📊 Total de registros obtenidos: {len(sales)}")

# Calcular ventas por línea comercial
ventas_por_linea = {}
for sale in sales:
    balance = float(sale.get('balance', 0))
    
    # Obtener línea comercial
    linea_info = sale.get('commercial_line_national_id')
    if linea_info and isinstance(linea_info, list) and len(linea_info) > 1:
        linea_nombre = linea_info[1].upper()
        
        # Normalizar GENVET y MARCA BLANCA como TERCEROS
        if linea_nombre in ['GENVET', 'MARCA BLANCA']:
            linea_nombre = 'TERCEROS'
        
        # Excluir VENTA INTERNACIONAL
        if 'VENTA INTERNACIONAL' in linea_nombre:
            continue
        
        ventas_por_linea[linea_nombre] = ventas_por_linea.get(linea_nombre, 0) + abs(balance)

# Mostrar resultados
print("\n" + "="*80)
print("VENTAS POR LÍNEA COMERCIAL - DICIEMBRE 2025")
print("="*80)
print(f"{'Línea Comercial':<20} | {'Venta (S/)':<15}")
print("-"*80)

total = 0
for linea in sorted(ventas_por_linea.keys()):
    venta = ventas_por_linea[linea]
    total += venta
    print(f"{linea:<20} | S/ {venta:>12,.2f}")

print("-"*80)
print(f"{'TOTAL':<20} | S/ {total:>12,.2f}")
print("="*80)

# Comparar con valor anterior
valor_anterior = 7880135
diferencia = total - valor_anterior
print(f"\n📊 COMPARACIÓN:")
print(f"   Valor anterior (con límite 5,000): S/ {valor_anterior:,.0f}")
print(f"   Valor nuevo (con límite 10,000):   S/ {total:,.0f}")
print(f"   Diferencia:                         S/ {diferencia:+,.0f} ({diferencia/valor_anterior*100:+.2f}%)")

# Verificar AGROVET específicamente
agrovet_nuevo = ventas_por_linea.get('AGROVET', 0)
agrovet_anterior = 1986712
diferencia_agrovet = agrovet_nuevo - agrovet_anterior
print(f"\n🔍 VERIFICACIÓN AGROVET:")
print(f"   Valor anterior: S/ {agrovet_anterior:,.0f}")
print(f"   Valor nuevo:    S/ {agrovet_nuevo:,.0f}")
print(f"   Diferencia:     S/ {diferencia_agrovet:+,.0f} ({diferencia_agrovet/agrovet_anterior*100:+.2f}%)")
