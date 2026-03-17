"""
Utilidades para manejo de fechas y meses.

Módulo que contiene funciones auxiliares para generación de listas de meses,
formatos de fechas y conversiones temporales.
"""


def get_meses_del_año(año):
    """
    Genera una lista de meses para un año específico.
    
    Args:
        año (int): Año para el cual generar la lista de meses.
    
    Returns:
        list: Lista de diccionarios con formato:
            [
                {'key': 'YYYY-MM', 'nombre': 'Nombre Mes YYYY'},
                ...
            ]
    
    Ejemplo:
        >>> get_meses_del_año(2026)
        [
            {'key': '2026-01', 'nombre': 'Enero 2026'},
            {'key': '2026-02', 'nombre': 'Febrero 2026'},
            ...
        ]
    """
    meses_nombres = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    meses_disponibles = []
    for i in range(1, 13):
        mes_key = f"{año}-{i:02d}"
        mes_nombre = f"{meses_nombres[i-1]} {año}"
        meses_disponibles.append({'key': mes_key, 'nombre': mes_nombre})
    return meses_disponibles
