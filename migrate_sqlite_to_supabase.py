"""
Script de Migración: SQLite → Supabase
Dashboard Ventas - Sistema de Permisos

Este script migra usuarios existentes de permissions.db (SQLite)
a Supabase (PostgreSQL)
"""

import sqlite3
import os
from src.permissions_manager import PermissionsManager
from src.audit_logger import AuditLogger
from src.logging_config import get_logger

logger = get_logger(__name__)


def check_sqlite_exists() -> bool:
    """Verifica si existe la base de datos SQLite"""
    return os.path.exists('permissions.db')


def migrate_users():
    """
    Migra todos los usuarios de SQLite a Supabase.
    
    Proceso:
    1. Lee usuarios de permissions.db
    2. Crea cada usuario en Supabase
    3. Registra migración en audit log
    """
    if not check_sqlite_exists():
        print("❌ Error: No se encontró permissions.db")
        print("   Si no tienes usuarios en SQLite, puedes saltar este script.")
        return
    
    try:
        # Conectar a SQLite
        print("📂 Conectando a SQLite (permissions.db)...")
        conn = sqlite3.connect('permissions.db')
        cursor = conn.cursor()
        
        # Leer usuarios
        cursor.execute("SELECT user_email, role FROM user_permissions")
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            print("⚠️  No se encontraron usuarios en SQLite")
            return
        
        print(f"📊 Encontrados {len(users)} usuarios en SQLite\n")
        
        # Conectar a Supabase
        print("☁️  Conectando a Supabase...")
        pm = PermissionsManager()
        audit = AuditLogger()
        
        print("✅ Conexión exitosa a Supabase\n")
        print("🔄 Iniciando migración...\n")
        
        # Migrar cada usuario
        migrated = 0
        skipped = 0
        errors = 0
        
        for email, role in users:
            try:
                # Verificar si ya existe
                existing_role = pm.get_user_role(email)
                if existing_role:
                    print(f"⏭️  {email:40} | {role:20} | Ya existe - saltado")
                    skipped += 1
                    continue
                
                # Crear en Supabase
                success = pm.add_user(email, role, created_by='MIGRATION_SQLITE')
                
                if success:
                    print(f"✅ {email:40} | {role:20} | Migrado")
                    audit.log_user_created('MIGRATION_SQLITE', email, role)
                    migrated += 1
                else:
                    print(f"❌ {email:40} | {role:20} | Error al crear")
                    errors += 1
                    
            except Exception as e:
                print(f"❌ {email:40} | Error: {e}")
                logger.error(f"Error migrando {email}: {e}", exc_info=True)
                errors += 1
        
        # Resumen
        print("\n" + "="*80)
        print("📊 RESUMEN DE MIGRACIÓN")
        print("="*80)
        print(f"✅ Migrados exitosamente: {migrated}")
        print(f"⏭️  Saltados (ya existían): {skipped}")
        print(f"❌ Errores: {errors}")
        print(f"📝 Total procesados: {len(users)}")
        print("="*80)
        
        if migrated > 0:
            print("\n🎉 ¡Migración completada exitosamente!")
            print("   Puedes verificar los usuarios en Supabase Dashboard")
            print("   O ejecutar: python test_supabase_permissions.py")
        
        if errors > 0:
            print("\n⚠️  Algunos usuarios tuvieron errores")
            print("   Revisa los logs para más detalles")
        
    except sqlite3.Error as e:
        print(f"❌ Error de SQLite: {e}")
        logger.error(f"Error de SQLite: {e}", exc_info=True)
    except Exception as e:
        print(f"❌ Error durante migración: {e}")
        logger.error(f"Error durante migración: {e}", exc_info=True)


def verify_migration():
    """Verifica que la migración fue exitosa"""
    try:
        pm = PermissionsManager()
        
        # Contar usuarios en Supabase
        users = pm.get_all_users(include_inactive=True)
        print(f"\n✅ Total usuarios en Supabase: {len(users)}")
        
        # Mostrar distribución por rol
        print("\n📊 Distribución por rol:")
        roles = {}
        for user in users:
            role = user.get('role', 'unknown')
            roles[role] = roles.get(role, 0) + 1
        
        for role, count in sorted(roles.items()):
            print(f"   {role:20} : {count:3} usuarios")
        
        # Contar cambios en audit log
        audit = AuditLogger()
        stats = audit.get_statistics()
        print(f"\n📝 Total logs de auditoría: {stats.get('total_logs', 0)}")
        
    except Exception as e:
        print(f"❌ Error verificando migración: {e}")
        logger.error(f"Error verificando migración: {e}", exc_info=True)


def backup_sqlite():
    """Crea backup de la base SQLite antes de migrar"""
    if not check_sqlite_exists():
        return
    
    import shutil
    from datetime import datetime
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'permissions_backup_{timestamp}.db'
        
        shutil.copy2('permissions.db', backup_name)
        print(f"💾 Backup creado: {backup_name}\n")
    except Exception as e:
        print(f"⚠️  Error creando backup: {e}")


if __name__ == '__main__':
    print("="*80)
    print("🔄 MIGRACIÓN SQLITE → SUPABASE")
    print("Dashboard Ventas - Sistema de Permisos")
    print("="*80)
    print()
    
    # Crear backup primero
    backup_sqlite()
    
    # Ejecutar migración
    migrate_users()
    
    # Verificar resultados
    print("\n" + "="*80)
    print("🔍 VERIFICACIÓN")
    print("="*80)
    verify_migration()
    
    print("\n✅ Proceso completado")
