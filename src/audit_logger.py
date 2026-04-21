"""
audit_logger.py - Sistema de auditoría de cambios de permisos y accesos (SUPABASE VERSION)

Registra todas las operaciones CRUD sobre usuarios y permisos, 
así como eventos de autenticación (login/logout) usando Supabase,
compatible con producción en Render.com
"""

import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from supabase import create_client, Client
from src.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)

# Timezone de Perú
PERU_TZ = pytz.timezone('America/Lima')
UTC_TZ = pytz.UTC


class AuditLogger:
    """
    Logger de auditoría para cambios en permisos de usuario y accesos usando Supabase.
    
    Registra:
    - Creación de usuarios
    - Actualización de roles
    - Eliminación/desactivación de usuarios
    - Reactivación de usuarios
    - Inicio de sesión exitoso
    - Intentos de login fallidos
    - Cierre de sesión
    - Expiración de sesión por timeout
    - IP, timestamp, user agent de todas las operaciones
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
    
    def log_login_success(self, user_email: str, user_name: str = None, 
                         role: str = None, ip_address: str = None, 
                         user_agent: str = None, oauth_provider: str = 'google',
                         session_id: str = None):
        """
        Registra inicio de sesión exitoso.
        
        Args:
            user_email: Email del usuario que inició sesión
            user_name: Nombre completo del usuario
            role: Rol del usuario en el sistema
            ip_address: IP desde donde se hizo el login
            user_agent: User agent del navegador
            oauth_provider: Proveedor OAuth usado (default: 'google')
            session_id: ID de sesión para correlación con logout
        """
        try:
            data = {
                'admin_email': user_email.lower(),  # El usuario es actor de su propio login
                'action': 'LOGIN_SUCCESS',
                'target_user_email': user_email.lower(),
                'new_value': role,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'details': {
                    'name': user_name,
                    'role': role,
                    'oauth_provider': oauth_provider,
                    'session_id': session_id,
                    'timestamp_readable': datetime.now().isoformat()
                }
            }
            
            response = self.supabase.table('audit_log_permissions')\
                .insert(data)\
                .execute()
            
            if response.data:
                logger.info(f"🔓 Audit log: {user_email} inició sesión exitosamente (rol: {role})")
            else:
                logger.error(f"Error registrando login exitoso en audit log")
        except Exception as e:
            logger.error(f"Error en log_login_success: {e}", exc_info=True)
    
    def log_login_failed(self, attempted_email: str = None, 
                        ip_address: str = None, user_agent: str = None,
                        failure_reason: str = 'unknown', error_message: str = None):
        """
        Registra intento de inicio de sesión fallido.
        
        Args:
            attempted_email: Email que intentó acceder (puede ser None si falló OAuth)
            ip_address: IP desde donde se hizo el intento
            user_agent: User agent del navegador
            failure_reason: Razón del fallo (user_not_authorized, oauth_error, invalid_domain, etc)
            error_message: Mensaje descriptivo del error
        """
        try:
            data = {
                'admin_email': attempted_email.lower() if attempted_email else 'unknown',
                'action': 'LOGIN_FAILED',
                'target_user_email': attempted_email.lower() if attempted_email else 'unknown',
                'old_value': failure_reason,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'details': {
                    'failure_reason': failure_reason,
                    'error_message': error_message,
                    'timestamp_readable': datetime.now().isoformat()
                }
            }
            
            response = self.supabase.table('audit_log_permissions')\
                .insert(data)\
                .execute()
            
            if response.data:
                logger.warning(f"🔒 Audit log: Intento de login fallido - {attempted_email or 'unknown'} ({failure_reason})")
            else:
                logger.error(f"Error registrando login fallido en audit log")
        except Exception as e:
            logger.error(f"Error en log_login_failed: {e}", exc_info=True)
    
    def log_logout(self, user_email: str, ip_address: str = None,
                  session_duration: str = None, logout_type: str = 'manual',
                  session_id: str = None):
        """
        Registra cierre de sesión.
        
        Args:
            user_email: Email del usuario que cerró sesión
            ip_address: IP desde donde se hizo el logout
            session_duration: Duración total de la sesión (formato: 'HH:MM:SS')
            logout_type: Tipo de logout ('manual', 'timeout', 'admin_force')
            session_id: ID de sesión para correlación con login
        """
        try:
            data = {
                'admin_email': user_email.lower(),
                'action': 'LOGOUT',
                'target_user_email': user_email.lower(),
                'new_value': logout_type,
                'ip_address': ip_address,
                'details': {
                    'logout_type': logout_type,
                    'session_duration': session_duration,
                    'session_id': session_id,
                    'timestamp_readable': datetime.now().isoformat()
                }
            }
            
            response = self.supabase.table('audit_log_permissions')\
                .insert(data)\
                .execute()
            
            if response.data:
                logger.info(f"🔐 Audit log: {user_email} cerró sesión ({logout_type})")
            else:
                logger.error(f"Error registrando logout en audit log")
        except Exception as e:
            logger.error(f"Error en log_logout: {e}", exc_info=True)
    
    def log_session_timeout(self, user_email: str, timeout_type: str = 'inactivity',
                           last_activity: str = None, ip_address: str = None):
        """
        Registra expiración de sesión por timeout.
        
        Args:
            user_email: Email del usuario cuya sesión expiró
            timeout_type: Tipo de timeout ('inactivity', 'absolute_limit')
            last_activity: Timestamp de última actividad
            ip_address: Última IP conocida
        """
        try:
            data = {
                'admin_email': user_email.lower(),
                'action': 'SESSION_TIMEOUT',
                'target_user_email': user_email.lower(),
                'old_value': timeout_type,
                'ip_address': ip_address,
                'details': {
                    'timeout_type': timeout_type,
                    'last_activity': last_activity,
                    'timestamp_readable': datetime.now().isoformat()
                }
            }
            
            response = self.supabase.table('audit_log_permissions')\
                .insert(data)\
                .execute()
            
            if response.data:
                logger.info(f"⏱️ Audit log: Sesión de {user_email} expiró por {timeout_type}")
            else:
                logger.error(f"Error registrando session timeout en audit log")
        except Exception as e:
            logger.error(f"Error en log_session_timeout: {e}", exc_info=True)
    
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
                          admin_email: str = '', target_email: str = '',
                          exclude_auth_events: bool = False) -> List[Dict]:
        """
        Obtiene logs con filtros aplicados.
        
        Args:
            days: Número de días hacia atrás
            action: Filtrar por tipo de acción (CREATE, UPDATE, DELETE, etc)
            admin_email: Filtrar por administrador que hizo el cambio
            target_email: Filtrar por usuario afectado
            exclude_auth_events: Si True, excluye LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, SESSION_TIMEOUT
        
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
            
            # 🆕 Excluir eventos de autenticación si se solicita
            if exclude_auth_events:
                query = query.not_.in_('action', ['LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT', 'SESSION_TIMEOUT'])
            
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
        Obtiene estadísticas generales de auditoría de PERMISOS solamente.
        Excluye eventos de autenticación (LOGIN, LOGOUT, etc).
        
        Returns:
            Dict: Estadísticas generales de cambios de permisos
        """
        try:
            # Acciones de permisos (excluye autenticación)
            permission_actions = ['CREATE', 'UPDATE', 'DELETE', 'DEACTIVATE', 'ACTIVATE']
            
            # Total de logs de permisos
            total_response = self.supabase.table('audit_log_permissions')\
                .select('id', count='exact')\
                .in_('action', permission_actions)\
                .execute()
            
            # Logs última semana (solo permisos)
            date_limit = (datetime.now() - timedelta(days=7)).isoformat()
            week_response = self.supabase.table('audit_log_permissions')\
                .select('action', count='exact')\
                .in_('action', permission_actions)\
                .gte('timestamp', date_limit)\
                .execute()
            
            # Contar por acción (solo permisos)
            actions_response = self.supabase.table('audit_log_permissions')\
                .select('action')\
                .in_('action', permission_actions)\
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
    
    def get_security_stats(self, hours: int = 24) -> Dict:
        """
        Obtiene estadísticas de seguridad (login/logout) para dashboard.
        
        Args:
            hours: Número de horas hacia atrás (default: 24)
        
        Returns:
            Dict: Estadísticas de seguridad con métricas de login/logout
        """
        try:
            date_limit = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            # Obtener todos los eventos de seguridad recientes
            response = self.supabase.table('audit_log_permissions')\
                .select('*')\
                .in_('action', ['LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT', 'SESSION_TIMEOUT'])\
                .gte('timestamp', date_limit)\
                .execute()
            
            events = response.data
            
            # Contar eventos por tipo
            login_success = sum(1 for e in events if e['action'] == 'LOGIN_SUCCESS')
            login_failed = sum(1 for e in events if e['action'] == 'LOGIN_FAILED')
            logout_manual = sum(1 for e in events if e['action'] == 'LOGOUT')
            session_timeout = sum(1 for e in events if e['action'] == 'SESSION_TIMEOUT')
            
            # Calcular tasa de éxito de login
            total_login_attempts = login_success + login_failed
            success_rate = (login_success / total_login_attempts * 100) if total_login_attempts > 0 else 100
            
            # IPs con más intentos fallidos
            failed_by_ip = {}
            for event in events:
                if event['action'] == 'LOGIN_FAILED':
                    ip = event.get('ip_address', 'Unknown')
                    failed_by_ip[ip] = failed_by_ip.get(ip, 0) + 1
            
            top_failed_ips = sorted(failed_by_ip.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Usuarios con más intentos fallidos
            failed_by_user = {}
            for event in events:
                if event['action'] == 'LOGIN_FAILED':
                    user = event.get('target_user_email', 'Unknown')
                    failed_by_user[user] = failed_by_user.get(user, 0) + 1
            
            top_failed_users = sorted(failed_by_user.items(), key=lambda x: x[1], reverse=True)[:5]
            
            stats = {
                'period_hours': hours,
                'login_success': login_success,
                'login_failed': login_failed,
                'logout_manual': logout_manual,
                'session_timeout': session_timeout,
                'total_login_attempts': total_login_attempts,
                'success_rate': round(success_rate, 2),
                'top_failed_ips': [{'ip': ip, 'count': count} for ip, count in top_failed_ips],
                'top_failed_users': [{'user': user, 'count': count} for user, count in top_failed_users],
                'active_users': login_success  # Usuarios que iniciaron sesión en el período
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de seguridad: {e}", exc_info=True)
            return {
                'period_hours': hours,
                'login_success': 0,
                'login_failed': 0,
                'logout_manual': 0,
                'session_timeout': 0,
                'total_login_attempts': 0,
                'success_rate': 100,
                'top_failed_ips': [],
                'top_failed_users': [],
                'active_users': 0
            }
    
    def get_login_timeline(self, hours: int = 24) -> List[Dict]:
        """
        Obtiene timeline de login/logout por hora para gráficas EN HORA DE PERÚ.
        
        Args:
            hours: Número de horas hacia atrás
        
        Returns:
            List[Dict]: Lista de eventos agrupados por hora (hora de Perú)
        """
        try:
            date_limit = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            response = self.supabase.table('audit_log_permissions')\
                .select('action, timestamp')\
                .in_('action', ['LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT', 'SESSION_TIMEOUT'])\
                .gte('timestamp', date_limit)\
                .order('timestamp', desc=False)\
                .execute()
            
            events = response.data
            
            # Agrupar por hora (CONVERTIR A HORA DE PERÚ)
            hourly_data = {}
            for event in events:
                # Parse timestamp UTC
                utc_timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                
                # Convertir a hora de Perú
                if utc_timestamp.tzinfo is None:
                    utc_timestamp = UTC_TZ.localize(utc_timestamp)
                peru_timestamp = utc_timestamp.astimezone(PERU_TZ)
                
                # Agrupar por hora de Perú
                hour_key = peru_timestamp.strftime('%Y-%m-%d %H:00')
                
                if hour_key not in hourly_data:
                    hourly_data[hour_key] = {
                        'hour': hour_key,
                        'login_success': 0,
                        'login_failed': 0,
                        'logout': 0,
                        'timeout': 0
                    }
                
                action = event['action']
                if action == 'LOGIN_SUCCESS':
                    hourly_data[hour_key]['login_success'] += 1
                elif action == 'LOGIN_FAILED':
                    hourly_data[hour_key]['login_failed'] += 1
                elif action == 'LOGOUT':
                    hourly_data[hour_key]['logout'] += 1
                elif action == 'SESSION_TIMEOUT':
                    hourly_data[hour_key]['timeout'] += 1
            
            return sorted(hourly_data.values(), key=lambda x: x['hour'])
        except Exception as e:
            logger.error(f"Error obteniendo timeline de login: {e}", exc_info=True)
            return []
    
    def get_recent_failed_attempts(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene intentos de login fallidos recientes para alertas.
        
        Args:
            limit: Número máximo de intentos a retornar
        
        Returns:
            List[Dict]: Lista de intentos fallidos recientes
        """
        try:
            response = self.supabase.table('audit_log_permissions')\
                .select('*')\
                .eq('action', 'LOGIN_FAILED')\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            attempts = []
            for row in response.data:
                attempts.append({
                    'timestamp': row['timestamp'],
                    'attempted_email': row.get('target_user_email', 'Unknown'),
                    'ip_address': row.get('ip_address', 'Unknown'),
                    'failure_reason': row.get('details', {}).get('failure_reason', 'Unknown'),
                    'error_message': row.get('details', {}).get('error_message', ''),
                    'user_agent': row.get('user_agent', '')[:50] + '...' if row.get('user_agent') else 'Unknown'
                })
            
            return attempts
        except Exception as e:
            logger.error(f"Error obteniendo intentos fallidos: {e}", exc_info=True)
            return []
    
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
            'ACTIVATE': 'primary',
            'LOGIN_SUCCESS': 'success',
            'LOGIN_FAILED': 'danger',
            'LOGOUT': 'secondary',
            'SESSION_TIMEOUT': 'warning'
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
            'ACTIVATE': 'Reactivado',
            'LOGIN_SUCCESS': 'Login Exitoso',
            'LOGIN_FAILED': 'Login Fallido',
            'LOGOUT': 'Cerró Sesión',
            'SESSION_TIMEOUT': 'Sesión Expirada'
        }
        return action_displays.get(action, action)
