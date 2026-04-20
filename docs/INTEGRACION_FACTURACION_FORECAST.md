# 📊 Integración de Datos de Facturación para Forecast de Demanda

## 🎯 Objetivo

Este documento describe cómo conectarse a los datos de facturación del Dashboard de Ventas para integrarlos en un modelo de **forecast de demanda de ventas locales** y calcular el **MAPE (Mean Absolute Percentage Error)** para medir la precisión del pronóstico.

---

## 📐 Contexto del Proyecto

### Sistema Actual
- **Backend:** Flask 3.1.3 + Python 3.13.7
- **ERP:** Odoo (XML-RPC / JSON-RPC)
- **Base de Datos:** Supabase PostgreSQL (para analytics y permisos)
- **Odoo Database:** Base de datos empresarial con módulos de ventas y contabilidad

### Flujo de Datos
```
┌─────────────────┐
│  Odoo ERP       │
│  (Facturación)  │
└────────┬────────┘
         │ XML-RPC / JSON-RPC
         ↓
┌─────────────────┐       ┌──────────────────┐
│ OdooManager     │ ───→  │ Modelo Forecast  │
│ (Extractor)     │       │ (Tu desarrollo)  │
└─────────────────┘       └────────┬─────────┘
                                   │
                                   ↓
                          ┌─────────────────┐
                          │ Cálculo MAPE    │
                          │ (Validación)    │
                          └─────────────────┘
```

---

## 🗄️ Estructura de Datos de Facturación en Odoo

### Modelos Principales

#### 1. `account.move` (Facturas - Cabecera)
Representa el documento contable completo (factura, nota de crédito, etc.)

```python
{
    'id': 12345,
    'name': 'FACT/2026/0001',  # Número de factura
    'move_type': 'out_invoice',  # Tipo: out_invoice (venta) o out_refund (nota crédito)
    'state': 'posted',  # Estado: draft, posted, cancel
    'invoice_date': '2026-04-10',  # Fecha de factura ⭐ IMPORTANTE
    'invoice_user_id': [123, 'Juan Pérez'],  # Vendedor
    'partner_id': [456, 'Cliente ABC'],  # Cliente
    'amount_total': 1500.00,  # Total factura
    'invoice_origin': 'SO123',  # Orden de venta origen
    'journal_id': [1, 'Ventas'],  # Diario contable
    'payment_state': 'paid'  # Estado de pago
}
```

#### 2. `account.move.line` (Líneas de Factura - Detalle)
Representa cada producto/servicio dentro de la factura

```python
{
    'id': 98765,
    'move_id': [12345, 'FACT/2026/0001'],  # Referencia a la factura
    'product_id': [789, 'Paracetamol 500mg'],  # Producto ⭐ IMPORTANTE
    'quantity': 100.0,  # Cantidad vendida ⭐ IMPORTANTE
    'price_unit': 10.50,  # Precio unitario
    'balance': -1050.00,  # Total línea (negativo para ventas)
    'partner_id': [456, 'Cliente ABC'],  # Cliente
    'move_name': 'FACT/2026/0001'  # Número de factura
}
```

#### 3. `product.product` (Productos)
Metadatos del producto farmacéutico

```python
{
    'id': 789,
    'name': 'Paracetamol 500mg',
    'default_code': 'PARA-500',  # SKU/Código ⭐ IMPORTANTE
    'categ_id': [50, 'Analgésicos'],  # Categoría
    'commercial_line_national_id': [10, 'Linea Humano'],  # Línea comercial
    'pharmacological_classification_id': [20, 'Analgésico'],
    'pharmaceutical_forms_id': [30, 'Tableta'],
    'administration_way_id': [40, 'Oral']
}
```

---

## 🔌 Configuración de Conexión

### Variables de Entorno (`.env`)

```bash
# Credenciales de Odoo
ODOO_URL=https://tu-empresa.odoo.com
ODOO_DB=nombre_base_datos
ODOO_USER=usuario@empresa.com
ODOO_PASSWORD=tu_password_seguro
ODOO_RPC_TIMEOUT=30
```

### Instalación de Dependencias

