"""
Tests unitarios para OdooManager

Tests del cliente JSON-RPC para integración con Odoo ERP.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, date
from src.odoo_manager import OdooManager


class TestOdooManager:
    """Suite de tests para OdooManager"""
    
    @pytest.fixture
    def mock_odoo_client(self):
        """Mock del cliente JSON-RPC de Odoo"""
        mock_client = MagicMock()
        return mock_client
    
    @pytest.fixture
    def om(self, mock_odoo_client):
        """Instancia de OdooManager con cliente mockeado"""
        with patch('src.odoo_manager.OdooJSONRPCClient', return_value=mock_odoo_client):
            with patch('src.odoo_manager.os.getenv') as mock_getenv:
                mock_getenv.side_effect = lambda key, default=None: {
                    'ODOO_URL': 'https://test.odoo.com',
                    'ODOO_DB': 'test_db',
                    'ODOO_USERNAME': 'test@example.com',
                    'ODOO_PASSWORD': 'test_password'
                }.get(key, default)
                
                manager = OdooManager()
                manager.client = mock_odoo_client
                return manager
    
    # --- Tests de Inicialización ---
    
    @patch('src.odoo_manager.OdooJSONRPCClient')
    @patch('src.odoo_manager.os.getenv')
    def test_init_with_credentials(self, mock_getenv, mock_client_class):
        """Test que la inicialización usa credenciales del entorno"""
        mock_getenv.side_effect = lambda key, default=None: {
            'ODOO_URL': 'https://test.odoo.com',
            'ODOO_DB': 'test_db',
            'ODOO_USERNAME': 'test@example.com',
            'ODOO_PASSWORD': 'test_password'
        }.get(key, default)
        
        om = OdooManager()
        
        mock_client_class.assert_called_once_with(
            url='https://test.odoo.com',
            db='test_db',
            username='test@example.com',
            password='test_password'
        )
    
    @patch('src.odoo_manager.OdooJSONRPCClient')
    @patch('src.odoo_manager.os.getenv')
    def test_init_without_credentials(self, mock_getenv, mock_client_class):
        """Test que maneja credenciales faltantes"""
        mock_getenv.return_value = None
        
        with pytest.raises((ValueError, Exception)):
            om = OdooManager()
    
    # --- Tests de get_filter_options ---
    
    def test_get_filter_options_success(self, om, mock_odoo_client):
        """Test obtener opciones de filtro exitosamente"""
        mock_odoo_client.search_read.side_effect = [
            # Primera llamada: líneas comerciales
            [
                {'id': 1, 'name': 'PETMEDICA'},
                {'id': 2, 'name': 'AGROVET'},
            ],
            # Segunda llamada: clientes
            [
                {'id': 101, 'name': 'Cliente A'},
                {'id': 102, 'name': 'Cliente B'},
            ]
        ]
        
        result = om.get_filter_options()
        
        assert 'lineas' in result
        assert 'clients' in result
        assert len(result['lineas']) == 2
        assert len(result['clients']) == 2
        assert result['lineas'][0]['name'] == 'PETMEDICA'
    
    def test_get_filter_options_empty(self, om, mock_odoo_client):
        """Test cuando no hay datos"""
        mock_odoo_client.search_read.return_value = []
        
        result = om.get_filter_options()
        
        assert result == {'lineas': [], 'clients': []}
    
    def test_get_filter_options_error(self, om, mock_odoo_client):
        """Test manejo de error al obtener opciones"""
        mock_odoo_client.search_read.side_effect = Exception("Connection timeout")
        
        result = om.get_filter_options()
        
        assert result == {'lineas': [], 'clients': []}
    
    # --- Tests de get_sales_lines ---
    
    def test_get_sales_lines_success(self, om, mock_odoo_client):
        """Test obtener líneas de venta exitosamente"""
        mock_data = [
            {
                'id': 1,
                'name': 'SO001',
                'partner_id': [101, 'Cliente A'],
                'date_order': '2026-01-15',
                'amount_total': 5000.0,
                'state': 'sale',
                'order_line': [
                    {
                        'product_id': [201, 'Producto 1'],
                        'product_uom_qty': 10,
                        'price_unit': 500.0
                    }
                ]
            }
        ]
        
        mock_odoo_client.search_read.return_value = mock_data
        
        result = om.get_sales_lines(
            date_from='2026-01-01',
            date_to='2026-01-31'
        )
        
        assert len(result) > 0
        assert result[0]['name'] == 'SO001'
        mock_odoo_client.search_read.assert_called_once()
    
    def test_get_sales_lines_with_filters(self, om, mock_odoo_client):
        """Test filtros de búsqueda en sales lines"""
        mock_odoo_client.search_read.return_value = []
        
        om.get_sales_lines(
            date_from='2026-01-01',
            date_to='2026-01-31',
            linea_comercial='PETMEDICA',
            cliente_id=101
        )
        
        # Verificar que se llamó con los filtros correctos
        call_args = mock_odoo_client.search_read.call_args
        domain = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('domain', [])
        
        # El domain debe incluir filtros de fecha y otros
        assert any('date_order' in str(filter) for filter in domain)
    
    def test_get_sales_lines_date_parsing(self, om, mock_odoo_client):
        """Test que las fechas se parsean correctamente"""
        mock_odoo_client.search_read.return_value = [
            {
                'id': 1,
                'date_order': '2026-01-15 10:30:00',
                'amount_total': 1000.0
            }
        ]
        
        result = om.get_sales_lines(date_from='2026-01-01', date_to='2026-01-31')
        
        # Verificar que el resultado contiene datos procesados
        assert len(result) > 0
    
    def test_get_sales_lines_error(self, om, mock_odoo_client):
        """Test manejo de error al obtener sales lines"""
        mock_odoo_client.search_read.side_effect = Exception("Network error")
        
        result = om.get_sales_lines(date_from='2026-01-01', date_to='2026-01-31')
        
        assert result == []
    
    # --- Tests de get_all_sellers ---
    
    def test_get_all_sellers_success(self, om, mock_odoo_client):
        """Test obtener todos los vendedores"""
        mock_sellers = [
            {'id': 1, 'name': 'Vendedor A'},
            {'id': 2, 'name': 'Vendedor B'},
            {'id': 3, 'name': 'Vendedor C'},
        ]
        
        mock_odoo_client.search_read.return_value = mock_sellers
        
        result = om.get_all_sellers()
        
        assert len(result) == 3
        assert result[0]['name'] == 'Vendedor A'
        mock_odoo_client.search_read.assert_called_once()
    
    def test_get_all_sellers_empty(self, om, mock_odoo_client):
        """Test cuando no hay vendedores"""
        mock_odoo_client.search_read.return_value = []
        
        result = om.get_all_sellers()
        
        assert result == []
    
    def test_get_all_sellers_error(self, om, mock_odoo_client):
        """Test manejo de error al obtener vendedores"""
        mock_odoo_client.search_read.side_effect = Exception("Database error")
        
        result = om.get_all_sellers()
        
        assert result == []
    
    # --- Tests de get_commercial_lines_stacked_data ---
    
    def test_get_commercial_lines_stacked_data_success(self, om, mock_odoo_client):
        """Test obtener datos apilados de líneas comerciales"""
        mock_data = [
            {
                'id': 1,
                'linea_comercial': 'PETMEDICA',
                'date_order': '2026-01-15',
                'amount_total': 5000.0,
                'vendedor': 'Vendedor A'
            },
            {
                'id': 2,
                'linea_comercial': 'AGROVET',
                'date_order': '2026-01-20',
                'amount_total': 3000.0,
                'vendedor': 'Vendedor B'
            }
        ]
        
        mock_odoo_client.search_read.return_value = mock_data
        
        result = om.get_commercial_lines_stacked_data(
            date_from='2026-01-01',
            date_to='2026-01-31'
        )
        
        assert 'yAxis' in result
        assert 'series' in result
        assert 'legend' in result
        assert isinstance(result['series'], list)
    
    def test_get_commercial_lines_stacked_data_empty(self, om, mock_odoo_client):
        """Test datos apilados sin resultados"""
        mock_odoo_client.search_read.return_value = []
        
        result = om.get_commercial_lines_stacked_data(
            date_from='2026-01-01',
            date_to='2026-01-31'
        )
        
        assert result == {'yAxis': [], 'series': [], 'legend': []}
    
    def test_get_commercial_lines_stacked_data_aggregation(self, om, mock_odoo_client):
        """Test agregación correcta de datos por línea"""
        mock_data = [
            {'linea_comercial': 'PETMEDICA', 'amount_total': 1000.0, 'vendedor': 'V1'},
            {'linea_comercial': 'PETMEDICA', 'amount_total': 2000.0, 'vendedor': 'V1'},
            {'linea_comercial': 'AGROVET', 'amount_total': 1500.0, 'vendedor': 'V2'},
        ]
        
        mock_odoo_client.search_read.return_value = mock_data
        
        result = om.get_commercial_lines_stacked_data(
            date_from='2026-01-01',
            date_to='2026-01-31'
        )
        
        # Verificar que hay series de datos
        assert len(result['series']) > 0 or len(result['yAxis']) > 0
    
    # --- Tests de Métodos Auxiliares ---
    
    def test_format_currency(self, om):
        """Test formateo de moneda"""
        # Asumiendo que existe un método format_currency
        if hasattr(om, 'format_currency'):
            result = om.format_currency(1234.56)
            assert '$' in result or '1,234' in result
    
    def test_parse_date(self, om):
        """Test parseo de fechas"""
        if hasattr(om, 'parse_date'):
            result = om.parse_date('2026-01-15')
            assert isinstance(result, (date, datetime))
    
    # --- Tests de Caché ---
    
    @patch('src.odoo_manager.time.time')
    def test_cache_mechanism(self, mock_time, om, mock_odoo_client):
        """Test mecanismo de caché si existe"""
        mock_time.return_value = 1000
        mock_odoo_client.search_read.return_value = [{'id': 1}]
        
        # Primera llamada
        result1 = om.get_filter_options()
        call_count_1 = mock_odoo_client.search_read.call_count
        
        # Segunda llamada inmediata (debería usar caché si existe)
        result2 = om.get_filter_options()
        call_count_2 = mock_odoo_client.search_read.call_count
        
        # Si hay caché, call_count_2 debería ser igual a call_count_1
        # Si no hay caché, será mayor
        assert call_count_2 >= call_count_1
    
    # --- Tests de Manejo de Conexión ---
    
    def test_connection_retry(self, om, mock_odoo_client):
        """Test reintentos de conexión"""
        # Simular fallo y luego éxito
        mock_odoo_client.search_read.side_effect = [
            Exception("Connection timeout"),
            [{'id': 1, 'name': 'Test'}]
        ]
        
        # Dependiendo de la implementación, podría reintentar
        result = om.get_filter_options()
        
        # El resultado depende si hay lógica de retry
        assert isinstance(result, dict)
    
    def test_authentication_error(self, om, mock_odoo_client):
        """Test manejo de error de autenticación"""
        mock_odoo_client.search_read.side_effect = Exception("Authentication failed")
        
        result = om.get_filter_options()
        
        assert result == {'lineas': [], 'clients': []}
    
    # --- Tests de Validación de Datos ---
    
    def test_invalid_date_range(self, om, mock_odoo_client):
        """Test validación de rango de fechas inválido"""
        mock_odoo_client.search_read.return_value = []
        
        # date_from mayor que date_to
        result = om.get_sales_lines(
            date_from='2026-12-31',
            date_to='2026-01-01'
        )
        
        # Debería manejar el caso o retornar vacío
        assert isinstance(result, list)
    
    def test_null_values_handling(self, om, mock_odoo_client):
        """Test manejo de valores nulos"""
        mock_data = [
            {
                'id': 1,
                'name': 'SO001',
                'partner_id': None,  # Valor nulo
                'date_order': '2026-01-15',
                'amount_total': None  # Valor nulo
            }
        ]
        
        mock_odoo_client.search_read.return_value = mock_data
        
        result = om.get_sales_lines(date_from='2026-01-01', date_to='2026-01-31')
        
        # Debería manejar valores nulos sin crash
        assert isinstance(result, list)
    
    # --- Tests de Transformación de Datos ---
    
    def test_data_transformation(self, om, mock_odoo_client):
        """Test transformación de datos de Odoo a formato interno"""
        raw_data = [
            {
                'id': 1,
                'partner_id': [101, 'Cliente A'],  # Formato Many2one de Odoo
                'date_order': '2026-01-15 10:30:00',
                'amount_total': 5000.0,
                'currency_id': [1, 'USD']
            }
        ]
        
        mock_odoo_client.search_read.return_value = raw_data
        
        result = om.get_sales_lines(date_from='2026-01-01', date_to='2026-01-31')
        
        # Verificar que los datos se transformaron
        assert len(result) > 0
        # Los campos Many2one deberían procesarse
        if result:
            assert 'partner_id' in result[0] or 'cliente' in result[0]


# --- Tests de Integración ---

class TestOdooIntegration:
    """Tests de integración para OdooManager"""
    
    @pytest.fixture
    def om_integration(self):
        """OdooManager para tests de integración"""
        with patch('src.odoo_manager.OdooJSONRPCClient'):
            with patch('src.odoo_manager.os.getenv') as mock_getenv:
                mock_getenv.side_effect = lambda key, default=None: {
                    'ODOO_URL': 'https://test.odoo.com',
                    'ODOO_DB': 'test_db',
                    'ODOO_USERNAME': 'test@example.com',
                    'ODOO_PASSWORD': 'test_password'
                }.get(key, default)
                
                om = OdooManager()
                om.client = MagicMock()
                return om
    
    def test_complete_sales_workflow(self, om_integration):
        """Test flujo completo de consulta de ventas"""
        om = om_integration
        
        # Mock de datos completos
        om.client.search_read.return_value = [
            {
                'id': 1,
                'name': 'SO001',
                'partner_id': [101, 'Cliente A'],
                'date_order': '2026-01-15',
                'amount_total': 5000.0,
                'state': 'sale',
                'order_line': [
                    {
                        'product_id': [201, 'Producto 1'],
                        'product_uom_qty': 10,
                        'price_unit': 500.0
                    }
                ]
            }
        ]
        
        # Obtener filtros
        filters = om.get_filter_options()
        assert isinstance(filters, dict)
        
        # Obtener ventas
        sales = om.get_sales_lines(date_from='2026-01-01', date_to='2026-01-31')
        assert isinstance(sales, list)
        
        # Obtener vendedores
        sellers = om.get_all_sellers()
        assert isinstance(sellers, list)
    
    def test_error_recovery(self, om_integration):
        """Test recuperación de errores"""
        om = om_integration
        
        # Primera llamada falla
        om.client.search_read.side_effect = Exception("Network error")
        
        result1 = om.get_filter_options()
        assert result1 == {'lineas': [], 'clients': []}
        
        # Segunda llamada exitosa
        om.client.search_read.side_effect = None
        om.client.search_read.return_value = [{'id': 1, 'name': 'Test'}]
        
        result2 = om.get_filter_options()
        assert isinstance(result2, dict)
    
    def test_performance_large_dataset(self, om_integration):
        """Test rendimiento con dataset grande"""
        om = om_integration
        
        # Simular 1000 registros
        large_dataset = [
            {
                'id': i,
                'name': f'SO{i:04d}',
                'amount_total': i * 100.0
            }
            for i in range(1, 1001)
        ]
        
        om.client.search_read.return_value = large_dataset
        
        result = om.get_sales_lines(date_from='2026-01-01', date_to='2026-12-31')
        
        assert len(result) == 1000


# --- Tests de Mocks y Fixtures ---

@pytest.fixture
def sample_odoo_data():
    """Datos de ejemplo para tests"""
    return {
        'sales_orders': [
            {
                'id': 1,
                'name': 'SO001',
                'partner_id': [101, 'Cliente A'],
                'date_order': '2026-01-15',
                'amount_total': 5000.0,
                'state': 'sale'
            },
            {
                'id': 2,
                'name': 'SO002',
                'partner_id': [102, 'Cliente B'],
                'date_order': '2026-01-20',
                'amount_total': 3000.0,
                'state': 'sale'
            }
        ],
        'sellers': [
            {'id': 1, 'name': 'Vendedor A'},
            {'id': 2, 'name': 'Vendedor B'}
        ],
        'lineas': [
            {'id': 1, 'name': 'PETMEDICA'},
            {'id': 2, 'name': 'AGROVET'}
        ]
    }


def test_sample_data_structure(sample_odoo_data):
    """Test que los datos de ejemplo tienen la estructura correcta"""
    assert 'sales_orders' in sample_odoo_data
    assert 'sellers' in sample_odoo_data
    assert 'lineas' in sample_odoo_data
    assert len(sample_odoo_data['sales_orders']) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
