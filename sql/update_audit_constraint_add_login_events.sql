-- ============================================================
-- ACTUALIZACIÓN DE CONSTRAINT PARA EVENTOS DE LOGIN/LOGOUT
-- Dashboard Ventas - Auditoría de Autenticación
-- ============================================================
-- Fecha: 21 de abril de 2026
-- Propósito: Permitir registro de eventos de login/logout en audit_log_permissions
-- ============================================================

-- 1. ELIMINAR el constraint antiguo
ALTER TABLE audit_log_permissions 
DROP CONSTRAINT IF EXISTS audit_log_permissions_action_check;

-- 2. AGREGAR el nuevo constraint con todos los tipos de acción
ALTER TABLE audit_log_permissions 
ADD CONSTRAINT audit_log_permissions_action_check 
CHECK (action IN (
    -- Acciones de permisos (existentes)
    'CREATE', 
    'UPDATE', 
    'DELETE', 
    'DEACTIVATE', 
    'ACTIVATE',
    -- Acciones de autenticación (nuevas) 🆕
    'LOGIN_SUCCESS',
    'LOGIN_FAILED',
    'LOGOUT',
    'SESSION_TIMEOUT'
));

-- 3. ACTUALIZAR el comentario de la columna
COMMENT ON COLUMN audit_log_permissions.action IS 
'Tipo de acción: CREATE, UPDATE, DELETE, DEACTIVATE, ACTIVATE (permisos) | LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, SESSION_TIMEOUT (autenticación)';

-- 4. VERIFICAR que el constraint se aplicó correctamente
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid = 'audit_log_permissions'::regclass
  AND conname = 'audit_log_permissions_action_check';

-- ============================================================
-- RESULTADO ESPERADO:
-- constraint_name                      | definition
-- -------------------------------------|------------------------------------------
-- audit_log_permissions_action_check   | CHECK ((action = ANY (ARRAY['CREATE'::text, ...
-- ============================================================
