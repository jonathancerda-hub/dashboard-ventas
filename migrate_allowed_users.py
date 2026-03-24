"""
migrate_allowed_users.py - Migra usuarios de allowed_users.json a Supabase

Este script toma todos los usuarios del archivo allowed_users.json y los agrega
a la tabla user_permissions en Supabase con el rol 'user_basic'.
"""

import json
from src.permissions_manager import PermissionsManager
from src.logging_config import get_logger

logger = get_logger(__name__)


def migrate_users_from_json():
    """Migra usuarios del JSON a Supabase"""
    print("\n" + "="*60)
    print("🚀 MIGRACIÓN DE USUARIOS A SUPABASE")
    print("="*60 + "\n")
    
    # Inicializar permissions manager
    try:
        pm = PermissionsManager()
        print("✅ Conexión a Supabase establecida\n")
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        return
    
    # Leer archivo allowed_users.json
    try:
        with open('allowed_users.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            emails = data.get('allowed_emails', [])
        
        print(f"📋 Usuarios encontrados en JSON: {len(emails)}\n")
    except FileNotFoundError:
        print("❌ Archivo allowed_users.json no encontrado")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error leyendo JSON: {e}")
        return
    
    # Estadísticas
    stats = {
        'agregados': 0,
        'existentes': 0,
        'errores': 0
    }
    
    # Procesar cada usuario
    print("📝 Procesando usuarios...")
    print("-" * 60)
    
    for email in emails:
        try:
            # Verificar si ya existe
            existing_role = pm.get_user_role(email)
            
            if existing_role:
                print(f"⚠️  Ya existe: {email} (rol: {existing_role})")
                stats['existentes'] += 1
            else:
                # Agregar nuevo usuario con rol básico
                success = pm.add_user(
                    user_email=email,
                    role='user_basic',
                    created_by='sistema_migracion'
                )
                
                if success:
                    print(f"✅ Agregado: {email}")
                    stats['agregados'] += 1
                else:
                    print(f"❌ Error agregando: {email}")
                    stats['errores'] += 1
        
        except Exception as e:
            print(f"❌ Error procesando {email}: {e}")
            stats['errores'] += 1
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("="*60)
    print(f"✅ Usuarios agregados:     {stats['agregados']}")
    print(f"⚠️  Ya existían:            {stats['existentes']}")
    print(f"❌ Errores:                {stats['errores']}")
    print(f"📋 Total procesados:       {len(emails)}")
    print("="*60 + "\n")
    
    # Verificar total en base de datos
    try:
        all_users = pm.get_all_users()
        print(f"🗄️  Total usuarios en Supabase: {len(all_users)}")
        
        # Contar por roles
        roles_count = {}
        for user in all_users:
            role = user.get('role', 'unknown')
            roles_count[role] = roles_count.get(role, 0) + 1
        
        print("\n📊 Distribución por roles:")
        for role, count in sorted(roles_count.items()):
            role_name = pm.ROLE_DISPLAY_NAMES.get(role, role)
            print(f"   {role_name}: {count}")
        
    except Exception as e:
        print(f"⚠️  No se pudo obtener el total: {e}")
    
    print("\n✅ Migración completada\n")


if __name__ == '__main__':
    migrate_users_from_json()
