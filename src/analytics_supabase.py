"""
analytics_supabase.py - Sistema de Analytics usando Supabase

Migración del sistema de analytics de SQLite/PostgreSQL a Supabase.
Registra y analiza visitas de usuarios al dashboard.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from src.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


class AnalyticsSupabase:
    """Gestiona el registro y consulta de estadísticas de uso usando Supabase."""
    
    TABLE_NAME = 'page_visits_ventas_locales'  # Nombre de la tabla en Supabase
    
    def __init__(self):
        """Inicializa conexión a Supabase."""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            logger.error("❌ Credenciales de Supabase no configuradas para Analytics")
            self.enabled = False
            return
        
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.enabled = True
            logger.info("✅ AnalyticsSupabase inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error conectando a Supabase (Analytics): {e}", exc_info=True)
            self.enabled = False
    
    def log_visit(self, user_email: str, user_name: str, page_url: str, 
                  page_title: Optional[str] = None, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None, referrer: Optional[str] = None,
                  method: str = 'GET') -> bool:
        """
        Registra una visita a una página.
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            page_url: URL visitada
            page_title: Título de la página
            ip_address: IP del visitante
            user_agent: User agent del navegador
            referrer: URL de referencia
            method: Método HTTP (GET, POST, etc.)
        
        Returns:
            bool: True si se registró correctamente
        """
        if not self.enabled:
            return False
        
        try:
            data = {
                'user_email': user_email.lower() if user_email else None,
                'user_name': user_name,
                'page_url': page_url,
                'page_title': page_title,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'referrer': referrer,
                'method': method,
                'visit_timestamp': datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table(self.TABLE_NAME)\
                .insert(data)\
                .execute()
            
            if response.data:
                logger.debug(f"📊 Visita registrada: {user_email} → {page_url}")
                return True
            
            logger.warning(f"⚠️ No se pudo registrar visita de {user_email}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error registrando visita: {e}", exc_info=True)
            return False
    
    def get_total_visits(self, days: int = 30) -> int:
        """
        Obtiene el total de visitas en los últimos N días.
        
        Args:
            days: Número de días a consultar
        
        Returns:
            int: Total de visitas
        """
        if not self.enabled:
            return 0
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table(self.TABLE_NAME)\
                .select('id', count='exact')\
                .gte('visit_timestamp', cutoff_date)\
                .neq('user_email', 'jonathan.cerda@agrovetmarket.com')\
                .execute()
            
            return response.count if response.count else 0
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo visitas totales: {e}", exc_info=True)
            return 0
    
    def get_unique_users(self, days: int = 30) -> int:
        """
        Obtiene el número de usuarios únicos en los últimos N días.
        
        Args:
            days: Número de días a consultar
        
        Returns:
            int: Número de usuarios únicos
        """
        if not self.enabled:
            return 0
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Supabase no tiene COUNT(DISTINCT), usamos query RPC o procesamos en Python
            response = self.supabase.table(self.TABLE_NAME)\
                .select('user_email')\
                .gte('visit_timestamp', cutoff_date)\
                .neq('user_email', 'jonathan.cerda@agrovetmarket.com')\
                .execute()
            
            if response.data:
                unique_emails = set(row['user_email'] for row in response.data if row.get('user_email'))
                return len(unique_emails)
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuarios únicos: {e}", exc_info=True)
            return 0
    
    def get_visits_by_user(self, days: int = 30, limit: int = 20) -> List[Dict]:
        """
        Obtiene las visitas agrupadas por usuario.
        
        Args:
            days: Número de días a consultar
            limit: Número máximo de usuarios a retornar
        
        Returns:
            List[Dict]: Lista de usuarios con sus estadísticas
        """
        if not self.enabled:
            return []
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Obtener todas las visitas y agrupar en Python
            response = self.supabase.table(self.TABLE_NAME)\
                .select('user_email, user_name, visit_timestamp')\
                .gte('visit_timestamp', cutoff_date)\
                .neq('user_email', 'jonathan.cerda@agrovetmarket.com')\
                .order('visit_timestamp', desc=True)\
                .execute()
            
            if not response.data:
                return []
            
            # Agrupar por usuario
            user_stats = {}
            for row in response.data:
                email = row['user_email']
                if email not in user_stats:
                    user_stats[email] = {
                        'user_email': email,
                        'user_name': row.get('user_name', email),
                        'visit_count': 0,
                        'last_visit': row['visit_timestamp']
                    }
                user_stats[email]['visit_count'] += 1
            
            # Ordenar por visitas y limitar
            sorted_users = sorted(
                user_stats.values(),
                key=lambda x: x['visit_count'],
                reverse=True
            )[:limit]
            
            return sorted_users
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo visitas por usuario: {e}", exc_info=True)
            return []
    
    def get_visits_by_page(self, days: int = 30) -> List[Dict]:
        """
        Obtiene las visitas agrupadas por página.
        
        Args:
            days: Número de días a consultar
        
        Returns:
            List[Dict]: Lista de páginas con sus estadísticas
        """
        if not self.enabled:
            return []
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Obtener todas las visitas y agrupar en Python
            response = self.supabase.table(self.TABLE_NAME)\
                .select('page_url, page_title')\
                .gte('visit_timestamp', cutoff_date)\
                .neq('user_email', 'jonathan.cerda@agrovetmarket.com')\
                .execute()
            
            if not response.data:
                return []
            
            # Agrupar por página
            page_stats = {}
            for row in response.data:
                url = row['page_url']
                if url not in page_stats:
                    page_stats[url] = {
                        'page_url': url,
                        'page_title': row.get('page_title', url),
                        'visit_count': 0
                    }
                page_stats[url]['visit_count'] += 1
            
            # Ordenar por visitas
            sorted_pages = sorted(
                page_stats.values(),
                key=lambda x: x['visit_count'],
                reverse=True
            )
            
            return sorted_pages
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo visitas por página: {e}", exc_info=True)
            return []
    
    def get_visits_by_day(self, days: int = 30) -> List[Dict]:
        """
        Obtiene las visitas agrupadas por día.
        
        Args:
            days: Número de días a consultar
        
        Returns:
            List[Dict]: Lista de días con sus estadísticas
        """
        if not self.enabled:
            return []
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Obtener todas las visitas
            response = self.supabase.table(self.TABLE_NAME)\
                .select('visit_timestamp, user_email')\
                .gte('visit_timestamp', cutoff_date)\
                .neq('user_email', 'jonathan.cerda@agrovetmarket.com')\
                .order('visit_timestamp', desc=True)\
                .execute()
            
            if not response.data:
                return []
            
            # Agrupar por día
            day_stats = {}
            for row in response.data:
                try:
                    visit_dt = datetime.fromisoformat(row['visit_timestamp'].replace('Z', '+00:00'))
                    visit_date = visit_dt.date().isoformat()
                    
                    if visit_date not in day_stats:
                        day_stats[visit_date] = {
                            'visit_date': visit_date,
                            'visit_count': 0,
                            'unique_users': set()
                        }
                    
                    day_stats[visit_date]['visit_count'] += 1
                    day_stats[visit_date]['unique_users'].add(row['user_email'])
                except Exception as e:
                    logger.warning(f"Error procesando fecha: {e}")
                    continue
            
            # Convertir sets a contadores y ordenar
            result = []
            for date, stats in day_stats.items():
                result.append({
                    'visit_date': date,
                    'visit_count': stats['visit_count'],
                    'unique_users': len(stats['unique_users'])
                })
            
            result.sort(key=lambda x: x['visit_date'], reverse=True)
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo visitas por día: {e}", exc_info=True)
            return []
    
    def get_visits_by_hour(self, days: int = 7) -> List[Dict]:
        """
        Obtiene las visitas agrupadas por hora del día (últimos N días).
        
        Args:
            days: Número de días a consultar (default: 7)
        
        Returns:
            List[Dict]: Lista de horas con sus estadísticas
        """
        if not self.enabled:
            return []
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Obtener todas las visitas
            response = self.supabase.table(self.TABLE_NAME)\
                .select('visit_timestamp')\
                .gte('visit_timestamp', cutoff_date)\
                .neq('user_email', 'jonathan.cerda@agrovetmarket.com')\
                .execute()
            
            if not response.data:
                return []
            
            # Agrupar por hora
            hour_stats = {}
            for row in response.data:
                try:
                    visit_dt = datetime.fromisoformat(row['visit_timestamp'].replace('Z', '+00:00'))
                    hour = visit_dt.hour
                    
                    if hour not in hour_stats:
                        hour_stats[hour] = {
                            'hour': hour,
                            'visit_count': 0
                        }
                    
                    hour_stats[hour]['visit_count'] += 1
                except Exception as e:
                    logger.warning(f"Error procesando hora: {e}")
                    continue
            
            # Convertir a lista y ordenar
            result = sorted(hour_stats.values(), key=lambda x: x['hour'])
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo visitas por hora: {e}", exc_info=True)
            return []
