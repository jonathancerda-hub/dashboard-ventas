"""
Utilidades para normalización y limpieza de nombres de productos y líneas comerciales.

Este módulo contiene funciones para estandarizar nombres de líneas comerciales,
productos y agrupaciones de productos según reglas de negocio establecidas.
"""

import re


def normalizar_linea_comercial(nombre_linea):
    """
    Normaliza nombres de líneas comerciales agrupando GENVET y MARCA BLANCA como TERCEROS.
    
    Args:
        nombre_linea (str): Nombre original de la línea comercial.
    
    Returns:
        str: Nombre normalizado de la línea comercial.
    
    Ejemplos:
        >>> normalizar_linea_comercial('GENVET')
        'TERCEROS'
        >>> normalizar_linea_comercial('MARCA BLANCA')
        'TERCEROS'
        >>> normalizar_linea_comercial('GENVET PERÚ')
        'TERCEROS'
        >>> normalizar_linea_comercial('PETMEDICA')
        'PETMEDICA'
    """
    if not nombre_linea:
        return nombre_linea
    
    nombre_upper = nombre_linea.upper().strip()
    
    # Agrupar GENVET y MARCA BLANCA como TERCEROS
    if 'GENVET' in nombre_upper or 'MARCA BLANCA' in nombre_upper:
        return 'TERCEROS'
    
    return nombre_linea.upper().strip()


def limpiar_nombre_producto(nombre_producto):
    """
    Limpia los nombres de productos para agruparlos en el gráfico Top 7.
    
    Aplica agrupaciones específicas por marca y elimina variantes de tamaño/presentación
    para productos ATREVIA.
    
    Agrupaciones de productos:
    - BIOCAN → "BIOCAN"
    - ATREVIA VERSA → "ATREVIA VERSA"
    - SURALAN (sin QUATTRO) → "SURALAN"
    - SURALAN QUATTRO → "SURALAN QUATTRO"
    - EARTHBORN HOLISTIC → "EARTHBORN HOLISTIC"
    - FORMULA NATURAL → "FORMULA NATURAL"
    - GO NATIVE (sin ESSENTIALS) → "GO NATIVE"
    - GO NATIVE ESSENTIALS → "GO NATIVE ESSENTIALS"
    - NUTRIBITES → "NUTRIBITES"
    - PRO PAC → "PRO PAC"
    - SPORTMIX → "SPORTMIX"
    - PET DELICIA → "PET DELICIA"
    - ATREVIA (otros) → Agrupa por sub-producto (ONE, XR, etc.)
    
    Args:
        nombre_producto (str): Nombre original del producto.
    
    Returns:
        str: Nombre limpio y normalizado del producto.
    
    Ejemplo:
        >>> limpiar_nombre_producto('BIOCAN PERROS ADULTOS RAZAS GRANDES')
        'BIOCAN'
        >>> limpiar_nombre_producto('ATREVIA VERSA SMALL')
        'ATREVIA VERSA'
        >>> limpiar_nombre_producto('SURALAN QUATTRO 2.5ML')
        'SURALAN QUATTRO'
    """
    if not nombre_producto:
        return nombre_producto
    
    nombre_upper = nombre_producto.upper()
    
    # === AGRUPACIONES COMPLETAS (todas las variantes en un solo grupo) ===
    
    # BIOCAN: Todas las variantes
    if 'BIOCAN' in nombre_upper:
        return 'BIOCAN'
    
    # GO NATIVE ESSENTIALS: Debe ir ANTES de GO NATIVE para detectarlo primero
    if 'GO NATIVE ESSENTIALS' in nombre_upper or 'GO NATIVE ESSENTIAL' in nombre_upper:
        return 'GO NATIVE ESSENTIALS'
    
    # GO NATIVE: Sin ESSENTIALS
    if 'GO NATIVE' in nombre_upper:
        return 'GO NATIVE'
    
    # EARTHBORN HOLISTIC
    if 'EARTHBORN' in nombre_upper and 'HOLISTIC' in nombre_upper:
        return 'EARTHBORN HOLISTIC'
    
    # FORMULA NATURAL
    if 'FORMULA NATURAL' in nombre_upper:
        return 'FORMULA NATURAL'
    
    # NUTRIBITES
    if 'NUTRIBITES' in nombre_upper or 'NUTRIBITE' in nombre_upper:
        return 'NUTRIBITES'
    
    # PRO PAC
    if 'PRO PAC' in nombre_upper:
        return 'PRO PAC'
    
    # SPORTMIX
    if 'SPORTMIX' in nombre_upper:
        return 'SPORTMIX'
    
    # PET DELICIA
    if 'PET DELICIA' in nombre_upper or ('CACAROLINHA' in nombre_upper or 'JARDINEIRA' in nombre_upper or 
        'MARAVILHA' in nombre_upper or 'PICADINHO' in nombre_upper or 
        'RISOTINHO' in nombre_upper or 'PANELINHA' in nombre_upper):
        return 'PET DELICIA'
    
    # SURALAN QUATTRO: Debe ir ANTES de SURALAN para detectarlo primero
    if 'SURALAN' in nombre_upper and 'QUATTRO' in nombre_upper:
        return 'SURALAN QUATTRO'
    
    # SURALAN: Sin QUATTRO
    if 'SURALAN' in nombre_upper:
        return 'SURALAN'
    
    # ATREVIA VERSA: Todas las presentaciones
    if 'ATREVIA VERSA' in nombre_upper or 'ATREVIA' in nombre_upper and 'VERSA' in nombre_upper:
        return 'ATREVIA VERSA'
    
    # === ATREVIA (otros): Agrupación por sub-producto ===
    if 'ATREVIA' not in nombre_upper:
        return nombre_producto
    
    # Lista de palabras que indican tamaño/presentación a eliminar para ATREVIA
    tamanos_presentaciones = [
        'MEDIUM', 'LARGE', 'SMALL', 'MINI', 'EXTRA LARGE', 'XL', 'L', 'M', 'S', 
        'SPOT ON MEDIUM', 'SPOT ON LARGE', 'SPOT ON SMALL', 'SPOT ON MINI',
        'CATS SPOT ON MEDIUM', 'CATS SPOT ON LARGE', 'CATS SPOT ON SMALL', 'CATS SPOT ON MINI',
        'SPOT ON'
    ]
    
    nombre_limpio = nombre_producto.strip()
    
    # Paso 1: Eliminar (N) al final si existe
    nombre_limpio = re.sub(r'\s*\(N\)\s*$', '', nombre_limpio, flags=re.IGNORECASE).strip()
    
    # Paso 2: Ordenar por longitud descendente para procesar primero las frases más largas
    tamanos_ordenados = sorted(tamanos_presentaciones, key=len, reverse=True)
    
    for tamano in tamanos_ordenados:
        # Buscar y eliminar el tamaño/presentación al final del nombre
        if nombre_limpio.upper().endswith(' ' + tamano):
            nombre_limpio = nombre_limpio[:-(len(tamano) + 1)].strip()
            break
    
    return nombre_limpio


# Mantener alias para compatibilidad con código existente
limpiar_nombre_atrevia = limpiar_nombre_producto
