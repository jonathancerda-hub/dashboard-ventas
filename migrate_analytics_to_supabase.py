"""
migrate_analytics_to_supabase.py - Migra datos históricos de Analytics a Supabase

Este script migra todos los registros de page_visits desde SQLite o PostgreSQL
a la tabla page_visits_ventas_locales en Supabase.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from src.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)

# Intentar importar psycopg2
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None


def get_old_analytics_connection():
    """
    Determina y retorna la conexión a la base de datos antigua de analytics.
    
    Returns:
        tuple: (connection, is_sqlite) o (None, None) si no hay datos
    """
    database_url = os.getenv('DATABASE_URL', '')
    sqlite_path = 'analytics.db'
    
    # Prioridad 1: PostgreSQL si DATABASE_URL existe y no está vacía
    if database_url and database_url.strip():
        if not PSYCOPG2_AVAILABLE:
            print("❌ DATABASE_URL configurada pero psycopg2 no está instalado")
            print("   Instala con: pip install psycopg2-binary")
            return None, None
        
        try:
            conn = psycopg2.connect(database_url)
            print(f"✅ Conectado a PostgreSQL (DATABASE_URL)")
            return conn, False
        except Exception as e:
            print(f"⚠️  Error conectando a PostgreSQL: {e}")
            print(f"   Intentando SQLite local...")
    
    # Prioridad 2: SQLite local si existe el archivo
    if Path(sqlite_path).exists():
        try:
            conn = sqlite3.connect(sqlite_path)
            conn.row_factory = sqlite3.Row
            print(f"✅ Conectado a SQLite local ({sqlite_path})")
            return conn, True
        except Exception as e:
            print(f"❌ Error conectando a SQLite: {e}")
            return None, None
    
    print(f"⚠️  No se encontró base de datos antigua:")
    print(f"   - DATABASE_URL vacía o no configurada")
    print(f"   - Archivo {sqlite_path} no existe")
    print(f"   No hay datos para migrar.")
    return None, None


def get_records_from_old_db(conn, is_sqlite):
    """
    Lee todos los registros de page_visits de la base antigua.
    
    Args:
        conn: Conexión a la base de datos
        is_sqlite: True si es SQLite, False si es PostgreSQL
    
    Returns:
        list: Lista de registros (dicts)
    """
    cursor = conn.cursor()
    
    if is_sqlite:
        cursor.execute("""
            SELECT 
                user_email,
                user_name,
                page_url,
                page_title,
                visit_timestamp,
                session_duration,
                ip_address,
                user_agent,
                referrer,
                method
            FROM page_visits
            ORDER BY visit_timestamp ASC
        """)
        rows = cursor.fetchall()
        # Convertir Row a dict
        return [dict(row) for row in rows]
    else:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                user_email,
                user_name,
                page_url,
                page_title,
                visit_timestamp,
                session_duration,
                ip_address,
                user_agent,
                referrer,
                method
            FROM page_visits
            ORDER BY visit_timestamp ASC
        """)
        return cursor.fetchall()


def migrate_analytics_to_supabase():
    """Ejecuta la migración completa de analytics a Supabase"""
    print("\n" + "="*70)
    print("🚀 MIGRACIÓN DE ANALYTICS A SUPABASE")
    print("="*70 + "\n")
    
    # 1. Conectar a Supabase
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Variables SUPABASE_URL y SUPABASE_KEY no configuradas en .env")
            return
        
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Conexión a Supabase establecida")
        print(f"   URL: {supabase_url}\n")
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        return
    
    # 2. Conectar a base de datos antigua
    old_conn, is_sqlite = get_old_analytics_connection()
    
    if not old_conn:
        print("\n⏭️  No hay datos para migrar. La tabla en Supabase está lista para uso.")
        return
    
    print()
    
    # 3. Leer registros antiguos
    try:
        print("📊 Leyendo registros de analytics antiguos...")
        records = get_records_from_old_db(old_conn, is_sqlite)
        print(f"   Registros encontrados: {len(records)}\n")
        
        if len(records) == 0:
            print("⏭️  No hay registros para migrar.")
            return
    except Exception as e:
        print(f"❌ Error leyendo registros: {e}")
        return
    finally:
        old_conn.close()
    
    # 4. Migrar registros a Supabase
    print("🔄 Migrando registros a Supabase...\n")
    
    stats = {
        'migrados': 0,
        'errores': 0,
        'total': len(records)
    }
    
    batch_size = 100  # Insertar en lotes de 100
    batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
    
    for batch_num, batch in enumerate(batches, 1):
        try:
            # Preparar datos para inserción
            data_to_insert = []
            for record in batch:
                # Convertir timestamp si es necesario
                visit_ts = record.get('visit_timestamp')
                if isinstance(visit_ts, datetime):
                    visit_ts = visit_ts.isoformat()
                elif isinstance(visit_ts, str):
                    # Ya es string, dejarlo como está
                    pass
                
                data_to_insert.append({
                    'user_email': record.get('user_email'),
                    'user_name': record.get('user_name'),
                    'page_url': record.get('page_url'),
                    'page_title': record.get('page_title'),
                    'visit_timestamp': visit_ts,
                    'session_duration': record.get('session_duration', 0),
                    'ip_address': record.get('ip_address'),
                    'user_agent': record.get('user_agent'),
                    'referrer': record.get('referrer'),
                    'method': record.get('method', 'GET')
                })
            
            # Insertar lote en Supabase
            response = supabase.table('page_visits_ventas_locales').insert(data_to_insert).execute()
            
            if response.data:
                stats['migrados'] += len(batch)
                print(f"   ✅ Lote {batch_num}/{len(batches)}: {len(batch)} registros migrados")
            else:
                stats['errores'] += len(batch)
                print(f"   ⚠️  Lote {batch_num}/{len(batches)}: Sin datos en respuesta")
                
        except Exception as e:
            stats['errores'] += len(batch)
            print(f"   ❌ Lote {batch_num}/{len(batches)}: Error - {e}")
    
    # 5. Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("="*70)
    print(f"Total registros:     {stats['total']}")
    print(f"✅ Migrados:         {stats['migrados']}")
    print(f"❌ Errores:          {stats['errores']}")
    print(f"📈 Tasa de éxito:    {(stats['migrados']/stats['total']*100):.1f}%")
    print("="*70 + "\n")
    
    if stats['migrados'] > 0:
        print("🎉 ¡Migración completada!")
        print(f"   Los datos históricos ahora están en page_visits_ventas_locales")
    
    if stats['errores'] > 0:
        print(f"⚠️  Hubo {stats['errores']} errores. Revisa los logs arriba.")


if __name__ == '__main__':
    try:
        migrate_analytics_to_supabase()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        logger.error(f"Error en migración de analytics: {e}", exc_info=True)
