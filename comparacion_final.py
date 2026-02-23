# -*- coding: utf-8 -*-
"""
Comparación final corregida con paginación
"""
from odoo_manager import OdooManager
from supabase_manager import SupabaseManager
import calendar

def main():
    print("=" * 80)
    print("COMPARACIÓN FINAL: ODOO vs SUPABASE 2025")
    print("=" * 80)
    
    odoo = OdooManager()
    supabase = SupabaseManager()
    
    if not odoo.uid or not supabase.enabled:
        print("Error de conexión")
        return
    
    print("\nConsultando mes por mes...\n")
    
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    print(f"{'MES':<15} {'ODOO REGISTROS':>15} {'ODOO MONTO':>20} {'SUPABASE REG':>15} {'SUPABASE MONTO':>20} {'MATCH':>8}")
    print("=" * 110)
    
    total_odoo_reg = 0
    total_odoo_monto = 0.0
    total_sb_reg = 0
    total_sb_monto = 0.0
    
    for mes_num in range(1, 13):
        mes = meses[mes_num - 1]
        fecha_inicio = f"2025-{mes_num:02d}-01"
        ultimo_dia = calendar.monthrange(2025, mes_num)[1]
        fecha_fin = f"2025-{mes_num:02d}-{ultimo_dia:02d}"
        
        # Odoo
        lines_odoo = odoo.get_sales_lines(date_from=fecha_inicio, date_to=fecha_fin, limit=None)
        reg_odoo = len(lines_odoo)
        monto_odoo = sum(line.get('balance', 0) for line in lines_odoo)
        
        # Supabase (con paginación)
        sb_records = []
        offset = 0
        batch_size = 1000
        
        while True:
            result = supabase.supabase.table('ventas_odoo_2025')\
                .select('balance')\
                .gte('invoice_date', fecha_inicio)\
                .lte('invoice_date', fecha_fin)\
                .range(offset, offset + batch_size - 1)\
                .execute()
            
            if not result.data:
                break
            
            sb_records.extend(result.data)
            offset += batch_size
            
            if len(result.data) < batch_size:
                break
        
        reg_sb = len(sb_records)
        monto_sb = sum(float(row['balance'] or 0) for row in sb_records)
        
        # Acumular
        total_odoo_reg += reg_odoo
        total_odoo_monto += monto_odoo
        total_sb_reg += reg_sb
        total_sb_monto += monto_sb
        
        # Match
        match = "✅" if reg_odoo == reg_sb and abs(monto_odoo - monto_sb) < 1 else "⚠️"
        
        print(f"{mes:<15} {reg_odoo:>15,} {monto_odoo:>19,.2f} {reg_sb:>15,} {monto_sb:>19,.2f} {match:>8}")
    
    print("=" * 110)
    print(f"{'TOTAL':<15} {total_odoo_reg:>15,} {total_odoo_monto:>19,.2f} {total_sb_reg:>15,} {total_sb_monto:>19,.2f}")
    print("=" * 110)
    
    if total_odoo_reg == total_sb_reg and abs(total_odoo_monto - total_sb_monto) < 1:
        print("\n✅ MIGRACIÓN EXITOSA: Todos los datos coinciden perfectamente")
    else:
        print(f"\n⚠️ Diferencias detectadas:")
        print(f"   Registros: {total_sb_reg - total_odoo_reg:+,}")
        print(f"   Monto: S/ {total_sb_monto - total_odoo_monto:+,.2f}")

if __name__ == "__main__":
    main()