```bash
pip install requests pandas python-dotenv
```

---

## 💻 Código de Extracción de Facturación

### Script Completo: `extraer_facturacion_forecast.py`

```python
#!/usr/bin/env python3
"""
Extractor de Datos de Facturación para Modelos de Forecast
Extrae ventas históricas de Odoo para cálculo de MAPE
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class OdooFacturacionExtractor:
    """Extrae datos de facturación desde Odoo para forecasting"""
    
    def __init__(self):
        # Cargar credenciales
        self.url = os.getenv('ODOO_URL')
        self.db = os.getenv('ODOO_DB')
        self.username = os.getenv('ODOO_USER')
        self.password = os.getenv('ODOO_PASSWORD')
        self.timeout = int(os.getenv('ODOO_RPC_TIMEOUT', '30'))
        
        # Validar credenciales
        if not all([self.url, self.db, self.username, self.password]):
            raise ValueError("Faltan credenciales de Odoo en .env")
        
        self.jsonrpc_url = f"{self.url}/jsonrpc"
        self.uid = None
        self._authenticate()
    
    def _authenticate(self):
        """Autenticación con Odoo"""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [self.db, self.username, self.password, {}]
            },
            "id": 1
        }
        
        response = requests.post(
            self.jsonrpc_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout
        )
        
        result = response.json()
        if result.get('result'):
            self.uid = result['result']
            print(f"✅ Autenticado correctamente. UID: {self.uid}")
        else:
            raise Exception(f"Error de autenticación: {result.get('error')}")
    
    def _execute_kw(self, model, method, args, kwargs=None):
        """Ejecuta llamada XML-RPC a Odoo"""
        if kwargs is None:
            kwargs = {}
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [self.db, self.uid, self.password, model, method, args, kwargs]
            },
            "id": 1
        }
        
        response = requests.post(
            self.jsonrpc_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout
        )
        
        result = response.json()
        if 'error' in result:
            raise Exception(f"Error en Odoo: {result['error']}")
        
        return result.get('result')
    
    def extraer_ventas_historicas(self, date_from, date_to, 
                                   excluir_notas_credito=True,
                                   excluir_categorias=None):
        """
        Extrae ventas históricas desde Odoo para forecast
        
        Args:
            date_from (str): Fecha inicio 'YYYY-MM-DD'
            date_to (str): Fecha fin 'YYYY-MM-DD'
            excluir_notas_credito (bool): Si True, solo facturas de venta
            excluir_categorias (list): IDs de categorías a excluir
        
        Returns:
            pandas.DataFrame: Ventas históricas con columnas:
                - fecha: Fecha de factura
                - producto_id: ID del producto
                - producto_codigo: SKU del producto
                - producto_nombre: Nombre del producto
                - cantidad: Unidades vendidas
                - precio_unitario: Precio por unidad
                - total_linea: Total de la línea (abs)
                - cliente_id: ID del cliente
                - cliente_nombre: Nombre del cliente
                - vendedor_id: ID del vendedor
                - vendedor_nombre: Nombre del vendedor
                - factura_numero: Número de factura
                - linea_comercial: Línea comercial del producto
        """
        print(f"📊 Extrayendo ventas desde {date_from} hasta {date_to}...")
        
        # Construir dominio de filtro
        domain = [
            ('move_id.state', '=', 'posted'),  # Solo facturas contabilizadas
            ('move_id.invoice_date', '>=', date_from),
            ('move_id.invoice_date', '<=', date_to),
            ('product_id', '!=', False),  # Solo líneas con producto
            ('product_id.default_code', '!=', False)  # Solo productos con SKU
        ]
        
        # Filtrar tipo de documento
        if excluir_notas_credito:
            domain.append(('move_id.move_type', '=', 'out_invoice'))
        else:
            domain.append(('move_id.move_type', 'in', ['out_invoice', 'out_refund']))
        
        # Excluir categorías específicas (ej: servicios, muestras)
        if excluir_categorias:
            domain.append(('product_id.categ_id', 'not in', excluir_categorias))
        
        # Obtener líneas de factura
        print("🔍 Consultando account.move.line...")
        lines = self._execute_kw(
            'account.move.line',
            'search_read',
            [domain],
            {
                'fields': [
                    'move_id', 'product_id', 'quantity', 'price_unit', 
                    'balance', 'partner_id', 'move_name'
                ],
                'limit': 100000,  # Ajustar según volumen de datos
                'context': {'lang': 'es_PE'}
            }
        )
        
        print(f"✅ {len(lines)} líneas de factura obtenidas")
        
        if not lines:
            return pd.DataFrame()
        
        # Extraer IDs únicos para consultas relacionadas
        move_ids = list(set([line['move_id'][0] for line in lines]))
        product_ids = list(set([line['product_id'][0] for line in lines]))
        
        # Obtener datos de facturas (fechas, vendedores)
        print("🔍 Consultando account.move (facturas)...")
        moves = self._execute_kw(
            'account.move',
            'search_read',
            [[('id', 'in', move_ids)]],
            {
                'fields': ['invoice_date', 'invoice_user_id', 'name'],
                'context': {'lang': 'es_PE'}
            }
        )
        move_data = {m['id']: m for m in moves}
        
        # Obtener datos de productos
        print("🔍 Consultando product.product...")
        products = self._execute_kw(
            'product.product',
            'search_read',
            [[('id', 'in', product_ids)]],
            {
                'fields': [
                    'name', 'default_code', 'commercial_line_national_id'
                ],
                'context': {'lang': 'es_PE'}
            }
        )
        product_data = {p['id']: p for p in products}
        
        # Construir DataFrame
        print("🔧 Construyendo DataFrame...")
        records = []
        
        for line in lines:
            move_id = line['move_id'][0]
            product_id = line['product_id'][0]
            
            move = move_data.get(move_id, {})
            product = product_data.get(product_id, {})
            
            # Extraer vendedor
            vendedor = move.get('invoice_user_id')
            vendedor_id = vendedor[0] if vendedor else None
            vendedor_nombre = vendedor[1] if vendedor else 'Sin Vendedor'
            
            # Extraer cliente
            partner = line.get('partner_id')
            cliente_id = partner[0] if partner else None
            cliente_nombre = partner[1] if partner else 'Sin Cliente'
            
            # Extraer línea comercial
            linea = product.get('commercial_line_national_id')
            linea_comercial = linea[1] if linea else 'Sin Línea'
            
            # Balance es negativo para ventas, convertir a positivo
            total_linea = abs(line.get('balance', 0))
            
            records.append({
                'fecha': move.get('invoice_date'),
                'producto_id': product_id,
                'producto_codigo': product.get('default_code', ''),
                'producto_nombre': product.get('name', ''),
                'cantidad': line.get('quantity', 0),
                'precio_unitario': line.get('price_unit', 0),
                'total_linea': total_linea,
                'cliente_id': cliente_id,
                'cliente_nombre': cliente_nombre,
                'vendedor_id': vendedor_id,
                'vendedor_nombre': vendedor_nombre,
                'factura_numero': line.get('move_name', ''),
                'linea_comercial': linea_comercial
            })
        
        df = pd.DataFrame(records)
        
        # Convertir fecha a datetime
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Ordenar por fecha
        df = df.sort_values('fecha')
        
        print(f"✅ DataFrame construido: {len(df)} registros")
        print(f"📅 Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
        print(f"📦 Productos únicos: {df['producto_id'].nunique()}")
        print(f"💰 Total ventas: ${df['total_linea'].sum():,.2f}")
        
        return df
    
    def agregar_por_producto_periodo(self, df, frecuencia='M'):
        """
        Agrega ventas por producto y periodo para forecasting
        
        Args:
            df (DataFrame): DataFrame de ventas históricas
            frecuencia (str): 'D' (día), 'W' (semana), 'M' (mes), 'Q' (trimestre)
        
        Returns:
            DataFrame: Ventas agregadas con columnas:
                - periodo: Inicio del periodo
                - producto_id: ID del producto
                - producto_codigo: SKU
                - producto_nombre: Nombre
                - cantidad_total: Suma de unidades vendidas
                - ventas_total: Suma del total facturado
                - num_facturas: Número de transacciones
        """
        print(f"📊 Agregando por producto y periodo ({frecuencia})...")
        
        # Crear columna de periodo
        df['periodo'] = df['fecha'].dt.to_period(frecuencia).dt.to_timestamp()
        
        # Agrupar
        aggregated = df.groupby([
            'periodo', 'producto_id', 'producto_codigo', 
            'producto_nombre', 'linea_comercial'
        ]).agg({
            'cantidad': 'sum',
            'total_linea': 'sum',
            'factura_numero': 'count'
        }).reset_index()
        
        # Renombrar columnas
        aggregated.columns = [
            'periodo', 'producto_id', 'producto_codigo', 'producto_nombre',
            'linea_comercial', 'cantidad_total', 'ventas_total', 'num_facturas'
        ]
        
        print(f"✅ Agregación completa: {len(aggregated)} registros")
        print(f"📅 Periodos: {aggregated['periodo'].nunique()}")
        
        return aggregated


# ============================================================================
# 🧮 FUNCIONES PARA CÁLCULO DE MAPE
# ============================================================================

def calcular_mape(df_real, df_pronostico, col_real='cantidad_total', 
                  col_pronostico='cantidad_forecast'):
    """
    Calcula MAPE (Mean Absolute Percentage Error) para forecast
    
    Args:
        df_real (DataFrame): Ventas reales con columnas [periodo, producto_id, cantidad_total]
        df_pronostico (DataFrame): Pronóstico con columnas [periodo, producto_id, cantidad_forecast]
        col_real (str): Nombre columna de valores reales
        col_pronostico (str): Nombre columna de pronóstico
    
    Returns:
        dict: Métricas de precisión
            - mape_global: MAPE promedio
            - mape_por_producto: MAPE por producto
            - mae_global: MAE (Mean Absolute Error)
            - rmse_global: RMSE (Root Mean Squared Error)
    
    Fórmula MAPE:
        MAPE = (1/n) * Σ|((Real - Pronóstico) / Real)| * 100
    """
    import numpy as np
    
    # Hacer merge por periodo y producto
    merged = pd.merge(
        df_real[['periodo', 'producto_id', 'producto_codigo', col_real]],
        df_pronostico[['periodo', 'producto_id', col_pronostico]],
        on=['periodo', 'producto_id'],
        how='inner'
    )
    
    # Filtrar valores reales = 0 (evitar división por cero)
    merged = merged[merged[col_real] > 0]
    
    # Calcular error absoluto porcentual
    merged['ape'] = np.abs(
        (merged[col_real] - merged[col_pronostico]) / merged[col_real]
    ) * 100
    
    # MAPE global
    mape_global = merged['ape'].mean()
    
    # MAPE por producto
    mape_por_producto = merged.groupby([
        'producto_id', 'producto_codigo'
    ])['ape'].mean().reset_index()
    mape_por_producto.columns = ['producto_id', 'producto_codigo', 'mape']
    mape_por_producto = mape_por_producto.sort_values('mape')
    
    # MAE (Mean Absolute Error)
    merged['ae'] = np.abs(merged[col_real] - merged[col_pronostico])
    mae_global = merged['ae'].mean()
    
    # RMSE (Root Mean Squared Error)
    merged['se'] = (merged[col_real] - merged[col_pronostico]) ** 2
    rmse_global = np.sqrt(merged['se'].mean())
    
    return {
        'mape_global': mape_global,
        'mape_por_producto': mape_por_producto,
        'mae_global': mae_global,
        'rmse_global': rmse_global,
        'n_observaciones': len(merged),
        'n_productos': merged['producto_id'].nunique()
    }


def interpretar_mape(mape):
    """
    Interpreta el valor de MAPE según benchmarks de la industria
    
    Returns:
        str: Interpretación del MAPE
    """
    if mape < 10:
        return "🟢 EXCELENTE - Pronóstico muy preciso"
    elif mape < 20:
        return "🟡 BUENO - Pronóstico aceptable"
    elif mape < 30:
        return "🟠 REGULAR - Requiere ajustes"
    else:
        return "🔴 DEFICIENTE - Revisar modelo completamente"


# ============================================================================
# 📝 EJEMPLO DE USO COMPLETO
# ============================================================================

if __name__ == "__main__":
    # 1. Inicializar extractor
    extractor = OdooFacturacionExtractor()
    
    # 2. Definir periodo de análisis (últimos 12 meses)
    date_to = datetime.now().strftime('%Y-%m-%d')
    date_from = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    # 3. Extraer ventas históricas
    df_ventas = extractor.extraer_ventas_historicas(
        date_from=date_from,
        date_to=date_to,
        excluir_notas_credito=True,
        excluir_categorias=[315, 333, 304, 314, 318, 339]  # Ej: servicios, muestras
    )
    
    # 4. Agregar por producto y mes
    df_agregado = extractor.agregar_por_producto_periodo(
        df_ventas, 
        frecuencia='M'  # Mensual
    )
    
    # 5. Guardar datos para análisis
    df_agregado.to_csv('ventas_historicas_mensual.csv', index=False)
    print("✅ Datos guardados en ventas_historicas_mensual.csv")
    
    # 6. Ejemplo de cálculo de MAPE (asumiendo que tienes un pronóstico)
    # df_pronostico = pd.read_csv('mi_forecast.csv')  # Tu modelo de forecast
    # 
    # metricas = calcular_mape(
    #     df_real=df_agregado,
    #     df_pronostico=df_pronostico,
    #     col_real='cantidad_total',
    #     col_pronostico='cantidad_forecast'
    # )
    # 
    # print(f"\n📊 RESULTADOS DEL FORECAST:")
    # print(f"MAPE Global: {metricas['mape_global']:.2f}%")
    # print(f"Interpretación: {interpretar_mape(metricas['mape_global'])}")
    # print(f"MAE Global: {metricas['mae_global']:.2f} unidades")
    # print(f"RMSE Global: {metricas['rmse_global']:.2f} unidades")
    # print(f"Observaciones: {metricas['n_observaciones']}")
    # print(f"Productos evaluados: {metricas['n_productos']}")
    # 
    # # TOP 10 productos con mejor/peor pronóstico
    # print("\n🏆 TOP 10 Productos con Mejor Pronóstico:")
    # print(metricas['mape_por_producto'].head(10))
    # 
    # print("\n⚠️ TOP 10 Productos con Peor Pronóstico:")
    # print(metricas['mape_por_producto'].tail(10))
```

