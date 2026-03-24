"""
audit_logger.py - Sistema de auditoría de cambios de permisos (SUPABASE VERSION)

Registra todas las operaciones CRUD sobre usuarios y permisos usando Supabase,
compatible con producción en Render.com
"""

import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from src.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


class AuditLogger:
    """
    Logger de auditoría para cambios en permisos de usuario usando Supabase.
    
    Registra:
    - Creación de usuarios
    - Actualización de roles
    - Eliminación/desactivación de usuarios
    - IP, timestamp, admin que realizó el cambio
    """
    
    def __init__(self):
        """Inicializa el audit logger con Supabase"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            logger.error("❌ Credenciales de Supabase no configuradas en .env")
            raise ValueError("SUPABASE_URL y SUPABASE_KEY son requeridas")
        
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.enabled = True
            logger.info("✅ AuditLogger inicializado con Supabase")
        except Exception as e:
            logger.error(f"❌ Error al conectar con Supabase: {e}", exc_info=True)
            raise
    
    def log_user_created(self, admin_email: str, new_user_email: str, 
                         role: str, ip_address: str = None, user_agent: str = None):
        """
        Registra creación de nuevo usuario.
        
        Args:
            admin_email: Email del administrador que creó el usuario
            new_user_email: Email del nuevo usuario
            role: Rol asignado al nuevo usuario
            ip_address: IP desde donde se hizo el cambio
            user_agent: User agent del navegador
        """
        try:
            data = {
                'admin_email': admin_email.lower(),
                'action': 'CREATE',
                'target_user_email': new_user_email.lower(),
                'new_value': role,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'details': {
                    'role_assigned': role,
                    'timestamp_readable': datetime.now().isoformat()
                }
            }
            
            response = self.supabase.table('audit_log_permissions')\
                .insert(data)\
                .execute()
            
            if response.data:
                logger.info(f"📝 Audit log: {admin_email} creó usuario {new_user_email} con rol {role}")
            else:
                logger.error(f"Error registrando creación de usuario en audit log")
        except Exception as e:
            logger.error(f"Error en log_user_created: {e}", exc_info=True)
    
    def log_user_updated(self, admin_email: str, user_email: str, 
                         old_role: str, new_role: str, 
                         ip_address: str = None, user_agent: str = None):
        """
        Registra actualización de rol de usuario.
        
        Args:
            admin_email: Email del administrador que actualizó
            user_email: Email del usuario actualizado
            old_role: Rol anterior
            new_role: Rol nuevo
            ip_address: IP desde donde se hizo el cambio
            user_agent: User agent del navegador
        """
        try:
            data = {
                'admin_email': admin_email.lower(),
                'action': 'UPDATE',
                'target_user_email': user_email.lower(),
                'old_value': old_role,
                'new_value': new_role,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'details': {
                    'change': f"{old_role} → {new_role}",
                    'timestamp_readable': datetime.now().isoformat()
                }
            }
            
            response = self.supabase.table('audit_log_permissions')\
                .insert(data)\
                .execute()
            
            if response.data:
                logger.info(f"📝 Audit log: {admin_email} actualizó {user_email}: {old_role} → {new_role}")
            else:
                logger.error(f"Error registrando actualización en audit log")
        except Exception as e:
            logger.error(f"Error en log_user_updated: {e}", exc_info=True)
    
    def log_user_deleted(self, admin_email: str, user_email: str, 
                         soft_delete: bool = True,
                         ip_address: str = None, user_agent: str = None):
        """
        Registra eliminación o desactivación de usuario.
        
        Args:
            admin_email: Email del administrador que eliminó
            user_email: Email del usuario eliminado
            soft_delete: Si True, fue desactivación. Si False, eliminación física
            ip_address: IP desde donde se hizo el cambio
            user_agent: User agent del navegador
        """
        try:
            action = 'DEACTIVATE' if soft_delete else 'DELETE'
            
            data = {
                'admin_email': admin_email.lower(),
                'action': action,
                'target_user_email': user_email.lower(),
                'ip_address': ip_address,
                'user_agent': user_agent,
                'details': {
                    'type': 'soft_delete' if soft_delete else 'hard_delete',
                    'timestamp_readable': datetime.now().isoformat()
                }
            }
            
            response = self.supabase.table('audit_log_permissions')\
                .insert(data)\
                .execute()
            
            if response.data:
                action_text = "desactivó" if soft_delete else "eliminó"
                logger.info(f"📝 Audit log: {admin_email} {action_text} usuario {user_email}")
            else:
                logger.error(f"Error registrando eliminación en audit log")
        except Exception as e:
            logger.error(f"Error en log_user_deleted: {e}", exc_info=True)
    
    def log_user_reactivated(self, admin_email: str, user_email: str,
                             ip_address: str = None, user_agent: str = None):
        """
        Registra reactivación de usuario previamente desactivado.
        
        Args:
            admin_email: Email del administrador que reactivó
            user_email: Email del usuario reactivado
            ip_address: IP desde donde se hizo el cambio
            user_agent: User agent del navegador
        """
        try:
            data = {
                'admin_email': admin_email.lower(),
                'action': 'ACTIVATE',
                'target_user_email': user_email.lower(),
                'new_value': 'REACTIVATED',
                'ip_address': ip_address,
                'user_agent': user_agent,
                'details': {
                    'type': 'reactivation',
                    'timestamp_readable': datetime.now().isoformat()
                }
            }
            
            response = self.supabase.table('audit_log_permissions')\
                .insert(data)\
                .execute()
            
            if response.data:
                logger.info(f"📝 Audit log: {admin_email} reactivó usuario {user_email}")
            else:
                logger.error(f"Error registrando reactivación en audit log")
        except Exception as e:
            logger.error(f"Error en log_user_reactivated: {e}", exc_info=True)
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """
        Obtiene logs recientes con detalles formateados.
        
        Args:
            limit: Número máximo de logs a retornar
        
        Returns:
            List[Dict]: Lista de logs con detalles
        """
        try:
            response = self.supabase.table('audit_log_permissions')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            logs = []
            for row in response.data:
                logs.append({
                    'id': row['id'],
                    'admin_email': row['admin_email'],
                    'action': row['action'],
                    'action_class': self._get_action_badge_class(row['action']),
                    'action_display': self._get_action_display(row['action']),
                    'target_user_email': row['target_user_email'],
                    'old_value': row.get('old_value'),
                    'new_value': row.get('new_value'),
                    'ip_address': row.get('ip_address', 'N/A'),
                    'user_agent': row.get('user_agent'),
                    'timestamp': row['timestamp'],
                    'details': row.get('details', {})
                })
            
            logger.debug(f"Obtenidos {len(logs)} logs recientes")
            return logs
        except Exception as e:
            logger.error(f"Error obteniendo logs: {e}", exc_info=True)
            return []
    
    def get_filtered_logs(self, days: int = 30, action: str = '', 
                          admin_email: str = '', target_email: str = '') -> List[Dict]:
        """
        Obtiene logs con filtros aplicados.
        
        Args:
            days: Número de días hacia atrás
            action: Filtrar por tipo de acción (CREATE, UPDATE, DELETE, etc)
            admin_email: Filtrar por administrador que hizo el cambio
            target_email: Filtrar por usuario afectado
        
        Returns:
            List[Dict]: Logs que cumplen los filtros
        """
        try:
            # Calcular fecha límite
            date_limit = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = self.supabase.table('audit_log_permissions')\
                .select('*')\
                .gte('timestamp', date_limit)\
                .order('timestamp', desc=True)
            
            if action:
                query = query.eq('action', action)
            
            if admin_email:
                query = query.eq('admin_email', admin_email.lower())
            
            if target_email:
                query = query.eq('target_user_email', target_email.lower())
            
            response = query.execute()
            
            return [dict(row) for row in response.data]
        except Exception as e:
            logger.error(f"Error filtrando logs: {e}", exc_info=True)
            return []
    
    def get_user_history(self, user_email: str) -> List[Dict]:
        """
        Obtiene todo el historial de cambios de un usuario específico.
        
        Args:
            user_email: Email del usuario
        
        Returns:
            List[Dict]: Historial completo de cambios del usuario
        """
        try:
            response = self.supabase.table('audit_log_permissions')\
                .select('*')\
                .eq('target_user_email', user_email.lower())\
                .order('timestamp', desc=True)\
                .execute()
            
            return [dict(row) for row in response.data]
        except Exception as e:
            logger.error(f"Error obteniendo historial de {user_email}: {e}", exc_info=True)
            return []
    
    def count_changes_last_week(self) -> int:
        """
        Cuenta cambios realizados en los últimos 7 días.
        
        Returns:
            int: Número de cambios
        """
        try:
            date_limit = (datetime.now() - timedelta(days=7)).isoformat()
            
            response = self.supabase.table('audit_log_permissions')\
                .select('id', count='exact')\
                .gte('timestamp', date_limit)\
                .execute()
            
            return response.count if response.count else 0
        except Exception as e:
            logger.error(f"Error contando cambios: {e}", exc_info=True)
            return 0
    
    def get_admin_activity(self, admin_email: str, days: int = 30) -> Dict:
        """
        Obtiene estadísticas de actividad de un administrador.
        
        Args:
            admin_email: Email del administrador
            days: Número de días hacia atrás
        
        Returns:
            Dict: Estadísticas de actividad
        """
        try:
            date_limit = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table('audit_log_permissions')\
                .select('action')\
                .eq('admin_email', admin_email.lower())\
                .gte('timestamp', date_limit)\
                .execute()
            
            actions = [row['action'] for row in response.data]
            
            stats = {
                'total_changes': len(actions),
                'creates': actions.count('CREATE'),
                'updates': actions.count('UPDATE'),
                'deletes': actions.count('DELETE') + actions.count('DEACTIVATE'),
                'period_days': days
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo actividad de {admin_email}: {e}", exc_info=True)
            return {}
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas generales de auditoría.
        
        Returns:
            Dict: Estadísticas generales
        """
        try:
            # Total de logs
            total_response = self.supabase.table('audit_log_permissions')\
                .select('id', count='exact')\
                .execute()
            
            # Logs última semana
            date_limit = (datetime.now() - timedelta(days=7)).isoformat()
            week_response = self.supabase.table('audit_log_permissions')\
                .select('action', count='exact')\
                .gte('timestamp', date_limit)\
                .execute()
            
            # Contar por acción
            actions_response = self.supabase.table('audit_log_permissions')\
                .select('action')\
                .execute()
            
            actions = [row['action'] for row in actions_response.data]
            
            stats = {
                'total_logs': total_response.count if total_response.count else 0,
                'changes_last_week': week_response.count if week_response.count else 0,
                'total_creates': actions.count('CREATE'),
                'total_updates': actions.count('UPDATE'),
                'total_deletes': actions.count('DELETE') + actions.count('DEACTIVATE'),
                'total_reactivations': actions.count('ACTIVATE')
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}", exc_info=True)
            return {}
    
    @staticmethod
    def _get_action_badge_class(action: str) -> str:
        """
        Retorna clase CSS para badge según acción (para UI).
        
        Args:
            action: Tipo de acción
        
        Returns:
            str: Clase CSS Bootstrap
        """
        badge_classes = {
            'CREATE': 'success',
            'UPDATE': 'info',
            'DELETE': 'danger',
            'DEACTIVATE': 'warning',
            'ACTIVATE': 'primary'
        }
        return badge_classes.get(action, 'secondary')
    
    @staticmethod
    def _get_action_display(action: str) -> str:
        """
        Retorna texto en español para mostrar en UI.
        
        Args:
            action: Tipo de acción
        
        Returns:
            str: Texto en español
        """
        action_displays = {
            'CREATE': 'Creado',
            'UPDATE': 'Actualizado',
            'DELETE': 'Eliminado',
            'DEACTIVATE': 'Desactivado',
            'ACTIVATE': 'Reactivado'
        }
        return action_displays.get(action, action)
