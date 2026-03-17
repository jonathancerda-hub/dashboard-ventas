# Tests Unitarios - Dashboard de Ventas

Suite de tests unitarios para los managers del Dashboard de Ventas Farmacéuticas.

## 📁 Estructura

```
tests/
├── __init__.py
└── unit/
    ├── __init__.py
    ├── test_permissions_manager.py   # Tests de sistema de permisos
    ├── test_supabase_manager.py      # Tests de gestión de metas
    └── test_odoo_manager.py          # Tests de integración Odoo
```

## 🚀 Ejecutar Tests

### Todos los tests

```bash
pytest
```

### Tests de un archivo específico

```bash
pytest tests/unit/test_permissions_manager.py
```

### Tests con cobertura

```bash
pytest --cov=src --cov-report=html
```

### Tests con más detalle

```bash
pytest -v -s
```

### Tests por categoría

```bash
# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Excluir tests lentos
pytest -m "not slow"
```

## 📦 Dependencias

Instalar dependencias de testing:

```bash
pip install pytest pytest-cov pytest-mock
```

## 📊 Cobertura

### test_permissions_manager.py
- ✅ Inicialización y creación de DB
- ✅ CRUD completo (add, update, remove)
- ✅ Verificación de permisos por rol
- ✅ Migración desde listas hardcodeadas
- ✅ Manejo de errores
- **56 tests**

### test_supabase_manager.py
- ✅ CRUD de metas (create, read, update, delete)
- ✅ Filtros por mes y línea comercial
- ✅ Upsert (insert or update)
- ✅ Manejo de errores de conexión
- **33 tests**

### test_odoo_manager.py
- ✅ Obtención de opciones de filtro
- ✅ Consulta de líneas de venta
- ✅ Listado de vendedores
- ✅ Datos apilados de líneas comerciales
- ✅ Manejo de errores y reintentos
- ✅ Validación de datos
- **38 tests**

**Total: 127 tests unitarios**

## 🎯 Cobertura de Código

Los tests cubren:
- ✅ Flujos principales (happy path)
- ✅ Casos de error
- ✅ Validaciones de datos
- ✅ Manejo de valores nulos
- ✅ Casos extremos (edge cases)

## 🔧 Configuración

### pytest.ini

Configuración centralizada en `pytest.ini`:
- Verbose output por defecto
- Markers para categorizar tests
- Filtros de warnings

### Mocks

Los tests usan mocks para:
- **SQLite**: Base de datos temporal en memoria
- **Supabase**: Mock del cliente con MagicMock
- **Odoo**: Mock del cliente JSON-RPC

## 📝 Escribir Nuevos Tests

### Template básico

```python
import pytest
from unittest.mock import Mock, patch

class TestMiModulo:
    """Suite de tests para MiModulo"""
    
    @pytest.fixture
    def mi_instancia(self):
        """Fixture que retorna instancia de prueba"""
        return MiModulo()
    
    def test_mi_funcionalidad(self, mi_instancia):
        """Test de funcionalidad específica"""
        resultado = mi_instancia.mi_metodo()
        assert resultado == esperado
```

### Mejores prácticas

1. **Un test, un concepto**: Cada test verifica una sola cosa
2. **Nombres descriptivos**: `test_create_user_with_invalid_email`
3. **AAA Pattern**: Arrange, Act, Assert
4. **Fixtures reutilizables**: Usar @pytest.fixture
5. **Mocks específicos**: Mockear solo lo necesario

## 🐛 Debugging Tests

### Ver prints en tests

```bash
pytest -s
```

### Detener en primer fallo

```bash
pytest -x
```

### Ver traceback completo

```bash
pytest --tb=long
```

### Modo debug

```bash
pytest --pdb
```

## 📈 Métricas

### Ejecutar con timing

```bash
pytest --durations=10
```

### Verificar tests lentos

```bash
pytest -m slow --durations=0
```

## 🔄 CI/CD

Los tests pueden integrarse en CI/CD:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=src
```

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)

## 🤝 Contribuir

Al agregar nuevo código:
1. Escribir tests ANTES de la implementación (TDD)
2. Mantener cobertura > 80%
3. Ejecutar suite completa antes de commit
4. Documentar casos especiales

## ⚠️ Notas

- Los tests usan bases de datos temporales (no afectan producción)
- Todos los mocks están aislados (no hay llamadas reales a APIs)
- Los fixtures se limpian automáticamente después de cada test