---

## 📊 Ejemplo de DataFrame de Salida

### Ventas Históricas Detalladas
```python
# df_ventas = extractor.extraer_ventas_historicas(...)
print(df_ventas.head())
```

| fecha       | producto_id | producto_codigo | producto_nombre     | cantidad | precio_unitario | total_linea | cliente_nombre | vendedor_nombre | factura_numero   | linea_comercial |
|-------------|-------------|-----------------|---------------------|----------|-----------------|-------------|----------------|-----------------|------------------|-----------------|
| 2025-10-15  | 789         | PARA-500        | Paracetamol 500mg   | 100.0    | 10.50           | 1050.00     | Farmacia XYZ   | Juan Pérez      | FACT/2025/1234   | Linea Humano    |
| 2025-10-16  | 790         | IBUP-400        | Ibuprofeno 400mg    | 50.0     | 8.75            | 437.50      | Droguería ABC  | María López     | FACT/2025/1235   | Linea Humano    |

### Ventas Agregadas Mensuales
```python
# df_agregado = extractor.agregar_por_producto_periodo(df_ventas, 'M')
print(df_agregado.head())
```

| periodo    | producto_id | producto_codigo | producto_nombre     | cantidad_total | ventas_total | num_facturas | linea_comercial |
|------------|-------------|-----------------|---------------------|----------------|--------------|--------------|-----------------|
| 2025-10-01 | 789         | PARA-500        | Paracetamol 500mg   | 2500           | 26250.00     | 15           | Linea Humano    |
| 2025-10-01 | 790         | IBUP-400        | Ibuprofeno 400mg    | 1200           | 10500.00     | 8            | Linea Humano    |
| 2025-11-01 | 789         | PARA-500        | Paracetamol 500mg   | 2800           | 29400.00     | 18           | Linea Humano    |

