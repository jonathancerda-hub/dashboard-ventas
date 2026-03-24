"""
permissions_manager.py - Sistema centralizado de permisos de usuario (SUPABASE VERSION)

Este módulo gestiona roles y permisos de usuarios del dashboard usando Supabase,
compatible con producción en Render.com
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from src.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


class PermissionsManager:
    """
    Gestor de permisos de usuario basado en roles usando Supabase.
    
    Roles disponibles:
    - admin_full: Acceso total (exports, analytics, metas, gestión de usuarios)
    - admin_export: Puede exportar datos
    - analytics_viewer: Acceso a página de analytics
    - user_basic: Solo visualización de dashboards
    """
    
    # Definición de permisos por rol
    ROLE_PERMISSIONS = {
        'admin_full': ['view_dashboard', 'view_analytics', 'edit_targets', 'export_data', 'manage_users'],
        'admin_export': ['view_dashboard', 'view_analytics', 'export_data'],
        'analytics_viewer': ['view_dashboard', 'view_analytics'],
        'user_basic': ['view_dashboard']
    }
    
    # Nombres de display para UI
    ROLE_DISPLAY_NAMES = {
        'admin_full': 'Administrador Total',
        'admin_export': 'Administrador con Exportación',
        'analytics_viewer': 'Visualizador de Analytics',
        'user_basic': 'Usuario Básico'
    }
    
    def __init__(self):
        """Inicializa el gestor y conecta con Supabase"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            logger.error("❌ Credenciales de Supabase no configuradas en .env")
            raise ValueError("SUPABASE_URL y SUPABASE_KEY son requeridas")
        
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.enabled = True
            logger.info("✅ PermissionsManager inicializado con Supabase")
        except Exception as e:
            logger.error(f"❌ Error al conectar con Supabase: {e}", exc_info=True)
            raise
    
    def has_permission(self, user_email: str, permission: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico.
        
        Args:
            user_email: Email del usuario
            permission: Permiso a verificar (ej: 'view_analytics')
        
        Returns:
            bool: True si el usuario tiene el permiso
        """
        try:
            role = self.get_user_role(user_email)
            if not role:
                logger.warning(f"Usuario sin rol: {user_email}")
                return False
            
            permissions = self.ROLE_PERMISSIONS.get(role, [])
            has_perm = permission in permissions
            
            logger.debug(f"Permiso '{permission}' para {user_email} ({role}): {has_perm}")
            return has_perm
        except Exception as e:
            logger.error(f"Error verificando permiso: {e}", exc_info=True)
            return False
    
    def is_admin(self, user_email: str) -> bool:
        """
        Verifica si un usuario tiene rol de administrador total.
        
        Args:
            user_email: Email del usuario
        
        Returns:
            bool: True si es admin_full
        """
        try:
            role = self.get_user_role(user_email)
            is_adm = role == 'admin_full'
            logger.debug(f"¿{user_email} es admin?: {is_adm}")
            return is_adm
        except Exception as e:
            logger.error(f"Error verificando admin: {e}", exc_info=True)
            return False
    
    def get_user_role(self, user_email: str) -> Optional[str]:
        """
        Obtiene el rol de un usuario.
        
        Args:
            user_email: Email del usuario
        
        Returns:
            str: Nombre del rol o None si no existe
        """
        try:
            response = self.supabase.table('user_permissions')\
                .select('role, is_active')\
                .eq('user_email', user_email.lower())\
                .eq('is_active', True)\
                .single()\
                .execute()
            
            if response.data:
                role = response.data['role']
                logger.debug(f"Rol de {user_email}: {role}")
                return role
            
            logger.debug(f"Usuario no encontrado: {user_email}")
            return None
        except Exception as e:
            logger.error(f"Error obteniendo rol de {user_email}: {e}", exc_info=True)
            return None
    
    def add_user(self, user_email: str, role: str = 'user_basic', created_by: str = 'SYSTEM') -> bool:
        """
        Agrega un usuario con un rol específico.
        
        Args:
            user_email: Email del usuario
            role: Rol a asignar (default: user_basic)
            created_by: Email del admin que crea el usuario
        
        Returns:
            bool: True si se agregó exitosamente
        """
        if role not in self.ROLE_PERMISSIONS:
            logger.error(f"Rol inválido: {role}")
            return False
        
        try:
            data = {
                'user_email': user_email.lower(),
                'role': role,
                'created_by': created_by,
                'is_active': True
            }
            
            response = self.supabase.table('user_permissions')\
                .insert(data)\
                .execute()
            
            if response.data:
                logger.info(f"✅ Usuario agregado: {user_email} con rol {role}")
                return True
            
            logger.error(f"No se pudo agregar usuario: {user_email}")
            return False
        except Exception as e:
            logger.error(f"Error agregando usuario {user_email}: {e}", exc_info=True)
            return False
    
    def update_user_role(self, user_email: str, new_role: str) -> bool:
        """
        Actualiza el rol de un usuario existente.
        
        Args:
            user_email: Email del usuario
            new_role: Nuevo rol a asignar
        
        Returns:
            bool: True si se actualizó correctamente
        """
        if new_role not in self.ROLE_PERMISSIONS:
            logger.error(f"Rol inválido: {new_role}")
            return False
        
        try:
            response = self.supabase.table('user_permissions')\
                .update({'role': new_role})\
                .eq('user_email', user_email.lower())\
                .execute()
            
            if response.data:
                logger.info(f"✅ Rol actualizado: {user_email} → {new_role}")
                return True
            
            logger.warning(f"Usuario no encontrado para actualizar: {user_email}")
            return False
        except Exception as e:
            logger.error(f"Error actualizando rol de {user_email}: {e}", exc_info=True)
            return False
    
    def delete_user(self, user_email: str, soft_delete: bool = True) -> bool:
        """
        Elimina un usuario del sistema (soft o hard delete).
        
        Args:
            user_email: Email del usuario a eliminar
            soft_delete: Si True, solo marca como inactivo. Si False, elimina físicamente.
        
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            if soft_delete:
                # Soft delete: marcar como inactivo
                response = self.supabase.table('user_permissions')\
                    .update({'is_active': False})\
                    .eq('user_email', user_email.lower())\
                    .execute()
            else:
                # Hard delete: eliminar físicamente
                response = self.supabase.table('user_permissions')\
                    .delete()\
                    .eq('user_email', user_email.lower())\
                    .execute()
            
            if response.data:
                delete_type = "desactivado" if soft_delete else "eliminado"
                logger.info(f"✅ Usuario {delete_type}: {user_email}")
                return True
            
            logger.warning(f"Usuario no encontrado para eliminar: {user_email}")
            return False
        except Exception as e:
            logger.error(f"Error eliminando usuario {user_email}: {e}", exc_info=True)
            return False
    
    def get_all_users(self, include_inactive: bool = False) -> List[Dict]:
        """
        Obtiene lista de todos los usuarios con sus detalles.
        
        Args:
            include_inactive: Si True, incluye usuarios inactivos
        
        Returns:
            List[Dict]: Lista de usuarios con email, role, permisos, fechas
        """
        try:
            query = self.supabase.table('user_permissions')\
                .select('*')\
                .order('updated_at', desc=True)
            
            if not include_inactive:
                query = query.eq('is_active', True)
            
            response = query.execute()
            
            users = []
            for row in response.data:
                users.append({
                    'email': row['user_email'],
                    'role': row['role'],
                    'role_display': self.ROLE_DISPLAY_NAMES.get(row['role'], row['role']),
                    'permissions': self.ROLE_PERMISSIONS.get(row['role'], []),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'created_by': row.get('created_by', 'N/A'),
                    'is_active': row['is_active'],
                    'role_class': self._get_role_badge_class(row['role'])
                })
            
            logger.debug(f"Obtenidos {len(users)} usuarios")
            return users
        except Exception as e:
            logger.error(f"Error obteniendo usuarios: {e}", exc_info=True)
            return []
    
    def search_users(self, query: str, include_inactive: bool = False) -> List[Dict]:
        """
        Busca usuarios por email usando búsqueda tipo LIKE.
        
        Args:
            query: Texto a buscar en el email
            include_inactive: Si True, incluye usuarios inactivos
        
        Returns:
            List[Dict]: Usuarios que coinciden con la búsqueda
        """
        try:
            supabase_query = self.supabase.table('user_permissions')\
                .select('*')\
                .ilike('user_email', f'%{query}%')\
                .order('user_email')
            
            if not include_inactive:
                supabase_query = supabase_query.eq('is_active', True)
            
            response = supabase_query.execute()
            
            return [dict(row) for row in response.data]
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}", exc_info=True)
            return []
    
    def get_users_by_role(self, role: str, include_inactive: bool = False) -> List[Dict]:
        """
        Filtra usuarios por rol específico.
        
        Args:
            role: Rol a filtrar
            include_inactive: Si True, incluye usuarios inactivos
        
        Returns:
            List[Dict]: Usuarios con el rol especificado
        """
        try:
            query = self.supabase.table('user_permissions')\
                .select('*')\
                .eq('role', role)\
                .order('user_email')
            
            if not include_inactive:
                query = query.eq('is_active', True)
            
            response = query.execute()
            
            return [dict(row) for row in response.data]
        except Exception as e:
            logger.error(f"Error filtrando por rol: {e}", exc_info=True)
            return []
    
    def get_user_details(self, user_email: str) -> Optional[Dict]:
        """
        Obtiene detalles completos de un usuario.
        
        Args:
            user_email: Email del usuario
        
        Returns:
            Dict con todos los datos del usuario o None
        """
        try:
            response = self.supabase.table('user_permissions')\
                .select('*')\
                .eq('user_email', user_email.lower())\
                .single()\
                .execute()
            
            if response.data:
                row = response.data
                return {
                    'email': row['user_email'],
                    'role': row['role'],
                    'role_display': self.ROLE_DISPLAY_NAMES.get(row['role'], row['role']),
                    'permissions': self.ROLE_PERMISSIONS.get(row['role'], []),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'created_by': row.get('created_by', 'N/A'),
                    'is_active': row['is_active']
                }
            
            return None
        except Exception as e:
            logger.error(f"Error obteniendo detalles de {user_email}: {e}", exc_info=True)
            return None
    
    def count_users(self, active_only: bool = True) -> int:
        """
        Cuenta total de usuarios.
        
        Args:
            active_only: Si True, solo cuenta usuarios activos
        
        Returns:
            int: Número de usuarios
        """
        try:
            query = self.supabase.table('user_permissions')\
                .select('id', count='exact')
            
            if active_only:
                query = query.eq('is_active', True)
            
            response = query.execute()
            return response.count if response.count else 0
        except Exception as e:
            logger.error(f"Error contando usuarios: {e}", exc_info=True)
            return 0
    
    def count_admins(self, active_only: bool = True) -> int:
        """
        Cuenta total de administradores (admin_full).
        
        Args:
            active_only: Si True, solo cuenta administradores activos
        
        Returns:
            int: Número de administradores
        """
        try:
            query = self.supabase.table('user_permissions')\
                .select('id', count='exact')\
                .eq('role', 'admin_full')
            
            if active_only:
                query = query.eq('is_active', True)
            
            response = query.execute()
            return response.count if response.count else 0
        except Exception as e:
            logger.error(f"Error contando admins: {e}", exc_info=True)
            return 0
    
    def reactivate_user(self, user_email: str) -> bool:
        """
        Reactiva un usuario previamente desactivado.
        
        Args:
            user_email: Email del usuario a reactivar
        
        Returns:
            bool: True si se reactivó correctamente
        """
        try:
            response = self.supabase.table('user_permissions')\
                .update({'is_active': True})\
                .eq('user_email', user_email.lower())\
                .execute()
            
            if response.data:
                logger.info(f"✅ Usuario reactivado: {user_email}")
                return True
            
            logger.warning(f"Usuario no encontrado para reactivar: {user_email}")
            return False
        except Exception as e:
            logger.error(f"Error reactivando usuario: {e}", exc_info=True)
            return False
    
    @staticmethod
    def _get_role_badge_class(role: str) -> str:
        """
        Retorna clase CSS para badge según rol (para UI).
        
        Args:
            role: Nombre del rol
        
        Returns:
            str: Clase CSS Bootstrap (danger, warning, info, secondary)
        """
        badge_classes = {
            'admin_full': 'danger',
            'admin_export': 'warning',
            'analytics_viewer': 'info',
            'user_basic': 'secondary'
        }
        return badge_classes.get(role, 'secondary')
    
    @staticmethod
    def get_all_roles() -> List[Dict]:
        """
        Obtiene lista de todos los roles disponibles con sus permisos.
        
        Returns:
            List[Dict]: Lista con información de cada rol
        """
        roles = []
        for role_key, permissions in PermissionsManager.ROLE_PERMISSIONS.items():
            roles.append({
                'key': role_key,
                'display_name': PermissionsManager.ROLE_DISPLAY_NAMES.get(role_key, role_key),
                'permissions': permissions,
                'permission_count': len(permissions)
            })
        return roles
