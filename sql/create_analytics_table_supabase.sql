-- ============================================
-- MIGRACIÓN DE ANALYTICS A SUPABASE
-- ============================================
-- Tabla: page_visits_ventas_locales - Registro de visitas y actividad de usuarios
-- ============================================

-- Crear tabla de visitas
CREATE TABLE IF NOT EXISTS page_visits_ventas_locales (
    id BIGSERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    user_name VARCHAR(255),
    page_url VARCHAR(500) NOT NULL,
    page_title VARCHAR(255),
    visit_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_duration INTEGER DEFAULT 0,
    ip_address VARCHAR(50),
    user_agent TEXT,
    referrer VARCHAR(500),
    method VARCHAR(10) DEFAULT 'GET',
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_ventas_visits_user 
ON page_visits_ventas_locales(user_email);

CREATE INDEX IF NOT EXISTS idx_ventas_visits_timestamp 
ON page_visits_ventas_locales(visit_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_ventas_visits_page 
ON page_visits_ventas_locales(page_url);

CREATE INDEX IF NOT EXISTS idx_ventas_visits_created_at 
ON page_visits_ventas_locales(created_at DESC);

-- Comentarios descriptivos
COMMENT ON TABLE page_visits_ventas_locales IS 'Registro de visitas y actividad de usuarios en el dashboard de ventas';
COMMENT ON COLUMN page_visits_ventas_locales.user_email IS 'Email del usuario que realizó la visita';
COMMENT ON COLUMN page_visits_ventas_locales.visit_timestamp IS 'Timestamp de la visita en UTC';
COMMENT ON COLUMN page_visits_ventas_locales.session_duration IS 'Duración de la sesión en segundos';
COMMENT ON COLUMN page_visits_ventas_locales.page_url IS 'URL de la página visitada';
COMMENT ON COLUMN page_visits_ventas_locales.page_title IS 'Título de la página visitada';

-- ============================================
-- POLÍTICAS RLS (Row Level Security)
-- ============================================

-- Habilitar RLS
ALTER TABLE page_visits_ventas_locales ENABLE ROW LEVEL SECURITY;

-- Política: Solo service_role puede insertar
CREATE POLICY "service_role_insert_visits" 
ON page_visits_ventas_locales 
FOR INSERT 
TO service_role 
WITH CHECK (true);

-- Política: Solo service_role puede leer
CREATE POLICY "service_role_select_visits" 
ON page_visits_ventas_locales 
FOR SELECT 
TO service_role 
USING (true);

-- Política: Solo service_role puede actualizar
CREATE POLICY "service_role_update_visits" 
ON page_visits_ventas_locales 
FOR UPDATE 
TO service_role 
USING (true);

-- Política: Solo service_role puede eliminar
CREATE POLICY "service_role_delete_visits" 
ON page_visits_ventas_locales 
FOR DELETE 
TO service_role 
USING (true);

-- ============================================
-- FIN DE SCRIPT DE MIGRACIÓN
-- ============================================