---

## 🧮 Cálculo de MAPE - Ejemplo Detallado

### Escenario
Tienes un modelo de forecast que predijo las ventas de enero 2026 y ahora quieres comparar con las ventas reales.

### Paso 1: Preparar Datos Reales
```python
df_ventas_reales = extractor.extraer_ventas_historicas(
    date_from='2026-01-01',
    date_to='2026-01-31'
)

df_reales_agregado = extractor.agregar_por_producto_periodo(
    df_ventas_reales, 
    frecuencia='M'
)
```

### Paso 2: Preparar Pronóstico (ejemplo)
```python
# Supongamos que tu modelo generó este pronóstico
df_pronostico = pd.DataFrame({
    'periodo': ['2026-01-01', '2026-01-01'],
    'producto_id': [789, 790],
    'cantidad_forecast': [2600, 1150]  # Tu pronóstico
})

df_pronostico['periodo'] = pd.to_datetime(df_pronostico['periodo'])
```

### Paso 3: Calcular MAPE
```python
metricas = calcular_mape(
    df_real=df_reales_agregado,
    df_pronostico=df_pronostico
)

print(f"MAPE: {metricas['mape_global']:.2f}%")
# Output: MAPE: 4.38%
# Interpretación: 🟢 EXCELENTE - Tu modelo es muy preciso
```

