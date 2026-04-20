"""
permissions_manager.py - Sistema centralizado de permisos de usuario

Este módulo gestiona roles y permisos de usuarios del dashboard,
reemplazando las listas hardcodeadas en app.py
"""

import sqlite3
from contextlib import contextmanager
from src.logging_config import get_logger

logger = get_logger(__name__)


class PermissionsManager:
    """
    Gestor de permisos de usuario basado en roles.
    
    Roles disponibles:
    - admin_full: Acceso total (exports, analytics, metas)
    - admin_export: Puede exportar datos
    - analytics_viewer: Acceso a página de analytics
    - user_basic: Solo visualización de dashboards
    """
    
    # Definición de permisos por rol
    ROLE_PERMISSIONS = {
        'admin_full': ['view_dashboard', 'view_analytics', 'edit_targets', 'export_data'],
        'admin_export': ['view_dashboard', 'export_data'],
        'analytics_viewer': ['view_dashboard', 'view_analytics'],
        'user_basic': ['view_dashboard']
    }
    
    def __init__(self, db_path='permissions.db'):
        """Inicializa el gestor y crea tablas si no existen"""
        self.db_path = db_path
        self._init_database()
        logger.info(f"PermissionsManager inicializado con DB: {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la DB"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en conexión DB permisos: {e}", exc_info=True)
            raise
        finally:
            if conn:
                conn.close()
    
    def _init_database(self):
        """Crea las tablas de permisos si no existen"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Tabla de permisos de usuario
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_permissions (
                        user_email TEXT PRIMARY KEY,
                        role TEXT NOT NULL CHECK(role IN ('admin_full', 'admin_export', 'analytics_viewer', 'user_basic')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índice para búsquedas rápidas
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_email 
                    ON user_permissions(user_email)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_role
                    ON user_permissions(role)
                """)
                
                logger.info("Tablas de permisos inicializadas correctamente")
                
        except Exception as e:
            logger.error(f"Error al inicializar DB de permisos: {e}", exc_info=True)
    
    def add_user(self, user_email, role='user_basic'):
        """
        Agrega un usuario con un rol específico.
        
        Args:
            user_email: Email del usuario
            role: Rol a asignar (default: user_basic)
        
        Returns:
            bool: True si se agregó exitosamente
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_permissions (user_email, role, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (user_email.lower(), role))
                
                logger.info(f"Usuario agregado: {user_email} con rol {role}")
                return True
                
        except Exception as e:
            logger.error(f"Error al agregar usuario: {e}", exc_info=True)
            return False
    
    def get_user_role(self, user_email):
        """
        Obtiene el rol de un usuario.
        
        Args:
            user_email: Email del usuario
        
        Returns:
            str: Rol del usuario o 'user_basic' por defecto
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT role FROM user_permissions 
                    WHERE user_email = ?
                """, (user_email.lower(),))
                
                result = cursor.fetchone()
                if result:
                    return result['role']
                else:
                    logger.warning(f"Usuario {user_email} no encontrado en DB, usando rol por defecto")
                    return 'user_basic'
                    
        except Exception as e:
            logger.error(f"Error al obtener rol de usuario: {e}", exc_info=True)
            return 'user_basic'
    
    def has_permission(self, user_email, permission):
        """
        Verifica si un usuario tiene un permiso específico.
        
        Args:
            user_email: Email del usuario
            permission: Permiso a verificar (ej: 'export', 'analytics')
        
        Returns:
            bool: True si el usuario tiene el permiso
        
        Example:
            >>> permissions_manager.has_permission('user@example.com', 'export')
            True
        """
        role = self.get_user_role(user_email)
        permissions = self.ROLE_PERMISSIONS.get(role, [])
        return permission in permissions
    
    def is_admin(self, user_email):
        """
        Verifica si un usuario es administrador (admin_full o admin_export).
        
        Args:
            user_email: Email del usuario
        
        Returns:
            bool: True si es administrador
        """
        role = self.get_user_role(user_email)
        return role in ['admin_full', 'admin_export']
    
    def get_all_users(self):
        """
        Obtiene todos los usuarios con sus roles.
        
        Returns:
            list: Lista de dicts con user_email, role, created_at
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_email, role, created_at, updated_at
                    FROM user_permissions
                    ORDER BY role, user_email
                """)
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"Error al obtener usuarios: {e}", exc_info=True)
            return []
    
    def get_users_by_role(self, role):
        """
        Obtiene todos los usuarios con un rol específico.
        
        Args:
            role: Rol a filtrar
        
        Returns:
            list: Lista de emails
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_email FROM user_permissions 
                    WHERE role = ?
                    ORDER BY user_email
                """, (role,))
                
                results = cursor.fetchall()
                return [row['user_email'] for row in results]
                
        except Exception as e:
            logger.error(f"Error al obtener usuarios por rol: {e}", exc_info=True)
            return []
    
    def remove_user(self, user_email):
        """
        Elimina un usuario del sistema de permisos.
        
        Args:
            user_email: Email del usuario a eliminar
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM user_permissions WHERE user_email = ?
                """, (user_email.lower(),))
                
                if cursor.rowcount > 0:
                    logger.info(f"Usuario eliminado: {user_email}")
                    return True
                else:
                    logger.warning(f"Usuario no encontrado para eliminar: {user_email}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error al eliminar usuario: {e}", exc_info=True)
            return False
    
    def migrate_from_lists(self, admin_full_list, admin_export_list, analytics_list):
        """
        Migra usuarios desde listas hardcodeadas al sistema de permisos.
        
        Args:
            admin_full_list: Lista de emails con permisos completos
            admin_export_list: Lista de emails con permisos de exportación
            analytics_list: Lista de emails con acceso a analytics
        
        Returns:
            dict: Resumen de la migración
        """
        migrated = {'admin_full': 0, 'admin_export': 0, 'analytics_viewer': 0, 'errors': 0}
        
        try:
            # Migrar admin_full
            for email in admin_full_list:
                if self.add_user(email, 'admin_full'):
                    migrated['admin_full'] += 1
                else:
                    migrated['errors'] += 1
            
            # Migrar admin_export (solo si no están en admin_full)
            for email in admin_export_list:
                if email not in admin_full_list:
                    if self.add_user(email, 'admin_export'):
                        migrated['admin_export'] += 1
                    else:
                        migrated['errors'] += 1
            
            # Migrar analytics_viewer (solo si no son admins)
            for email in analytics_list:
                if email not in admin_full_list and email not in admin_export_list:
                    if self.add_user(email, 'analytics_viewer'):
                        migrated['analytics_viewer'] += 1
                    else:
                        migrated['errors'] += 1
            
            logger.info(f"Migración completada: {migrated}")
            return migrated
            
        except Exception as e:
            logger.error(f"Error en migración de permisos: {e}", exc_info=True)
            return migrated


# Script de migración (ejecutar una vez)
if __name__ == '__main__':
    print("=== Migración de Permisos ===\n")
    
    # Listas actuales del app.py (copiar aquí los valores actuales)
    ADMIN_FULL = [
        "jonathan.cerda@agrovetmarket.com",
        "janet.hueza@agrovetmarket.com",
        "juan.portal@agrovetmarket.com",
    ]
    
    ADMIN_EXPORT = [
        "miguel.hernandez@agrovetmarket.com",
        "juana.lovaton@agrovetmarket.com",
        "jimena.delrisco@agrovetmarket.com",
    ]
    
    ANALYTICS_VIEWERS = [
        "ena.fernandez@agrovetmarket.com",
    ]
    
    # Crear manager y migrar
    permissions_manager = PermissionsManager()
    result = permissions_manager.migrate_from_lists(ADMIN_FULL, ADMIN_EXPORT, ANALYTICS_VIEWERS)
    
    print(f"\n✅ Usuarios migrados:")
    print(f"   - admin_full: {result['admin_full']}")
    print(f"   - admin_export: {result['admin_export']}")
    print(f"   - analytics_viewer: {result['analytics_viewer']}")
    print(f"   - errores: {result['errors']}\n")
    
    # Mostrar todos los usuarios
    print("📋 Usuarios en el sistema:")
    for user in permissions_manager.get_all_users():
        print(f"   {user['user_email']}: {user['role']}")
