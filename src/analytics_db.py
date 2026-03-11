# analytics_db.py - Sistema de monitoreo de visitas y analytics

import os
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
import pytz

# Timezone de Perú
PERU_TZ = pytz.timezone('America/Lima')

# Intentar importar psycopg2 (solo si está disponible)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None
    RealDictCursor = None

class AnalyticsDB:
    """Gestiona el registro y consulta de estadísticas de uso del dashboard."""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        
        # Usar SQLite para desarrollo local si DATABASE_URL está vacía
        if not self.database_url or self.database_url == "":
            self.use_sqlite = True
            self.db_path = 'analytics.db'
            print("📊 Analytics: Usando SQLite local (analytics.db)")
        else:
            self.use_sqlite = False
            print("📊 Analytics: Usando PostgreSQL en producción")
        
        self.enabled = True
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager para manejar conexiones a la base de datos."""
        if not self.enabled:
            yield None
            return
        
        conn = None
        try:
            if self.use_sqlite:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
            else:
                if not PSYCOPG2_AVAILABLE:
                    print("❌ psycopg2 no disponible. Usando SQLite como fallback.")
                    self.use_sqlite = True
                    if not hasattr(self, 'db_path'):
                        self.db_path = 'analytics.db'
                    conn = sqlite3.connect(self.db_path)
                    conn.row_factory = sqlite3.Row
                else:
                    conn = psycopg2.connect(self.database_url)
            
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Error en conexión DB: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _init_database(self):
        """Crea las tablas necesarias si no existen."""
        try:
            with self.get_connection() as conn:
                if not conn:
                    return
                
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    # Tabla de visitas para SQLite
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS page_visits (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_email TEXT NOT NULL,
                            user_name TEXT,
                            page_url TEXT NOT NULL,
                            page_title TEXT,
                            visit_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            session_duration INTEGER DEFAULT 0,
                            ip_address TEXT,
                            user_agent TEXT,
                            referrer TEXT,
                            method TEXT
                        )
                    """)
                    
                    # Índices para SQLite
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_visits_user 
                        ON page_visits(user_email)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_visits_timestamp 
                        ON page_visits(visit_timestamp DESC)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_visits_page 
                        ON page_visits(page_url)
                    """)
                else:
                    # Tabla de visitas para PostgreSQL
                    if not PSYCOPG2_AVAILABLE:
                        print("❌ psycopg2 no está instalado. Instala con: pip install psycopg2-binary")
                        self.enabled = False
                        return
                    
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS page_visits (
                            id SERIAL PRIMARY KEY,
                            user_email VARCHAR(255) NOT NULL,
                            user_name VARCHAR(255),
                            page_url VARCHAR(500) NOT NULL,
                            page_title VARCHAR(255),
                            visit_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            session_duration INTEGER DEFAULT 0,
                            ip_address VARCHAR(50),
                            user_agent TEXT,
                            referrer VARCHAR(500),
                            method VARCHAR(10)
                        )
                    """)
                    
                    # Índices para PostgreSQL
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_visits_user 
                        ON page_visits(user_email)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_visits_timestamp 
                        ON page_visits(visit_timestamp DESC)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_visits_page 
                        ON page_visits(page_url)
                    """)
                
                print("✅ Tablas de analytics inicializadas correctamente")
                
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {e}")
    
    def log_visit(self, user_email, user_name, page_url, page_title=None, 
                  ip_address=None, user_agent=None, referrer=None, method='GET'):
        """Registra una visita a una página."""
        if not self.enabled:
            return
        
        try:
            # Obtener timestamp en hora de Perú (sin timezone info para compatibilidad)
            utc_now = datetime.now(pytz.UTC)
            peru_time = utc_now.astimezone(PERU_TZ).replace(tzinfo=None)
            
            with self.get_connection() as conn:
                if not conn:
                    return
                
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute("""
                        INSERT INTO page_visits 
                        (user_email, user_name, page_url, page_title, ip_address, 
                         user_agent, referrer, method, visit_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_email, user_name, page_url, page_title, ip_address, 
                          user_agent, referrer, method, peru_time))
                else:
                    cursor.execute("""
                        INSERT INTO page_visits 
                        (user_email, user_name, page_url, page_title, ip_address, 
                         user_agent, referrer, method, visit_timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_email, user_name, page_url, page_title, ip_address, 
                          user_agent, referrer, method, peru_time))
                
        except Exception as e:
            print(f"❌ Error al registrar visita: {e}")
    
    def get_total_visits(self, days=30):
        """Obtiene el total de visitas en los últimos N días."""
        if not self.enabled:
            return 0
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return 0
                
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute("""
                        SELECT COUNT(*) as total
                        FROM page_visits
                        WHERE visit_timestamp >= datetime('now', '-' || ? || ' days')
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                    """, (days,))
                else:
                    cursor.execute("""
                        SELECT COUNT(*) as total
                        FROM page_visits
                        WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                    """, (days,))
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            print(f"❌ Error al obtener visitas totales: {e}")
            return 0
    
    def get_unique_users(self, days=30):
        """Obtiene el número de usuarios únicos en los últimos N días."""
        if not self.enabled:
            return 0
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return 0
                
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute("""
                        SELECT COUNT(DISTINCT user_email) as total
                        FROM page_visits
                        WHERE visit_timestamp >= datetime('now', '-' || ? || ' days')
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                    """, (days,))
                else:
                    cursor.execute("""
                        SELECT COUNT(DISTINCT user_email) as total
                        FROM page_visits
                        WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                    """, (days,))
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            print(f"❌ Error al obtener usuarios únicos: {e}")
            return 0
    
    def get_visits_by_user(self, days=30, limit=20):
        """Obtiene las visitas agrupadas por usuario."""
        if not self.enabled:
            return []
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return []
                
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute("""
                        SELECT 
                            user_email,
                            user_name,
                            COUNT(*) as visit_count,
                            MAX(visit_timestamp) as last_visit
                        FROM page_visits
                        WHERE visit_timestamp >= datetime('now', '-' || ? || ' days')
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                        GROUP BY user_email, user_name
                        ORDER BY visit_count DESC
                        LIMIT ?
                    """, (days, limit))
                else:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute("""
                        SELECT 
                            user_email,
                            user_name,
                            COUNT(*) as visit_count,
                            MAX(visit_timestamp) as last_visit
                        FROM page_visits
                        WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                        GROUP BY user_email, user_name
                        ORDER BY visit_count DESC
                        LIMIT %s
                    """, (days, limit))
                
                rows = cursor.fetchall()
                
                # Convertir a diccionarios si es SQLite
                if self.use_sqlite:
                    return [dict(row) for row in rows]
                return rows
                
        except Exception as e:
            print(f"❌ Error al obtener visitas por usuario: {e}")
            return []
    
    def get_visits_by_page(self, days=30):
        """Obtiene las visitas agrupadas por página."""
        if not self.enabled:
            return []
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return []
                
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute("""
                        SELECT 
                            page_url,
                            page_title,
                            COUNT(*) as visit_count
                        FROM page_visits
                        WHERE visit_timestamp >= datetime('now', '-' || ? || ' days')
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                        GROUP BY page_url, page_title
                        ORDER BY visit_count DESC
                    """, (days,))
                    
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute("""
                        SELECT 
                            page_url,
                            page_title,
                            COUNT(*) as visit_count
                        FROM page_visits
                        WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                        GROUP BY page_url, page_title
                        ORDER BY visit_count DESC
                    """, (days,))
                    
                    return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener visitas por página: {e}")
            return []
    
    def get_visits_by_day(self, days=30):
        """Obtiene las visitas agrupadas por día."""
        if not self.enabled:
            return []
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return []
                
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute("""
                        SELECT 
                            DATE(visit_timestamp) as visit_date,
                            COUNT(*) as visit_count,
                            COUNT(DISTINCT user_email) as unique_users
                        FROM page_visits
                        WHERE visit_timestamp >= datetime('now', '-' || ? || ' days')
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                        GROUP BY DATE(visit_timestamp)
                        ORDER BY visit_date DESC
                    """, (days,))
                    
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute("""
                        SELECT 
                            DATE(visit_timestamp) as visit_date,
                            COUNT(*) as visit_count,
                            COUNT(DISTINCT user_email) as unique_users
                        FROM page_visits
                        WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                        GROUP BY DATE(visit_timestamp)
                        ORDER BY visit_date DESC
                    """, (days,))
                    
                    return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener visitas por día: {e}")
            return []
    
    def get_visits_by_hour(self, days=7):
        """Obtiene las visitas agrupadas por hora del día."""
        if not self.enabled:
            return []
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return []
                
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute("""
                        SELECT 
                            CAST(strftime('%H', visit_timestamp) AS INTEGER) as hour,
                            COUNT(*) as visit_count
                        FROM page_visits
                        WHERE visit_timestamp >= datetime('now', '-' || ? || ' days')
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                        GROUP BY CAST(strftime('%H', visit_timestamp) AS INTEGER)
                        ORDER BY hour
                    """, (days,))
                    
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute("""
                        SELECT 
                            EXTRACT(HOUR FROM visit_timestamp) as hour,
                            COUNT(*) as visit_count
                        FROM page_visits
                        WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                        AND user_email != 'jonathan.cerda@agrovetmarket.com'
                        GROUP BY EXTRACT(HOUR FROM visit_timestamp)
                        ORDER BY hour
                    """, (days,))
                    
                    return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener visitas por hora: {e}")
            return []
    
    def get_recent_visits(self, limit=50):
        """Obtiene las visitas más recientes."""
        if not self.enabled:
            return []
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return []
                
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute("""
                        SELECT 
                            user_email,
                            user_name,
                            page_url,
                            page_title,
                            visit_timestamp,
                            ip_address
                        FROM page_visits
                        WHERE user_email != 'jonathan.cerda@agrovetmarket.com'
                        ORDER BY visit_timestamp DESC
                        LIMIT ?
                    """, (limit,))
                    
                    rows = cursor.fetchall()
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
                            ip_address
                        FROM page_visits
                        WHERE user_email != 'jonathan.cerda@agrovetmarket.com'
                        ORDER BY visit_timestamp DESC
                        LIMIT %s
                    """, (limit,))
                    
                    return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener visitas recientes: {e}")
            return []

    
    @contextmanager
    def get_connection(self):
        """Context manager para manejar conexiones a la base de datos."""
        if not self.enabled:
            yield None
            return
        
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Error en conexión DB: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _init_database(self):
        """Crea las tablas necesarias si no existen."""
        try:
            with self.get_connection() as conn:
                if not conn:
                    return
                
                cursor = conn.cursor()
                
                # Tabla de visitas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS page_visits (
                        id SERIAL PRIMARY KEY,
                        user_email VARCHAR(255) NOT NULL,
                        user_name VARCHAR(255),
                        page_url VARCHAR(500) NOT NULL,
                        page_title VARCHAR(255),
                        visit_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        session_duration INTEGER DEFAULT 0,
                        ip_address VARCHAR(50),
                        user_agent TEXT,
                        referrer VARCHAR(500),
                        method VARCHAR(10)
                    )
                """)
                
                # Índices para mejorar consultas
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_visits_user 
                    ON page_visits(user_email)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_visits_timestamp 
                    ON page_visits(visit_timestamp DESC)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_visits_page 
                    ON page_visits(page_url)
                """)
                
                print("✅ Tablas de analytics inicializadas correctamente")
                
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {e}")
    
    def log_visit(self, user_email, user_name, page_url, page_title=None, 
                  ip_address=None, user_agent=None, referrer=None, method='GET'):
        """Registra una visita a una página."""
        if not self.enabled:
            return
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return
                
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO page_visits 
                    (user_email, user_name, page_url, page_title, ip_address, 
                     user_agent, referrer, method, visit_timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_email, user_name, page_url, page_title, ip_address, 
                      user_agent, referrer, method, datetime.now()))
                
        except Exception as e:
            print(f"❌ Error al registrar visita: {e}")
    
    def get_total_visits(self, days=30):
        """Obtiene el total de visitas en los últimos N días."""
        if not self.enabled:
            return 0
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return 0
                
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM page_visits
                    WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                    AND user_email != 'jonathan.cerda@agrovetmarket.com'
                """, (days,))
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            print(f"❌ Error al obtener visitas totales: {e}")
            return 0
    
    def get_unique_users(self, days=30):
        """Obtiene el número de usuarios únicos en los últimos N días."""
        if not self.enabled:
            return 0
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return 0
                
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_email) as total
                    FROM page_visits
                    WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                    AND user_email != 'jonathan.cerda@agrovetmarket.com'
                """, (days,))
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            print(f"❌ Error al obtener usuarios únicos: {e}")
            return 0
    
    def get_visits_by_user(self, days=30, limit=20):
        """Obtiene las visitas agrupadas por usuario."""
        if not self.enabled:
            return []
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return []
                
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT 
                        user_email,
                        user_name,
                        COUNT(*) as visit_count,
                        MAX(visit_timestamp) as last_visit
                    FROM page_visits
                    WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                    AND user_email != 'jonathan.cerda@agrovetmarket.com'
                    GROUP BY user_email, user_name
                    ORDER BY visit_count DESC
                    LIMIT %s
                """, (days, limit))
                
                return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener visitas por usuario: {e}")
            return []
    
    def get_visits_by_page(self, days=30):
        """Obtiene las visitas agrupadas por página."""
        if not self.enabled:
            return []
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return []
                
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT 
                        page_url,
                        page_title,
                        COUNT(*) as visit_count
                    FROM page_visits
                    WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                    AND user_email != 'jonathan.cerda@agrovetmarket.com'
                    GROUP BY page_url, page_title
                    ORDER BY visit_count DESC
                """, (days,))
                
                return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener visitas por página: {e}")
            return []
    
    def get_visits_by_day(self, days=30):
        """Obtiene las visitas agrupadas por día."""
        if not self.enabled:
            return []
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return []
                
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT 
                        DATE(visit_timestamp) as visit_date,
                        COUNT(*) as visit_count,
                        COUNT(DISTINCT user_email) as unique_users
                    FROM page_visits
                    WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                    AND user_email != 'jonathan.cerda@agrovetmarket.com'
                    GROUP BY DATE(visit_timestamp)
                    ORDER BY visit_date DESC
                """, (days,))
                
                return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener visitas por día: {e}")
            return []
    
    def get_visits_by_hour(self, days=7):
        """Obtiene las visitas agrupadas por hora del día."""
        if not self.enabled:
            return []
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return []
                
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT 
                        EXTRACT(HOUR FROM visit_timestamp) as hour,
                        COUNT(*) as visit_count
                    FROM page_visits
                    WHERE visit_timestamp >= NOW() - INTERVAL '%s days'
                    AND user_email != 'jonathan.cerda@agrovetmarket.com'
                    GROUP BY EXTRACT(HOUR FROM visit_timestamp)
                    ORDER BY hour
                """, (days,))
                
                return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener visitas por hora: {e}")
            return []
    
    def get_recent_visits(self, limit=50):
        """Obtiene las visitas más recientes."""
        if not self.enabled:
            return []
        
        try:
            with self.get_connection() as conn:
                if not conn:
                    return []
                
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT 
                        user_email,
                        user_name,
                        page_url,
                        page_title,
                        visit_timestamp,
                        ip_address
                    FROM page_visits
                    WHERE user_email != 'jonathan.cerda@agrovetmarket.com'
                    ORDER BY visit_timestamp DESC
                    LIMIT %s
                """, (limit,))
                
                return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener visitas recientes: {e}")
            return []