### Interpretación Manual del MAPE

| MAPE       | Interpretación                           | Acción Recomendada                    |
|------------|------------------------------------------|---------------------------------------|
| < 10%      | 🟢 **EXCELENTE** - Muy preciso           | Mantener modelo, monitorear          |
| 10% - 20%  | 🟡 **BUENO** - Aceptable                 | Ajustes menores, revisar outliers    |
| 20% - 30%  | 🟠 **REGULAR** - Necesita mejoras        | Re-entrenar con más features         |
| > 30%      | 🔴 **DEFICIENTE** - No confiable         | Cambiar algoritmo o revisardatos     |

---

## 🔧 Configuración Avanzada

### Excluir Categorías de Productos

Algunas categorías pueden no ser relevantes para forecasting (muestras gratis, servicios, etc.):

```python
# IDs de categorías a excluir (ajustar según tu Odoo)
CATEGORIAS_EXCLUIR = [
    315,  # Muestras médicas
    333,  # Servicios
    304,  # Bonificaciones
    314,  # Productos descontinuados
    318,  # Materiales de marketing
    339   # Otros no inventariables
]

df_ventas = extractor.extraer_ventas_historicas(
    date_from=date_from,
    date_to=date_to,
    excluir_categorias=CATEGORIAS_EXCLUIR
)
```

