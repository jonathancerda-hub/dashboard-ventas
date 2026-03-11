#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para extraer metas de 2025 desde Supabase
"""

import os
import sys
from pathlib import Path

# Cargar .env
print("🔧 Cargando configuración...")
env_file = Path(__file__).parent / '.env'

with open(env_file, 'r', encoding='utf-8-sig') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip()
            os.environ[key] = val

from supabase_manager import SupabaseManager

def obtener_metas_2025():
    """Extrae todas las metas de 2025 desde Supabase"""
    print("📊 Conectando a Supabase...")
    
    try:
        supabase = SupabaseManager()
        
        if not supabase.enabled:
            print("❌ Supabase no disponible")
            return None
        
        # Obtener todas las metas
        print("📥 Extrayendo metas de 2025...")
        
        # Buscar en las tablas de metas
        metas_2025 = []
        
        # Verificar si hay tabla metas_ventas_2025 o buscar en 2026
        try:
            # Intentar obtener de metas_ventas_2025
            result = supabase.supabase.table('metas_ventas_2025')\
                .select('*')\
                .execute()
            metas_2025 = result.data
            print(f"✅ Obtenidas {len(metas_2025)} metas de 2025")
        except Exception as e:
            print(f"⚠️ No hay tabla metas_ventas_2025: {e}")
            
            # Intentar buscar registros de 2025 en tabla 2026
            try:
                result = supabase.supabase.table('metas_ventas_2026')\
                    .select('*')\
                    .like('mes', '2025-%')\
                    .execute()
                metas_2025 = result.data
                print(f"✅ Obtenidas {len(metas_2025)} metas de 2025 desde tabla 2026")
            except Exception as e2:
                print(f"⚠️ Tampoco se encontraron en tabla 2026: {e2}")
        
        # Procesar las metas por línea
        if metas_2025:
            metas_por_linea = {}
            
            for meta in metas_2025:
                linea = meta.get('linea_comercial', 'OTROS')
                # Manejar None values
                meta_total = meta.get('meta_total') or 0
                meta_ipn = meta.get('meta_ipn') or 0
                
                meta_total = float(meta_total)
                meta_ipn = float(meta_ipn)
                
                if linea not in metas_por_linea:
                    metas_por_linea[linea] = {'total': 0, 'ipn': 0}
                
                metas_por_linea[linea]['total'] += meta_total
                metas_por_linea[linea]['ipn'] += meta_ipn
            
            return metas_por_linea
        else:
            print("⚠️ No se encontraron metas de 2025 en Supabase")
            return {}
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Ejecutar
if __name__ == '__main__':
    print("="*70)
    print("📊 OBTENIENDO METAS DE 2025 DESDE SUPABASE")
    print("="*70)
    
    metas = obtener_metas_2025()
    
    if metas:
        print("\n" + "="*70)
        print("📋 METAS POR LÍNEA COMERCIAL (2025)")
        print("="*70)
        print(f"{'LÍNEA':<25} {'META TOTAL':>15} {'META IPN':>15}")
        print("-"*70)
        
        total_meta = 0
        total_ipn = 0
        
        for linea, valores in sorted(metas.items()):
            meta_total = valores['total']
            meta_ipn = valores['ipn']
            total_meta += meta_total
            total_ipn += meta_ipn
            
            print(f"{linea:<25} S/ {meta_total:>12,.2f} S/ {meta_ipn:>12,.2f}")
        
        print("-"*70)
        print(f"{'TOTAL':<25} S/ {total_meta:>12,.2f} S/ {total_ipn:>12,.2f}")
        print("="*70)
    else:
        print("\n❌ No se pudieron obtener metas")
        sys.exit(1)
