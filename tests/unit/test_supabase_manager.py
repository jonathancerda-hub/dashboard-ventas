"""
Tests unitarios para SupabaseManager

Tests de la gestión de metas de ventas en Supabase.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from src.supabase_manager import SupabaseManager


class TestSupabaseManager:
    """Suite de tests para SupabaseManager"""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock del cliente de Supabase"""
        mock_client = MagicMock()
        return mock_client
    
    @pytest.fixture
    def sm(self, mock_supabase_client):
        """Instancia de SupabaseManager con cliente mockeado"""
        with patch('src.supabase_manager.create_client', return_value=mock_supabase_client):
            manager = SupabaseManager()
            manager.supabase = mock_supabase_client
            return manager
    
    # --- Tests de Inicialización ---
    
    @patch('src.supabase_manager.create_client')
    @patch('src.supabase_manager.os.getenv')
    def test_init_with_credentials(self, mock_getenv, mock_create_client):
        """Test que la inicialización usa las credenciales del entorno"""
        mock_getenv.side_effect = lambda key, default=None: {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test-key-123'
        }.get(key, default)
        
        sm = SupabaseManager()
        
        mock_create_client.assert_called_once_with(
            'https://test.supabase.co',
            'test-key-123'
        )
    
    @patch('src.supabase_manager.create_client')
    @patch('src.supabase_manager.os.getenv')
    def test_init_without_credentials(self, mock_getenv, mock_create_client):
        """Test que la inicialización maneja credenciales faltantes"""
        mock_getenv.return_value = None
        
        # Debería lanzar error o manejar la falta de credenciales
        with pytest.raises((ValueError, Exception)):
            sm = SupabaseManager()
    
    # --- Tests de CREATE (create_meta) ---
    
    def test_create_meta_success(self, sm, mock_supabase_client):
        """Test crear meta exitosamente"""
        meta_data = {
            'mes': '2026-01',
            'linea_comercial': 'PETMEDICA',
            'meta_dolares': 100000.0,
            'meta_ipn_dolares': 50000.0
        }
        
        # Mock de la respuesta
        mock_response = MagicMock()
        mock_response.data = [{'id': 1, **meta_data}]
        mock_supabase_client.table().insert().execute.return_value = mock_response
        
        result = sm.create_meta(meta_data)
        
        assert result is True
        mock_supabase_client.table.assert_called_with('metas_2026')
        mock_supabase_client.table().insert.assert_called_once()
    
    def test_create_meta_validation_missing_fields(self, sm):
        """Test que create_meta valida campos requeridos"""
        incomplete_data = {
            'mes': '2026-01',
            # Falta linea_comercial
        }
        
        result = sm.create_meta(incomplete_data)
        assert result is False
    
    def test_create_meta_validation_invalid_month(self, sm):
        """Test validación de formato de mes"""
        invalid_data = {
            'mes': 'invalid-month',
            'linea_comercial': 'PETMEDICA',
            'meta_dolares': 100000.0,
            'meta_ipn_dolares': 50000.0
        }
        
        result = sm.create_meta(invalid_data)
        assert result is False
    
    def test_create_meta_error_handling(self, sm, mock_supabase_client):
        """Test manejo de errores al crear meta"""
        meta_data = {
            'mes': '2026-01',
            'linea_comercial': 'PETMEDICA',
            'meta_dolares': 100000.0,
            'meta_ipn_dolares': 50000.0
        }
        
        # Mock de error
        mock_supabase_client.table().insert().execute.side_effect = Exception("Database error")
        
        result = sm.create_meta(meta_data)
        assert result is False
    
    # --- Tests de READ (read_metas) ---
    
    def test_read_metas_success(self, sm, mock_supabase_client):
        """Test leer todas las metas"""
        mock_data = [
            {'id': 1, 'mes': '2026-01', 'linea_comercial': 'PETMEDICA', 'meta_dolares': 100000},
            {'id': 2, 'mes': '2026-01', 'linea_comercial': 'AGROVET', 'meta_dolares': 80000},
        ]
        
        mock_response = MagicMock()
        mock_response.data = mock_data
        mock_supabase_client.table().select().execute.return_value = mock_response
        
        result = sm.read_metas()
        
        assert len(result) == 2
        assert result[0]['linea_comercial'] == 'PETMEDICA'
        assert result[1]['linea_comercial'] == 'AGROVET'
    
    def test_read_metas_empty(self, sm, mock_supabase_client):
        """Test leer cuando no hay metas"""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase_client.table().select().execute.return_value = mock_response
        
        result = sm.read_metas()
        
        assert len(result) == 0
        assert result == []
    
    def test_read_metas_error(self, sm, mock_supabase_client):
        """Test manejo de error al leer metas"""
        mock_supabase_client.table().select().execute.side_effect = Exception("Connection error")
        
        result = sm.read_metas()
        
        assert result == []
    
    # --- Tests de UPDATE (update_meta) ---
    
    def test_update_meta_success(self, sm, mock_supabase_client):
        """Test actualizar meta exitosamente"""
        meta_id = 1
        update_data = {
            'meta_dolares': 120000.0,
            'meta_ipn_dolares': 60000.0
        }
        
        mock_response = MagicMock()
        mock_response.data = [{'id': meta_id, **update_data}]
        mock_supabase_client.table().update().eq().execute.return_value = mock_response
        
        result = sm.update_meta(meta_id, update_data)
        
        assert result is True
        mock_supabase_client.table().update.assert_called_once_with(update_data)
    
    def test_update_meta_not_found(self, sm, mock_supabase_client):
        """Test actualizar meta que no existe"""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase_client.table().update().eq().execute.return_value = mock_response
        
        result = sm.update_meta(999, {'meta_dolares': 100000})
        
        assert result is False
    
    def test_update_meta_error(self, sm, mock_supabase_client):
        """Test manejo de error al actualizar"""
        mock_supabase_client.table().update().eq().execute.side_effect = Exception("Update failed")
        
        result = sm.update_meta(1, {'meta_dolares': 100000})
        
        assert result is False
    
    # --- Tests de DELETE (delete_meta) ---
    
    def test_delete_meta_success(self, sm, mock_supabase_client):
        """Test eliminar meta exitosamente"""
        meta_id = 1
        
        mock_response = MagicMock()
        mock_response.data = [{'id': meta_id}]
        mock_supabase_client.table().delete().eq().execute.return_value = mock_response
        
        result = sm.delete_meta(meta_id)
        
        assert result is True
        mock_supabase_client.table().delete.assert_called_once()
    
    def test_delete_meta_not_found(self, sm, mock_supabase_client):
        """Test eliminar meta que no existe"""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase_client.table().delete().eq().execute.return_value = mock_response
        
        result = sm.delete_meta(999)
        
        assert result is False
    
    def test_delete_meta_error(self, sm, mock_supabase_client):
        """Test manejo de error al eliminar"""
        mock_supabase_client.table().delete().eq().execute.side_effect = Exception("Delete failed")
        
        result = sm.delete_meta(1)
        
        assert result is False
    
    # --- Tests de get_metas_by_filters ---
    
    def test_get_metas_by_filters_mes(self, sm, mock_supabase_client):
        """Test filtrar metas por mes"""
        mock_data = [
            {'id': 1, 'mes': '2026-01', 'linea_comercial': 'PETMEDICA'},
        ]
        
        mock_response = MagicMock()
        mock_response.data = mock_data
        mock_supabase_client.table().select().eq().execute.return_value = mock_response
        
        result = sm.get_metas_by_filters(mes='2026-01')
        
        assert len(result) == 1
        assert result[0]['mes'] == '2026-01'
        mock_supabase_client.table().select().eq.assert_called_with('mes', '2026-01')
    
    def test_get_metas_by_filters_linea(self, sm, mock_supabase_client):
        """Test filtrar metas por línea comercial"""
        mock_data = [
            {'id': 1, 'mes': '2026-01', 'linea_comercial': 'PETMEDICA'},
        ]
        
        mock_response = MagicMock()
        mock_response.data = mock_data
        mock_supabase_client.table().select().eq().execute.return_value = mock_response
        
        result = sm.get_metas_by_filters(linea_comercial='PETMEDICA')
        
        assert len(result) == 1
        assert result[0]['linea_comercial'] == 'PETMEDICA'
    
    def test_get_metas_by_filters_multiple(self, sm, mock_supabase_client):
        """Test filtrar con múltiples condiciones"""
        mock_data = [
            {'id': 1, 'mes': '2026-01', 'linea_comercial': 'PETMEDICA'},
        ]
        
        mock_response = MagicMock()
        mock_response.data = mock_data
        
        # Mock de encadenamiento de filtros
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase_client.table().select.return_value = mock_query
        
        result = sm.get_metas_by_filters(mes='2026-01', linea_comercial='PETMEDICA')
        
        assert len(result) == 1
    
    def test_get_metas_by_filters_no_results(self, sm, mock_supabase_client):
        """Test filtrar sin resultados"""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase_client.table().select().eq().execute.return_value = mock_response
        
        result = sm.get_metas_by_filters(mes='2099-12')
        
        assert len(result) == 0
    
    # --- Tests de get_meta_by_mes_linea ---
    
    def test_get_meta_by_mes_linea_found(self, sm, mock_supabase_client):
        """Test obtener meta específica por mes y línea"""
        mock_data = [
            {'id': 1, 'mes': '2026-01', 'linea_comercial': 'PETMEDICA', 'meta_dolares': 100000},
        ]
        
        mock_response = MagicMock()
        mock_response.data = mock_data
        
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase_client.table().select.return_value = mock_query
        
        result = sm.get_meta_by_mes_linea('2026-01', 'PETMEDICA')
        
        assert result is not None
        assert result['meta_dolares'] == 100000
    
    def test_get_meta_by_mes_linea_not_found(self, sm, mock_supabase_client):
        """Test cuando no se encuentra la meta"""
        mock_response = MagicMock()
        mock_response.data = []
        
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        mock_supabase_client.table().select.return_value = mock_query
        
        result = sm.get_meta_by_mes_linea('2099-12', 'INEXISTENTE')
        
        assert result is None
    
    # --- Tests de upsert_meta ---
    
    def test_upsert_meta_insert(self, sm, mock_supabase_client):
        """Test upsert cuando la meta no existe (insert)"""
        meta_data = {
            'mes': '2026-01',
            'linea_comercial': 'PETMEDICA',
            'meta_dolares': 100000.0
        }
        
        # Mock: primero no encuentra la meta
        mock_response_select = MagicMock()
        mock_response_select.data = []
        
        # Mock: luego inserta exitosamente
        mock_response_insert = MagicMock()
        mock_response_insert.data = [{'id': 1, **meta_data}]
        
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.side_effect = [mock_response_select, mock_response_insert]
        
        mock_supabase_client.table().select.return_value = mock_query
        mock_supabase_client.table().insert().execute.return_value = mock_response_insert
        
        result = sm.upsert_meta(meta_data)
        
        assert result is True
    
    def test_upsert_meta_update(self, sm, mock_supabase_client):
        """Test upsert cuando la meta existe (update)"""
        meta_data = {
            'mes': '2026-01',
            'linea_comercial': 'PETMEDICA',
            'meta_dolares': 120000.0
        }
        
        # Mock: encuentra la meta existente
        mock_response_select = MagicMock()
        mock_response_select.data = [{'id': 1, 'meta_dolares': 100000.0}]
        
        # Mock: actualiza exitosamente
        mock_response_update = MagicMock()
        mock_response_update.data = [{'id': 1, **meta_data}]
        
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response_select
        
        mock_supabase_client.table().select.return_value = mock_query
        mock_supabase_client.table().update().eq().execute.return_value = mock_response_update
        
        result = sm.upsert_meta(meta_data)
        
        assert result is True