### Agregar por Diferentes Periodos

```python
# Agregación diaria
df_diario = extractor.agregar_por_producto_periodo(df_ventas, frecuencia='D')

# Agregación semanal
df_semanal = extractor.agregar_por_producto_periodo(df_ventas, frecuencia='W')

# Agregación mensual
df_mensual = extractor.agregar_por_producto_periodo(df_ventas, frecuencia='M')

# Agregación trimestral
df_trimestral = extractor.agregar_por_producto_periodo(df_ventas, frecuencia='Q')
```

---

## 📈 Integración con Modelos de Forecasting

### Ejemplo con Prophet (Facebook)

```python
from fbprophet import Prophet

# 1. Extraer ventas históricas de un producto específico
df_producto = df_agregado[df_agregado['producto_codigo'] == 'PARA-500'].copy()

# 2. Preparar datos para Prophet
df_prophet = df_producto[['periodo', 'cantidad_total']].copy()
df_prophet.columns = ['ds', 'y']  # Prophet requiere columnas 'ds' y 'y'

# 3. Entrenar modelo
model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False
)
model.fit(df_prophet)

# 4. Hacer pronóstico (próximos 3 meses)
future = model.make_future_dataframe(periods=3, freq='M')
forecast = model.predict(future)

# 5. Extraer solo el pronóstico futuro
df_forecast = forecast[['ds', 'yhat']].tail(3)
df_forecast.columns = ['periodo', 'cantidad_forecast']
df_forecast['producto_id'] = 789

print(df_forecast)
```

