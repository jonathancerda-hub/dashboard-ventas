-- ============================================================
-- TABLAS DE PERMISOS Y AUDITORÍA PARA SUPABASE
-- Dashboard Ventas - Sistema de Administración de Usuarios
-- ============================================================
-- Fecha: 24 de marzo de 2026
-- Propósito: Gestión de usuarios y permisos del dashboard
-- Compatible con: PostgreSQL 12+ (Supabase)
-- ============================================================

-- ============================================================
-- TABLA 1: user_permissions
-- Almacena usuarios y sus roles de acceso
-- ============================================================

CREATE TABLE IF NOT EXISTS user_permissions (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('admin_full', 'admin_export', 'analytics_viewer', 'user_basic')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,  -- Email del admin que creó el usuario
    is_active BOOLEAN DEFAULT TRUE  -- Para soft delete
);

-- Comentarios descriptivos
COMMENT ON TABLE user_permissions IS 'Usuarios del dashboard con sus roles de acceso';
COMMENT ON COLUMN user_permissions.user_email IS 'Email corporativo del usuario (único)';
COMMENT ON COLUMN user_permissions.role IS 'Rol del usuario: admin_full, admin_export, analytics_viewer, user_basic';
COMMENT ON COLUMN user_permissions.is_active IS 'TRUE si el usuario está activo, FALSE si fue desactivado';

-- Índices para optimización de consultas
CREATE INDEX IF NOT EXISTS idx_user_email ON user_permissions(user_email);
CREATE INDEX IF NOT EXISTS idx_role ON user_permissions(role);
CREATE INDEX IF NOT EXISTS idx_is_active ON user_permissions(is_active);
CREATE INDEX IF NOT EXISTS idx_created_at ON user_permissions(created_at DESC);

-- ============================================================
-- TABLA 2: audit_log_permissions
-- Registra todos los cambios en permisos para auditoría
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_log_permissions (
    id BIGSERIAL PRIMARY KEY,
    admin_email TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'DEACTIVATE', 'ACTIVATE')),
    target_user_email TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    details JSONB  -- Para información adicional si es necesaria
);

-- Comentarios descriptivos
COMMENT ON TABLE audit_log_permissions IS 'Log de auditoría de cambios en permisos de usuarios';
COMMENT ON COLUMN audit_log_permissions.admin_email IS 'Email del administrador que realizó el cambio';
COMMENT ON COLUMN audit_log_permissions.action IS 'Tipo de acción: CREATE, UPDATE, DELETE, DEACTIVATE, ACTIVATE';
COMMENT ON COLUMN audit_log_permissions.target_user_email IS 'Email del usuario afectado por el cambio';
COMMENT ON COLUMN audit_log_permissions.old_value IS 'Valor anterior (ej: rol antiguo)';
COMMENT ON COLUMN audit_log_permissions.new_value IS 'Valor nuevo (ej: rol nuevo)';
COMMENT ON COLUMN audit_log_permissions.details IS 'JSON con información adicional del cambio';

-- Índices para búsquedas rápidas de auditoría
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log_permissions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_admin ON audit_log_permissions(admin_email);
CREATE INDEX IF NOT EXISTS idx_audit_target ON audit_log_permissions(target_user_email);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log_permissions(action);

-- ============================================================
-- POLÍTICAS DE SEGURIDAD (Row Level Security - RLS)
-- ============================================================

-- Habilitar RLS en ambas tablas
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log_permissions ENABLE ROW LEVEL SECURITY;

-- Política: Solo service_role puede acceder (backend con SUPABASE_KEY)
-- Esto previene acceso directo desde frontend

-- User Permissions: Solo backend puede leer/escribir
CREATE POLICY "Backend puede leer user_permissions" 
    ON user_permissions FOR SELECT 
    USING (auth.role() = 'service_role');

CREATE POLICY "Backend puede insertar user_permissions" 
    ON user_permissions FOR INSERT 
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Backend puede actualizar user_permissions" 
    ON user_permissions FOR UPDATE 
    USING (auth.role() = 'service_role');

