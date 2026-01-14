"""
EJECUTAR ESTE SCRIPT EN EL OTRO PROYECTO
Copiar este archivo al otro proyecto y ejecutar para diagnosticar
"""
from dotenv import load_dotenv
load_dotenv()  # Cargar variables de entorno del .env

from odoo_manager import OdooManager
import calendar

print("="*80)
print("DIAGNÓSTICO - OTRO PROYECTO (Ventas Nacionales)")
print("="*80)

om = OdooManager()

print("\n📋 CONFIGURACIÓN:")
print(f"   URL: {om.url}")
print(f"   Database: {om.db}")
print(f"   Usuario: {om.username}")

print("\n📋 VERIFICAR FILTROS en get_sales_lines():")
print("   Por favor revisar el código de odoo_manager.py y listar:")
print("   1. ¿Qué valores de move_type se incluyen?")
print("   2. ¿Qué canal se filtra?")
print("   3. ¿Qué categorías se excluyen?")
print("   4. ¿Hay filtro de línea comercial?")

print("\n" + "="*80)
print("ANÁLISIS MES POR MES - AÑO 2025")
print("="*80)

meses_nombres = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

print(f"{'Mes':<12} | {'#Regs':>7} | {'abs(balance)':>15} | {'-balance':>15} | {'price_subtotal':>15} | {'price_total':>15}")
print("-"*110)

totales = {
    'registros': 0,
    'abs_balance': 0,
    'neg_balance': 0,
    'subtotal': 0,
    'total': 0
}

for mes in range(1, 13):
    fecha_inicio = f"2025-{mes:02d}-01"
    ultimo_dia = calendar.monthrange(2025, mes)[1]
    fecha_fin = f"2025-{mes:02d}-{ultimo_dia}"
    
    print(f"🔍 Consultando {meses_nombres[mes]}...", end=" ", flush=True)
    
    sales = om.get_sales_lines(date_from=fecha_inicio, date_to=fecha_fin, limit=10000)
    
    num_registros = len(sales)
    balance_abs = sum(abs(float(s.get('balance', 0))) for s in sales)
    balance_neg = sum(-float(s.get('balance', 0)) for s in sales)
    price_subtotal = sum(float(s.get('price_subtotal', 0)) for s in sales)
    price_total = sum(float(s.get('price_total', 0)) for s in sales)
    
    totales['registros'] += num_registros
    totales['abs_balance'] += balance_abs
    totales['neg_balance'] += balance_neg
    totales['subtotal'] += price_subtotal
    totales['total'] += price_total
    
    print(f"\r{meses_nombres[mes]:<12} | {num_registros:>7} | S/ {balance_abs:>12,.0f} | S/ {balance_neg:>12,.0f} | S/ {price_subtotal:>12,.0f} | S/ {price_total:>12,.0f}")

print("-"*110)
print(f"{'TOTAL':<12} | {totales['registros']:>7} | S/ {totales['abs_balance']:>12,.0f} | S/ {totales['neg_balance']:>12,.0f} | S/ {totales['subtotal']:>12,.0f} | S/ {totales['total']:>12,.0f}")
print("="*110)

print("\n📌 COMPARAR CON VALORES ESPERADOS:")
esperados = [0, 1723599, 4355482, 5204492, 4299838, 5561739, 3348956, 
             3459387, 4027793, 4709979, 4151104, 5999186, 7880135]
total_esperado = sum(esperados)

print(f"\n{'Mes':<12} | {'Esperado':>15} | {'¿Cuál método?':>15} | {'Diferencia':>15}")
print("-"*70)

# Necesitamos identificar qué método se usa
# Comparar cada mes para ver cuál método coincide mejor

for mes in range(1, 13):
    fecha_inicio = f"2025-{mes:02d}-01"
    ultimo_dia = calendar.monthrange(2025, mes)[1]
    fecha_fin = f"2025-{mes:02d}-{ultimo_dia}"
    
    sales = om.get_sales_lines(date_from=fecha_inicio, date_to=fecha_fin, limit=10000)
    
    esperado = esperados[mes]
    balance_abs = sum(abs(float(s.get('balance', 0))) for s in sales)
    balance_neg = sum(-float(s.get('balance', 0)) for s in sales)
    price_subtotal = sum(float(s.get('price_subtotal', 0)) for s in sales)
    
    # Determinar cuál está más cerca
    dif_abs = abs(balance_abs - esperado)
    dif_neg = abs(balance_neg - esperado)
    dif_sub = abs(price_subtotal - esperado)
    
    min_dif = min(dif_abs, dif_neg, dif_sub)
    
    if min_dif == dif_abs:
        metodo = "abs(balance)"
        valor = balance_abs
    elif min_dif == dif_neg:
        metodo = "-balance"
        valor = balance_neg
    else:
        metodo = "price_subtotal"
        valor = price_subtotal
    
    diferencia = valor - esperado
    
    print(f"{meses_nombres[mes]:<12} | S/ {esperado:>12,.0f} | {metodo:>15} | {diferencia:>+14,.0f}")

print("\n" + "="*80)
print("PREGUNTAS CLAVE:")
print("="*80)
print("1. ¿Qué campo usa el método get_sales_lines() para calcular ventas?")
print("   - balance")
print("   - price_subtotal")
print("   - price_total")
print("   - Otro: _______")
print("\n2. ¿Usa abs() o multiplicación por -1 en ese campo?")
print("\n3. ¿Los filtros de dominio incluyen estos?")
print("   - Canal: NACIONAL")
print("   - Categorías excluidas: [315, 333, 304, 314, 318, 339]")
print("   - Línea comercial: NO 'VENTA INTERNACIONAL'")
print("   - move_type: ['out_invoice', 'out_refund']")
print("   - state: 'posted'")
print("\n4. ¿Usa algún filtro adicional que este proyecto no tenga?")