### Ejemplo con ARIMA (statsmodels)

```python
from statsmodels.tsa.arima.model import ARIMA

# 1. Preparar serie temporal
df_producto = df_agregado[df_agregado['producto_codigo'] == 'PARA-500'].copy()
df_producto = df_producto.set_index('periodo').sort_index()

# 2. Entrenar ARIMA
model = ARIMA(df_producto['cantidad_total'], order=(1, 1, 1))
model_fit = model.fit()

# 3. Pronóstico
forecast = model_fit.forecast(steps=3)
print(f"Pronóstico próximos 3 meses: {forecast.values}")
```

---

## 🚨 Consideraciones Importantes

### 1. **Manejo de Notas de Crédito**
- Las notas de crédito (`out_refund`) tienen cantidades negativas
- Decide si incluirlas o excluirlas según tu modelo
- Para forecast de demanda, generalmente se excluyen

### 2. **Productos con Ventas Esporádicas**
- Productos con ventas muy irregulares pueden generar MAPE muy alto
- Filtrar productos con mínimo de transacciones mensuales:

```python
# Filtrar productos con al menos 3 ventas por mes en promedio
df_filtrado = df_agregado.groupby('producto_id').filter(
    lambda x: len(x) >= 6 and x['num_facturas'].mean() >= 3
)
```

### 3. **Outliers y Promociones**
- Las promociones especiales pueden generar picos de venta
- Considerar detectar y tratar outliers antes de entrenar el modelo:

```python
from scipy import stats

# Detectar outliers con Z-score
df_agregado['z_score'] = stats.zscore(df_agregado['cantidad_total'])
df_sin_outliers = df_agregado[df_agregado['z_score'].abs() < 3]
```

### 4. **Rendimiento y Límites**
- La API de Odoo tiene límites de registros por request (default: 80)
- Ajustar `limit` en la función según volumen de datos
- Para grandes volúmenes (>100k líneas), considerar:
  - Dividir consultas por rango de fechas
  - Usar offset/paginación
  - Cachear datos en Supabase

---

## 📚 Referencias

### Documentación Odoo
- [Odoo External API](https://www.odoo.com/documentation/16.0/developer/reference/external_api.html)
- [Modelo account.move](https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html#reference-orm-model)

### Métricas de Forecast
- [MAPE Explained - Forecasting Metrics](https://en.wikipedia.org/wiki/Mean_absolute_percentage_error)
- [Forecast Accuracy Metrics](https://machinelearningmastery.com/time-series-forecasting-performance-measures-with-python/)

### Modelos de Forecasting
- [Prophet by Facebook](https://facebook.github.io/prophet/)
- [ARIMA - statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html)

---

## 🆘 Soporte y Contacto

Si tienes dudas sobre la integración:

1. **Revisar logs de Odoo:** Las llamadas JSON-RPC generan logs en el servidor
2. **Validar credenciales:** Verificar que `.env` tiene las credenciales correctas
3. **Probar con límites pequeños:** Empezar con `limit=100` para debugging
4. **Revisar permisos de usuario:** El usuario de Odoo debe tener acceso de lectura a `account.move` y `product.product`

---

## ✅ Checklist de Implementación

- [ ] Instalar dependencias: `pip install requests pandas python-dotenv`
- [ ] Configurar `.env` con credenciales de Odoo
- [ ] Probar autenticación con Odoo
- [ ] Extraer datos de prueba (últimos 7 días)
- [ ] Validar estructura del DataFrame
- [ ] Identificar categorías a excluir
- [ ] Implementar agregación mensual
- [ ] Entrenar modelo de forecast inicial
- [ ] Calcular MAPE con datos históricos (backtesting)
- [ ] Iterar y mejorar el modelo
- [ ] Documentar resultados y métricas

---

**Última actualización:** 10 de abril de 2026  
**Versión Dashboard:** 3.2  
**Autor:** Equipo de Desarrollo - AgrovetMarket

---

¡Éxito con tu modelo de forecasting! 🚀📊