CREATE POLICY "Backend puede eliminar user_permissions" 
    ON user_permissions FOR DELETE 
    USING (auth.role() = 'service_role');

-- Audit Log: Solo backend puede escribir, solo service_role puede leer
CREATE POLICY "Backend puede leer audit_log_permissions" 
    ON audit_log_permissions FOR SELECT 
    USING (auth.role() = 'service_role');

CREATE POLICY "Backend puede insertar audit_log_permissions" 
    ON audit_log_permissions FOR INSERT 
    WITH CHECK (auth.role() = 'service_role');

-- No permitir UPDATE ni DELETE de logs de auditoría (inmutables)

-- ============================================================
-- FUNCIÓN: Actualizar timestamp automáticamente
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar updated_at automáticamente
DROP TRIGGER IF EXISTS update_user_permissions_updated_at ON user_permissions;
CREATE TRIGGER update_user_permissions_updated_at
    BEFORE UPDATE ON user_permissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DATOS INICIALES (SEED DATA)
-- ============================================================

-- Insertar primer administrador (cambiar email según tu empresa)
INSERT INTO user_permissions (user_email, role, created_by, is_active)
VALUES ('jonathan.cerda@agrovetmarket.com', 'admin_full', 'SYSTEM', TRUE)
ON CONFLICT (user_email) DO NOTHING;

-- Log de auditoría del usuario inicial
INSERT INTO audit_log_permissions (admin_email, action, target_user_email, new_value, ip_address)
VALUES ('SYSTEM', 'CREATE', 'jonathan.cerda@agrovetmarket.com', 'admin_full', '127.0.0.1')
ON CONFLICT DO NOTHING;

-- ============================================================
-- VISTAS ÚTILES (OPTIONAL)
-- ============================================================

-- Vista: Usuarios activos con conteo de cambios
CREATE OR REPLACE VIEW v_active_users_with_audit AS
SELECT 
    up.user_email,
    up.role,
    up.created_at,
    up.updated_at,
    up.created_by,
    COUNT(al.id) as total_changes,
    MAX(al.timestamp) as last_change_at
FROM user_permissions up
LEFT JOIN audit_log_permissions al ON up.user_email = al.target_user_email
WHERE up.is_active = TRUE
GROUP BY up.user_email, up.role, up.created_at, up.updated_at, up.created_by
ORDER BY up.updated_at DESC;

COMMENT ON VIEW v_active_users_with_audit IS 'Usuarios activos con su historial de cambios';

-- Vista: Estadísticas de roles
CREATE OR REPLACE VIEW v_role_statistics AS
SELECT 
    role,
    COUNT(*) as total_users,
    COUNT(*) FILTER (WHERE is_active = TRUE) as active_users,
    COUNT(*) FILTER (WHERE is_active = FALSE) as inactive_users
FROM user_permissions
GROUP BY role
ORDER BY total_users DESC;

COMMENT ON VIEW v_role_statistics IS 'Estadísticas de usuarios por rol';

-- ============================================================
-- GRANTS (PERMISOS)
-- ============================================================

-- Si tienes roles específicos en Supabase, otorgar permisos aquí
-- Por defecto, service_role tiene acceso completo

-- ============================================================
-- SCRIPT COMPLETADO
-- ============================================================

-- Para ejecutar este script:
-- 1. Ir a Supabase Dashboard > SQL Editor
-- 2. Copiar y pegar todo este script
-- 3. Ejecutar (Run)
-- 4. Verificar que las tablas se crearon correctamente

-- Para verificar las tablas:
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE '%permission%';

-- Para verificar los índices:
-- SELECT indexname FROM pg_indexes WHERE schemaname = 'public' AND tablename IN ('user_permissions', 'audit_log_permissions');

-- Para ver políticas de RLS:
-- SELECT * FROM pg_policies WHERE tablename IN ('user_permissions', 'audit_log_permissions');
