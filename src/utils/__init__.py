"""
Utilidades auxiliares del Dashboard de Ventas.

Este paquete contiene funciones auxiliares para procesamiento de datos,
normalización y transformaciones.
"""

from .date_utils import get_meses_del_año
from .product_utils import normalizar_linea_comercial, limpiar_nombre_producto, limpiar_nombre_atrevia

__all__ = [
    'get_meses_del_año',
    'normalizar_linea_comercial',
    'limpiar_nombre_producto',
    'limpiar_nombre_atrevia'
]
