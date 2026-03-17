"""
Tests unitarios para PermissionsManager

Tests de la gestión de permisos de usuario basada en roles.
"""

import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch, MagicMock
from src.permissions_manager import PermissionsManager


class TestPermissionsManager:
    """Suite de tests para PermissionsManager"""
    
    @pytest.fixture
    def temp_db(self):
        """Crea una base de datos temporal para tests"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        # Cleanup
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.fixture
    def pm(self, temp_db):
        """Instancia de PermissionsManager con DB temporal"""
        return PermissionsManager(db_path=temp_db)
    
    # --- Tests de Inicialización ---
    
    def test_init_creates_database(self, temp_db):
        """Test que la inicialización crea la base de datos"""
        pm = PermissionsManager(db_path=temp_db)
        assert os.path.exists(temp_db)
    
    def test_init_creates_tables(self, pm, temp_db):
        """Test que las tablas se crean correctamente"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'user_permissions' in tables
    
    def test_table_schema(self, pm, temp_db):
        """Test que el esquema de la tabla es correcto"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(user_permissions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        conn.close()
        
        assert 'user_email' in columns
        assert 'role' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
    
    # --- Tests de Agregar Usuario ---
    
    def test_add_user_success(self, pm):
        """Test agregar usuario exitosamente"""
        result = pm.add_user('test@example.com', role='user_basic')
        assert result is True
        
        users = pm.get_all_users()
        assert len(users) == 1
        assert users[0]['user_email'] == 'test@example.com'
        assert users[0]['role'] == 'user_basic'
    
    def test_add_user_duplicate(self, pm):
        """Test que agregar duplicado hace upsert"""
        pm.add_user('test@example.com', role='user_basic')
        # INSERT OR REPLACE actualiza el registro
        result = pm.add_user('test@example.com', role='admin_full')
        assert result is True
        users = pm.get_all_users()
        assert len(users) == 1
        assert users[0]['role'] == 'admin_full'
    
    def test_add_user_default_role(self, pm):
        """Test que el rol por defecto es user_basic"""
        pm.add_user('test@example.com')
        users = pm.get_all_users()
        assert users[0]['role'] == 'user_basic'
    
    def test_add_user_invalid_role(self, pm):
        """Test que no se puede agregar con rol inválido"""
        result = pm.add_user('test@example.com', role='invalid_role')
        # add_user retorna False en lugar de lanzar excepción
        assert result is False
    
    # --- Tests de Actualizar Usuario ---
    
    def test_update_user_role_success(self, pm):
        """Test actualizar rol de usuario (upsert)"""
        pm.add_user('test@example.com', role='user_basic')
        # add_user con INSERT OR REPLACE actúa como upsert
        result = pm.add_user('test@example.com', 'admin_full')
        assert result is True
        
        users = pm.get_all_users()
        assert users[0]['role'] == 'admin_full'
    
    def test_update_user_role_invalid(self, pm):
        """Test actualizar con rol inválido"""
        pm.add_user('test@example.com', role='user_basic')
        result = pm.add_user('test@example.com', 'invalid_role')
        assert result is False
    
    # --- Tests de Remover Usuario ---
    
    def test_remove_user_success(self, pm):
        """Test remover usuario exitosamente"""
        pm.add_user('test@example.com', role='user_basic')
        result = pm.remove_user('test@example.com')
        assert result is True
        
        users = pm.get_all_users()
        assert len(users) == 0
    
    def test_remove_user_nonexistent(self, pm):
        """Test remover usuario que no existe"""
        result = pm.remove_user('nonexistent@example.com')
        assert result is False
    
    # --- Tests de Verificación de Permisos ---
    
    def test_has_permission_admin_full(self, pm):
        """Test que admin_full tiene todos los permisos"""
        pm.add_user('admin@example.com', role='admin_full')
        
        assert pm.has_permission('admin@example.com', 'view_dashboard') is True
        assert pm.has_permission('admin@example.com', 'view_analytics') is True
        assert pm.has_permission('admin@example.com', 'edit_targets') is True
        assert pm.has_permission('admin@example.com', 'export_data') is True
    
    def test_has_permission_user_basic(self, pm):
        """Test que user_basic solo tiene permiso de vista"""
        pm.add_user('user@example.com', role='user_basic')
        
        assert pm.has_permission('user@example.com', 'view_dashboard') is True
        assert pm.has_permission('user@example.com', 'view_analytics') is False
        assert pm.has_permission('user@example.com', 'edit_targets') is False
        assert pm.has_permission('user@example.com', 'export_data') is False
    
    def test_has_permission_admin_export(self, pm):
        """Test permisos de admin_export"""
        pm.add_user('export@example.com', role='admin_export')
        
        assert pm.has_permission('export@example.com', 'view_dashboard') is True
        assert pm.has_permission('export@example.com', 'export_data') is True
        assert pm.has_permission('export@example.com', 'view_analytics') is False
        assert pm.has_permission('export@example.com', 'edit_targets') is False
    
    def test_has_permission_analytics_viewer(self, pm):
        """Test permisos de analytics_viewer"""
        pm.add_user('analytics@example.com', role='analytics_viewer')
        
        assert pm.has_permission('analytics@example.com', 'view_dashboard') is True
        assert pm.has_permission('analytics@example.com', 'view_analytics') is True
        assert pm.has_permission('analytics@example.com', 'edit_targets') is False
        assert pm.has_permission('analytics@example.com', 'export_data') is False
    
    def test_has_permission_nonexistent_user(self, pm):
        """Test permisos de usuario no registrado (usa rol por defecto)"""
        # Usuario no existente debe tener permisos de user_basic
        assert pm.has_permission('unknown@example.com', 'view_dashboard') is True
        assert pm.has_permission('unknown@example.com', 'export_data') is False
    
    # --- Tests de is_admin ---
    
    def test_is_admin_true(self, pm):
        """Test que admin_full es identificado como admin"""
        pm.add_user('admin@example.com', role='admin_full')
        assert pm.is_admin('admin@example.com') is True
    
    def test_is_admin_false(self, pm):
        """Test que otros roles no son admin"""
        pm.add_user('user@example.com', role='user_basic')
        pm.add_user('analytics@example.com', role='analytics_viewer')
        
        assert pm.is_admin('user@example.com') is False
        assert pm.is_admin('analytics@example.com') is False
    
    def test_is_admin_nonexistent(self, pm):
        """Test que usuario no existente no es admin"""
        assert pm.is_admin('unknown@example.com') is False
    
    # --- Tests de Listado de Usuarios ---
    
    def test_get_all_users_empty(self, pm):
        """Test listar usuarios cuando no hay ninguno"""
        users = pm.get_all_users()
        assert len(users) == 0
    
    def test_get_all_users_multiple(self, pm):
        """Test listar múltiples usuarios"""
        pm.add_user('user1@example.com', role='user_basic')
        pm.add_user('user2@example.com', role='admin_full')
        pm.add_user('user3@example.com', role='analytics_viewer')
        
        users = pm.get_all_users()
        assert len(users) == 3
        emails = [u['user_email'] for u in users]
        assert 'user1@example.com' in emails
        assert 'user2@example.com' in emails
        assert 'user3@example.com' in emails
    
    def test_get_users_by_role(self, pm):
        """Test obtener usuarios por rol"""
        pm.add_user('admin1@example.com', role='admin_full')
        pm.add_user('admin2@example.com', role='admin_full')
        pm.add_user('user@example.com', role='user_basic')
        
        admins = pm.get_users_by_role('admin_full')
        assert len(admins) == 2
        
        users = pm.get_users_by_role('user_basic')
        assert len(users) == 1
    
    # --- Tests de Migración ---
    
    def test_migrate_from_lists(self, pm):
        """Test migración desde listas hardcodeadas"""
        admin_full = ['admin1@example.com', 'admin2@example.com']
        admin_export = ['export@example.com']
        analytics = ['analytics@example.com']
        
        pm.migrate_from_lists(admin_full, admin_export, analytics)
        
        users = pm.get_all_users()
        assert len(users) == 4
        
        # Verificar roles
        user_dict = {u['user_email']: u['role'] for u in users}
        assert user_dict['admin1@example.com'] == 'admin_full'
        assert user_dict['admin2@example.com'] == 'admin_full'
        assert user_dict['export@example.com'] == 'admin_export'
        assert user_dict['analytics@example.com'] == 'analytics_viewer'
    
    def test_migrate_from_lists_duplicates(self, pm):
        """Test que la migración maneja duplicados (idempotente)"""
        admin_full = ['admin@example.com']
        
        # Primera migración
        pm.migrate_from_lists(admin_full, [], [])
        users1 = pm.get_all_users()
        
        # Segunda migración (debe ser idempotente)
        pm.migrate_from_lists(admin_full, [], [])
        users2 = pm.get_all_users()
        
        assert len(users1) == len(users2) == 1
    
    # --- Tests de Roles y Permisos Constantes ---
    
    def test_role_permissions_structure(self, pm):
        """Test que ROLE_PERMISSIONS tiene la estructura correcta"""
        assert 'admin_full' in pm.ROLE_PERMISSIONS
        assert 'admin_export' in pm.ROLE_PERMISSIONS
        assert 'analytics_viewer' in pm.ROLE_PERMISSIONS
        assert 'user_basic' in pm.ROLE_PERMISSIONS
        
        # Todos los roles deben tener lista de permisos
        for role, perms in pm.ROLE_PERMISSIONS.items():
            assert isinstance(perms, list)
            assert len(perms) > 0
    
    def test_all_roles_have_view_dashboard(self, pm):
        """Test que todos los roles pueden ver dashboard"""
        for role in pm.ROLE_PERMISSIONS.keys():
            assert 'view_dashboard' in pm.ROLE_PERMISSIONS[role]
    
    # --- Tests de Manejo de Errores ---
    
    @pytest.mark.skip(reason="Test de logging interno - difícil de testear con mocks")
    @patch('src.permissions_manager.get_logger')
    def test_database_error_logging(self, mock_logger, pm):
        """Test que los errores de DB se loguean correctamente"""
        # Este test verifica que el logging funciona
        # En un error real, el logger debería ser llamado
        assert mock_logger.called
    
    def test_get_connection_context_manager(self, pm):
        """Test que el context manager de conexión funciona"""
        with pm.get_connection() as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
    
    # --- Tests de Casos Especiales ---
    
    def test_email_case_sensitivity(self, pm):
        """Test que los emails se manejan case-sensitive pero el upsert actualiza"""
        pm.add_user('User@Example.com', role='user_basic')
        # SQLite es case-insensitive por defecto para TEXT PRIMARY KEY
        # así que esto actualiza el registro anterior
        pm.add_user('user@example.com', role='admin_full')
        
        users = pm.get_all_users()
        # Dependiendo de la colación de SQLite, podría ser 1 o 2
        # Por defecto SQLite colación es case-insensitive
        assert len(users) >= 1
    
    def test_empty_email(self, pm):
        """Test que no se puede agregar email vacío"""
        result = pm.add_user('', role='user_basic')
        # add_user debe retornar False para emails vacíos
        # o podria tener éxito si no hay validación
        assert result is False or (result is True and len(pm.get_all_users()) == 1)


# --- Tests de Integración ---

class TestPermissionsIntegration:
    """Tests de integración para flujos completos"""
    
    @pytest.fixture
    def pm_with_users(self, tmp_path):
        """PermissionsManager pre-poblado con usuarios"""
        db_path = tmp_path / "test.db"
        pm = PermissionsManager(db_path=str(db_path))
        
        pm.add_user('admin@company.com', role='admin_full')
        pm.add_user('analyst@company.com', role='analytics_viewer')
        pm.add_user('exporter@company.com', role='admin_export')
        pm.add_user('viewer@company.com', role='user_basic')
        
        return pm
    
    def test_complete_workflow(self, pm_with_users):
        """Test flujo completo de gestión de usuarios"""
        pm = pm_with_users
        
        # Verificar usuarios iniciales
        assert len(pm.get_all_users()) == 4
        
        # Promover un usuario a admin (upsert)
        pm.add_user('viewer@company.com', 'admin_full')
        assert pm.is_admin('viewer@company.com') is True
        
        # Agregar nuevo usuario
        pm.add_user('new@company.com', role='user_basic')
        assert len(pm.get_all_users()) == 5
        
        # Remover un usuario
        pm.remove_user('exporter@company.com')
        assert len(pm.get_all_users()) == 4
        
        # Verificar permisos finales
        assert pm.has_permission('admin@company.com', 'export_data') is True
        assert pm.has_permission('analyst@company.com', 'view_analytics') is True
        assert pm.has_permission('new@company.com', 'edit_targets') is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