# --- Tests de Integración ---

class TestSupabaseIntegration:
    """Tests de integración para flujos completos"""
    
    @pytest.fixture
    def sm_integration(self):
        """SupabaseManager para tests de integración"""
        with patch('src.supabase_manager.create_client'):
            sm = SupabaseManager()
            sm.supabase = MagicMock()
            return sm
    
    def test_crud_workflow(self, sm_integration):
        """Test flujo completo CRUD"""
        sm = sm_integration
        
        # Mock de respuestas exitosas
        mock_response = MagicMock()
        mock_response.data = [{'id': 1, 'mes': '2026-01'}]
        sm.supabase.table().insert().execute.return_value = mock_response
        sm.supabase.table().select().execute.return_value = mock_response
        sm.supabase.table().update().eq().execute.return_value = mock_response
        sm.supabase.table().delete().eq().execute.return_value = mock_response
        
        # CREATE
        meta_data = {'mes': '2026-01', 'linea_comercial': 'TEST', 'meta_dolares': 1000}
        assert sm.create_meta(meta_data) is True
        
        # READ
        metas = sm.read_metas()
        assert len(metas) > 0
        
        # UPDATE
        assert sm.update_meta(1, {'meta_dolares': 2000}) is True
        
        # DELETE
        assert sm.delete_meta(1) is True
    
    def test_batch_operations(self, sm_integration):
        """Test operaciones por lotes"""
        sm = sm_integration
        
        # Mock de respuesta
        mock_response = MagicMock()
        mock_response.data = [
            {'id': i, 'mes': '2026-01', 'linea_comercial': f'LINE{i}'}
            for i in range(1, 6)
        ]
        sm.supabase.table().select().execute.return_value = mock_response
        
        metas = sm.read_metas()
        
        assert len(metas) == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
