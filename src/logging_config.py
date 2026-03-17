"""
Configuración centralizada de logging para Dashboard de Ventas.

Niveles de logging:
- DEBUG: Información detallada para debugging
- INFO: Confirmación de operaciones normales
- WARNING: Situaciones inesperadas pero manejables
- ERROR: Errores que afectan funcionalidad
- CRITICAL: Errores que pueden detener la aplicación
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para terminal (Windows compatible)"""
    
    # Códigos ANSI para colores
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }
    
    # Emojis por nivel (sin emoji para evitar encoding issues en Windows)
    PREFIXES = {
        'DEBUG': '[DEBUG]',
        'INFO': '[OK]',
        'WARNING': '[WARN]',
        'ERROR': '[ERROR]',
        'CRITICAL': '[CRITICAL]'
    }
    
    def format(self, record):
        # Agregar color y prefijo
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        prefix = self.PREFIXES.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        # Formato: [NIVEL] Módulo - Mensaje
        log_fmt = f"{color}{prefix} {record.name}{reset} - {record.getMessage()}"
        
        # Si hay excepción, agregar traceback
        if record.exc_info:
            log_fmt += f"\n{self.formatException(record.exc_info)}"
        
        return log_fmt


def setup_logging(log_level=logging.INFO, log_to_file=True):
    """
    Configura el sistema de logging para toda la aplicación.
    
    Args:
        log_level: Nivel mínimo de logging (default: INFO)
        log_to_file: Si True, también guarda logs en archivo (default: True)
    
    Returns:
        logging.Logger: Logger root configurado
    """
    # Crear directorio de logs si no existe
    if log_to_file:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Archivo de log con timestamp
        log_file = log_dir / f"dashboard_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para consola (con colores)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(ColoredFormatter())
    root_logger.addHandler(console_handler)
    
    # Handler para archivo (sin colores)
    if log_to_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Archivo captura todo
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Reducir verbosidad de librerías externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('supabase').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name):
    """
    Obtiene un logger específico para un módulo.
    
    Args:
        name: Nombre del módulo (usar __name__)
    
    Returns:
        logging.Logger: Logger configurado para el módulo
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Operación exitosa")
        >>> logger.error("Error procesando datos", exc_info=True)
    """
    return logging.getLogger(name)
