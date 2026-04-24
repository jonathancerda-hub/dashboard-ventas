"""
generar_informe_usuarios_inactivos.py

Genera un informe de usuarios habilitados que NO han ingresado al sistema.
Útil para identificar cuentas sin uso y seguimiento de adopción.

Autor: Jonathan Cerda
Fecha: Abril 2026
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from src.permissions_manager import PermissionsManager
from src.supabase_manager import SupabaseManager
from src.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


def generar_informe_usuarios_sin_ingreso():
    """
    Genera informe de usuarios habilitados que nunca han ingresado.
    
    Returns:
        Dict con estadísticas y lista de usuarios sin ingreso
    """
    try:
        # Inicializar managers
        perm_manager = PermissionsManager()
        supabase = SupabaseManager()
        
        print("\n" + "="*70)
        print("📊 INFORME DE USUARIOS HABILITADOS SIN INGRESO AL SISTEMA")
        print("="*70 + "\n")
        
        # 1. Obtener usuarios habilitados
        print("🔍 Paso 1: Obteniendo usuarios habilitados...")
        usuarios_habilitados = perm_manager.get_all_users(include_inactive=False)
        
        if not usuarios_habilitados:
            print("⚠️  No hay usuarios habilitados en el sistema.")
            return {
                'total_habilitados': 0,
                'total_con_ingreso': 0,
                'total_sin_ingreso': 0,
                'usuarios_sin_ingreso': []
            }
        
        print(f"✅ {len(usuarios_habilitados)} usuarios habilitados encontrados\n")
        
        # 2. Obtener usuarios que han ingresado (desde page_visits)
        print("🔍 Paso 2: Consultando visitas registradas...")
        
        response = supabase.supabase.table('page_visits_ventas_locales')\
            .select('user_email')\
            .execute()
        
        # Obtener emails únicos que han visitado
        usuarios_con_visitas = set()
        if response.data:
            usuarios_con_visitas = {row['user_email'] for row in response.data if row.get('user_email')}
        
        print(f"✅ {len(usuarios_con_visitas)} usuarios únicos con visitas registradas\n")
        
        # 3. Cruzar datos: buscar quiénes NO han ingresado
        print("🔍 Paso 3: Identificando usuarios sin ingreso...\n")
        
        usuarios_sin_ingreso = []
        usuarios_con_ingreso = []
        
        for user in usuarios_habilitados:
            email = user['user_email']
            
            # Verificar si tiene visitas
            if email in usuarios_con_visitas:
                usuarios_con_ingreso.append(user)
            else:
                # Usuario habilitado pero sin ingreso
                usuarios_sin_ingreso.append(user)
        
        # 4. Mostrar resultados
        print("="*70)
        print("📈 ESTADÍSTICAS")
        print("="*70)
        print(f"Total usuarios habilitados:     {len(usuarios_habilitados)}")
        print(f"Usuarios con al menos 1 ingreso: {len(usuarios_con_ingreso)} ({len(usuarios_con_ingreso)/len(usuarios_habilitados)*100:.1f}%)")
        print(f"Usuarios SIN ningún ingreso:     {len(usuarios_sin_ingreso)} ({len(usuarios_sin_ingreso)/len(usuarios_habilitados)*100:.1f}%)")
        print("="*70 + "\n")
        
        # 5. Detallar usuarios sin ingreso
        if usuarios_sin_ingreso:
            print("🚫 USUARIOS HABILITADOS QUE NO HAN INGRESADO:")
            print("-"*70)
            print(f"{'Email':<40} {'Rol':<25} {'Creado':<15}")
            print("-"*70)
            
            for user in sorted(usuarios_sin_ingreso, key=lambda x: x['created_at'], reverse=True):
                email = user['user_email']
                rol = user['role_display_name']
                fecha_creacion = user['created_at_formatted']
                
                print(f"{email:<40} {rol:<25} {fecha_creacion:<15}")
            
            print("-"*70 + "\n")
        else:
            print("✅ ¡Excelente! Todos los usuarios habilitados han ingresado al menos una vez.\n")
        
        # 6. Sugerencias
        if usuarios_sin_ingreso:
            print("💡 RECOMENDACIONES:")
            print("-"*70)
            print("1. Enviar correo de bienvenida con instrucciones de acceso")
            print("2. Verificar que los usuarios recibieron el email de invitación")
            print("3. Revisar si tienen problemas de autenticación OAuth")
            print("4. Considerar desactivar cuentas sin uso después de 30 días")
            print("5. Programar capacitación para nuevos usuarios")
            print("-"*70 + "\n")
        
        # Retornar datos para uso programático
        return {
            'total_habilitados': len(usuarios_habilitados),
            'total_con_ingreso': len(usuarios_con_ingreso),
            'total_sin_ingreso': len(usuarios_sin_ingreso),
            'porcentaje_uso': len(usuarios_con_ingreso)/len(usuarios_habilitados)*100 if usuarios_habilitados else 0,
            'usuarios_sin_ingreso': usuarios_sin_ingreso,
            'usuarios_con_ingreso': usuarios_con_ingreso,
            'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        logger.error(f"Error generando informe: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        return None


def exportar_informe_csv(resultados: dict, archivo: str = "informe_usuarios_sin_ingreso.csv"):
    """
    Exporta el informe a CSV.
    
    Args:
        resultados: Diccionario con resultados del informe
        archivo: Nombre del archivo CSV
    """
    import csv
    
    try:
        usuarios = resultados['usuarios_sin_ingreso']
        
        if not usuarios:
            print("⚠️  No hay usuarios sin ingreso para exportar.")
            return
        
        with open(archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Encabezados
            writer.writerow([
                'Email',
                'Rol',
                'Rol Display',
                'Fecha Creación',
                'Fecha Actualización'
            ])
            
            # Datos
            for user in usuarios:
                writer.writerow([
                    user['user_email'],
                    user['role'],
                    user['role_display_name'],
                    user['created_at'],
                    user['updated_at']
                ])
        
        print(f"✅ Informe exportado a: {archivo}\n")
        
    except Exception as e:
        logger.error(f"Error exportando CSV: {e}", exc_info=True)
        print(f"❌ Error exportando CSV: {e}\n")


if __name__ == "__main__":
    print("\n🚀 Iniciando generación de informe...\n")
    
    # Generar informe
    resultados = generar_informe_usuarios_sin_ingreso()
    
    # Preguntar si exportar a CSV
    if resultados and resultados['total_sin_ingreso'] > 0:
        respuesta = input("¿Deseas exportar el informe a CSV? (s/n): ").strip().lower()
        if respuesta == 's':
            exportar_informe_csv(resultados)
    
    print("✅ Proceso completado.\n")
