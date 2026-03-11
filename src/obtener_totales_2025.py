#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para extraer datos reales de ventas 2025 desde Odoo
Solo muestra: Total 2025 + Productos Nuevos 2025
"""

import os
import sys
from pathlib import Path

# Cargar .env manualmente
print("🔧 Cargando configuración...")
env_file = Path(__file__).parent / '.env'

# Usar 'utf-8-sig' para eliminar BOM si existe
with open(env_file, 'r', encoding='utf-8-sig') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            # IMPORTANTE: Limpiar espacios en la clave y valor
            key = key.strip()
            val = val.strip()
            os.environ[key] = val

# Mostrar lo que se cargó
print(f"✅ ODOO_URL: {os.getenv('ODOO_URL')}")
print(f"✅ ODOO_DB: {os.getenv('ODOO_DB')}")
print(f"✅ ODOO_USER: {os.getenv('ODOO_USER')[:20]}...")
print("")

# Importar después de cargar .env
from odoo_manager import OdooManager

def obtener_totales_2025():
    """
    Extrae del Odoo:
    - Total de ventas 2025
    - Total de productos nuevos 2025
    - Desglose por línea comercial
    """
    print("📊 Conectando a Odoo...")
    
    try:
        odoo = OdooManager()
        
        # Obtener todas las ventas de 2025
        print("📥 Extrayendo datos de 2025...")
        sales_2025 = odoo.get_sales_lines(
            date_from='2025-01-01',
            date_to='2025-12-31',
            limit=100000
        )
        
        print(f"   Líneas obtenidas: {len(sales_2025)}")
        
        # Calcular totales
        total_venta = 0
        total_productos_nuevos = 0
        
        # Por línea comercial
        ventas_por_linea = {}
        productos_nuevos_por_linea = {}
        
        for sale in sales_2025:
            balance = float(sale.get('balance', 0))
            total_venta += balance
            
            # Obtener línea comercial
            linea_info = sale.get('commercial_line_national_id')
            if linea_info and isinstance(linea_info, list) and len(linea_info) > 1:
                linea_nombre = linea_info[1].upper()
                
                # Excluir venta internacional
                if 'VENTA INTERNACIONAL' not in linea_nombre:
                    # Sumar a la línea
                    if linea_nombre not in ventas_por_linea:
                        ventas_por_linea[linea_nombre] = 0
                        productos_nuevos_por_linea[linea_nombre] = 0
                    
                    ventas_por_linea[linea_nombre] += balance
                    
                    # Si es producto nuevo
                    if sale.get('product_life_cycle') == 'nuevo':
                        productos_nuevos_por_linea[linea_nombre] += balance
            
            # Total de productos nuevos
            if sale.get('product_life_cycle') == 'nuevo':
                total_productos_nuevos += balance
        
        # Ordenar líneas por venta descendente
        lineas_ordenadas = sorted(
            ventas_por_linea.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'total_venta': total_venta,
            'productos_nuevos': total_productos_nuevos,
            'num_lineas': len(sales_2025),
            'por_linea': [
                {
                    'nombre': linea,
                    'venta': venta,
                    'productos_nuevos': productos_nuevos_por_linea.get(linea, 0)
                }
                for linea, venta in lineas_ordenadas
            ]
        }
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Ejecutar
if __name__ == '__main__':
    datos = obtener_totales_2025()
    
    if datos:
        print("\n" + "="*70)
        print("📊 REPORTE ANUAL 2025 - TODO EL AÑO")
        print("="*70)
        print(f"💰 TOTAL VENDIDO:      S/ {datos['total_venta']:>18,.2f}")
        print(f"✨ PRODUCTOS NUEVOS:   S/ {datos['productos_nuevos']:>18,.2f}")
        pct_nuevo = (datos['productos_nuevos'] / datos['total_venta'] * 100) if datos['total_venta'] > 0 else 0
        print(f"📊 % Productos Nuevos:     {pct_nuevo:>18.1f}%")
        print(f"📈 Líneas procesadas:      {datos['num_lineas']:>18,}")
        print("="*70)
        
        print("\n📋 DESGLOSE POR LÍNEA COMERCIAL:")
        print("-"*70)
        print(f"{'LÍNEA':<25} {'VENTA TOTAL':>15} {'PROD. NUEVOS':>15} {'% NUEVOS':>10}")
        print("-"*70)
        
        for linea_data in datos['por_linea']:
            nombre = linea_data['nombre']
            venta = linea_data['venta']
            nuevos = linea_data['productos_nuevos']
            pct = (nuevos / venta * 100) if venta > 0 else 0
            
            print(f"{nombre:<25} S/ {venta:>12,.2f} S/ {nuevos:>12,.2f} {pct:>8.1f}%")
        
        print("="*70)
    else:
        print("\n❌ No se pudieron obtener los datos")
        sys.exit(1)
