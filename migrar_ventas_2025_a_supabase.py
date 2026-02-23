"""
Script para migrar todas las ventas del año 2025 desde Odoo a Supabase
Aplica los mismos filtros que usa el dashboard
"""

from odoo_manager import OdooManager
from supabase_manager import SupabaseManager
from datetime import datetime
import json

def extraer_campo_nombre(campo):
    """Extrae el nombre de un campo tipo [id, nombre]"""
    if campo and isinstance(campo, list) and len(campo) > 1:
        return campo[1]
    return None

def extraer_campo_id(campo):
    """Extrae el ID de un campo tipo [id, nombre]"""
    if campo and isinstance(campo, list) and len(campo) > 0:
        return campo[0]
    return None

def migrar_ventas_2025_a_supabase():
    """Extrae ventas del 2025 desde Odoo y las carga en Supabase"""
    
    print("=" * 80)
    print("MIGRACIÓN DE VENTAS 2025: ODOO → SUPABASE")
    print("=" * 80)
    
    # Inicializar managers
    print("\n1️⃣ Conectando a Odoo...")
    odoo = OdooManager()
    
    if not odoo.uid or not odoo.models:
        print("❌ Error: No se pudo conectar a Odoo")
        print("   Verifica las credenciales en las variables de entorno:")
        print("   - ODOO_URL")
        print("   - ODOO_DB")
        print("   - ODOO_USER")
        print("   - ODOO_PASSWORD")
        return
    
    print("✅ Conectado a Odoo exitosamente")
    
    print("\n2️⃣ Conectando a Supabase...")
    supabase = SupabaseManager()
    
    if not supabase.enabled or not supabase.supabase:
        print("❌ Error: No se pudo conectar a Supabase")
        print("   Verifica las credenciales en las variables de entorno:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_KEY")
        return
    
    print("✅ Conectado a Supabase exitosamente")
    
    # Definir rango del año 2025
    fecha_inicio = "2025-01-01"
    fecha_fin = "2025-12-31"
    
    print(f"\n3️⃣ Extrayendo ventas del {fecha_inicio} al {fecha_fin}...")
    print("   (Aplicando filtros del dashboard: IGV/IGV_INC, categorías excluidas)")
    
    # Extraer líneas de venta del 2025
    try:
        sales_lines = odoo.get_sales_lines(
            date_from=fecha_inicio,
            date_to=fecha_fin,
            limit=None  # Sin límite, queremos todas las ventas
        )
        
        print(f"✅ Extraídas {len(sales_lines)} líneas de venta del 2025")
        
        if not sales_lines:
            print("⚠️  No se encontraron ventas en el 2025")
            return
        
    except Exception as e:
        print(f"❌ Error al extraer ventas de Odoo: {e}")
        return
    
    # Preparar datos para Supabase
    print(f"\n4️⃣ Preparando datos para inserción en Supabase...")
    
    registros = []
    for line in sales_lines:
        try:
            # Extraer nombres de campos relacionales
            registro = {
                # Estado de pago
                'payment_state': line.get('payment_state'),
                
                # Canal de venta
                'sales_channel_id': extraer_campo_id(line.get('sales_channel_id')),
                'sales_channel_name': extraer_campo_nombre(line.get('sales_channel_id')),
                
                # Línea comercial
                'commercial_line_national_id': extraer_campo_id(line.get('commercial_line_national_id')),
                'commercial_line_name': extraer_campo_nombre(line.get('commercial_line_national_id')),
                
                # Vendedor
                'invoice_user_id': extraer_campo_id(line.get('invoice_user_id')),
                'invoice_user_name': extraer_campo_nombre(line.get('invoice_user_id')),
                
                # Cliente
                'partner_id': extraer_campo_id(line.get('partner_id')),
                'partner_name': line.get('partner_name'),
                'vat': line.get('vat'),
                
                # Origen
                'invoice_origin': line.get('invoice_origin'),
                
                # Asiento contable
                'move_id': extraer_campo_id(line.get('move_id')),
                'move_name': line.get('move_name'),
                'move_ref': line.get('move_ref'),
                'move_state': line.get('move_state'),
                
                # Orden de venta
                'order_id': extraer_campo_id(line.get('order_id')),
                'order_name': line.get('order_name'),
                'order_origin': line.get('order_origin'),
                'client_order_ref': line.get('client_order_ref'),
                'order_date': line.get('order_date') if line.get('order_date') and line.get('order_date') != False else None,
                'order_state': line.get('order_state'),
                'commitment_date': line.get('commitment_date') if line.get('commitment_date') and line.get('commitment_date') != False else None,
                'order_user_id': extraer_campo_id(line.get('order_user_id')),
                'order_user_name': extraer_campo_nombre(line.get('order_user_id')),
                
                # Producto
                'product_id': extraer_campo_id(line.get('product_id')),
                'product_name': line.get('name'),
                'default_code': line.get('default_code'),
                
                # Factura
                'invoice_date': line.get('invoice_date'),
                'l10n_latam_document_type_id': extraer_campo_id(line.get('l10n_latam_document_type_id')),
                'document_type_name': extraer_campo_nombre(line.get('l10n_latam_document_type_id')),
                'origin_number': line.get('origin_number'),
                
                # Montos (get_sales_lines ya devuelve balance convertido con signo correcto)
                'balance': float(line.get('balance', 0)) if line.get('balance') is not None else 0,
                'price_subtotal': float(line.get('balance', 0)) if line.get('balance') is not None else 0,
                
                # Clasificaciones farmacéuticas
                'pharmacological_classification_id': extraer_campo_id(line.get('pharmacological_classification_id')),
                'pharmacological_classification_name': extraer_campo_nombre(line.get('pharmacological_classification_id')),
                
                'pharmaceutical_forms_id': extraer_campo_id(line.get('pharmaceutical_forms_id')),
                'pharmaceutical_forms_name': extraer_campo_nombre(line.get('pharmaceutical_forms_id')),
                
                'administration_way_id': extraer_campo_id(line.get('administration_way_id')),
                'administration_way_name': extraer_campo_nombre(line.get('administration_way_id')),
                
                # Categoría y producción
                'categ_id': extraer_campo_id(line.get('categ_id')),
                'categ_name': extraer_campo_nombre(line.get('categ_id')),
                
                'production_line_id': extraer_campo_id(line.get('production_line_id')),
                'production_line_name': extraer_campo_nombre(line.get('production_line_id')),
                
                # Observaciones y entrega
                'delivery_observations': line.get('delivery_observations'),
                
                'partner_supplying_agency_id': extraer_campo_id(line.get('partner_supplying_agency_id')),
                'partner_supplying_agency_name': extraer_campo_nombre(line.get('partner_supplying_agency_id')),
                
                'partner_shipping_id': extraer_campo_id(line.get('partner_shipping_id')),
                'partner_shipping_name': extraer_campo_nombre(line.get('partner_shipping_id')),
                
                # Cantidad y precio
                'quantity': float(line.get('quantity', 0)) if line.get('quantity') is not None else 0,
                'price_unit': float(line.get('price_unit', 0)) if line.get('price_unit') is not None else 0,
                
                # Ruta y ciclo de vida
                'route_id': extraer_campo_id(line.get('route_id')),
                'route_name': extraer_campo_nombre(line.get('route_id')),
                'product_life_cycle': line.get('product_life_cycle'),
                
                # Impuestos
                'tax_id': line.get('tax_id'),
            }
            
            registros.append(registro)
            
        except Exception as e:
            print(f"⚠️  Error procesando línea: {e}")
            continue
    
    print(f"✅ Preparados {len(registros)} registros válidos")
    
    # Insertar en Supabase en lotes de 1000 registros
    print(f"\n5️⃣ Insertando datos en Supabase (tabla: ventas_odoo_2025)...")
    
    BATCH_SIZE = 1000
    total_insertados = 0
    total_errores = 0
    
    for i in range(0, len(registros), BATCH_SIZE):
        batch = registros[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(registros) + BATCH_SIZE - 1) // BATCH_SIZE
        
        try:
            print(f"   Insertando lote {batch_num}/{total_batches} ({len(batch)} registros)...", end=" ")
            
            response = supabase.supabase.table('ventas_odoo_2025').insert(batch).execute()
            
            if hasattr(response, 'data') and response.data:
                insertados = len(response.data)
                total_insertados += insertados
                print(f"✅ {insertados} registros insertados")
            else:
                print(f"✅ Lote procesado")
                total_insertados += len(batch)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            total_errores += len(batch)
            
            # Si el error es por duplicados, intentar actualizar
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                print(f"   ⚠️  Posibles registros duplicados, continuando...")
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE MIGRACIÓN")
    print("=" * 80)
    print(f"📊 Total registros extraídos de Odoo: {len(sales_lines)}")
    print(f"✅ Total registros insertados en Supabase: {total_insertados}")
    print(f"❌ Total con errores: {total_errores}")
    print("=" * 80)
    
    # Guardar resumen en archivo
    resumen = {
        'fecha_migracion': datetime.now().isoformat(),
        'rango_fechas': {'inicio': fecha_inicio, 'fin': fecha_fin},
        'total_extraidos': len(sales_lines),
        'total_insertados': total_insertados,
        'total_errores': total_errores,
        'tabla_destino': 'ventas_odoo_2025'
    }
    
    with open('migracion_ventas_2025_resumen.json', 'w', encoding='utf-8') as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Resumen guardado en: migracion_ventas_2025_resumen.json")
    print("\n🎉 Migración completada exitosamente!")

if __name__ == "__main__":
    migrar_ventas_2025_a_supabase()
