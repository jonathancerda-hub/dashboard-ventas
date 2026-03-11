# supabase_manager.py - Gestor de metas en Supabase
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class SupabaseManager:
    """
    Gestor de conexión y operaciones con Supabase para metas de ventas.
    Reemplaza GoogleSheetsManager para gestionar metas de 2026.
    """
    
    def __init__(self):
        """Inicializa la conexión con Supabase"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("⚠️ Credenciales de Supabase no configuradas. Usando modo fallback.")
            self.supabase = None
            self.enabled = False
            return
        
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.enabled = True
            print("✅ Conexión a Supabase establecida")
        except Exception as e:
            print(f"❌ Error al conectar con Supabase: {e}")
            self.supabase = None
            self.enabled = False
    
    # ========== METAS DE VENTAS GENERALES ==========
    
    def guardar_meta_venta(self, mes: str, linea_comercial: str, 
                           meta_total: float, meta_ipn: float = None):
        """
        Guarda o actualiza una meta de venta general por línea comercial
        
        Args:
            mes: Formato 'YYYY-MM' (ej: '2026-01')
            linea_comercial: Nombre de la línea comercial
            meta_total: Meta total del mes
            meta_ipn: Meta de productos nuevos (opcional)
        
        Returns:
            Dict con los datos guardados o None si hay error
        """
        if not self.enabled:
            print("⚠️ Supabase no disponible")
            return None
        
        try:
            data = {
                'mes': mes,
                'linea_comercial': linea_comercial.upper(),
                'meta_total': float(meta_total),
                'meta_ipn': float(meta_ipn) if meta_ipn else None,
                'updated_at': datetime.now().isoformat()
            }
            
            # Upsert: insertar o actualizar si existe
            result = self.supabase.table('metas_ventas_2026')\
                .upsert(data, on_conflict='mes,linea_comercial')\
                .execute()
            
            print(f"✅ Meta guardada: {linea_comercial} - {mes}")
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Error guardando meta: {e}")
            return None
    
    def obtener_metas_mes(self, mes: str):
        """
        Obtiene todas las metas de un mes específico
        
        Args:
            mes: Formato 'YYYY-MM' o 'YYYY-MM-DD'
        
        Returns:
            Lista de diccionarios con las metas por línea comercial
        """
        if not self.enabled:
            return []
        
        try:
            # Extraer solo año-mes si viene con día
            if len(mes) > 7:
                mes = mes[:7]
            
            result = self.supabase.table('metas_ventas_2026')\
                .select('*')\
                .eq('mes', mes)\
                .order('linea_comercial')\
                .execute()
            
            print(f"📊 Metas obtenidas para {mes}: {len(result.data)} líneas")
            return result.data
        except Exception as e:
            print(f"❌ Error obteniendo metas: {e}")
            return []
    
    def obtener_todas_metas(self):
        """
        Obtiene todas las metas de 2026
        
        Returns:
            Lista de todas las metas
        """
        if not self.enabled:
            return []
        
        try:
            result = self.supabase.table('metas_ventas_2026')\
                .select('*')\
                .order('mes, linea_comercial')\
                .execute()
            
            print(f"📊 Total de metas: {len(result.data)}")
            return result.data
        except Exception as e:
            print(f"❌ Error obteniendo todas las metas: {e}")
            return []
    
    # ========== METAS POR VENDEDOR ==========
    
    def guardar_meta_vendedor(self, mes: str, vendedor_id: int, 
                              vendedor_nombre: str, meta_total: float,
                              equipo_venta: str = None, linea_comercial: str = None,
                              meta_ipn: float = None, region: str = None):
        """
        Guarda o actualiza una meta de vendedor
        
        Args:
            mes: Formato 'YYYY-MM'
            vendedor_id: ID del vendedor en Odoo
            vendedor_nombre: Nombre completo del vendedor
            meta_total: Meta total asignada
            equipo_venta: Equipo al que pertenece (opcional)
            linea_comercial: Línea comercial específica (opcional)
            meta_ipn: Meta de productos nuevos (opcional)
            region: Región del vendedor (opcional)
        
        Returns:
            Dict con los datos guardados o None si hay error
        """
        if not self.enabled:
            print("⚠️ Supabase no disponible")
            return None
        
        try:
            data = {
                'mes': mes,
                'vendedor_id': int(vendedor_id),
                'vendedor_nombre': vendedor_nombre,
                'meta_total': float(meta_total),
                'meta_ipn': float(meta_ipn) if meta_ipn else None,
                'equipo_venta': equipo_venta,
                'linea_comercial': linea_comercial.upper() if linea_comercial else None,
                'region': region,
                'updated_at': datetime.now().isoformat()
            }
            
            # Upsert
            result = self.supabase.table('metas_vendedor_2026')\
                .upsert(data, on_conflict='mes,vendedor_id,linea_comercial')\
                .execute()
            
            print(f"✅ Meta vendedor guardada: {vendedor_nombre} - {mes}")
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Error guardando meta vendedor: {e}")
            return None
    
    def obtener_metas_vendedor_mes(self, mes: str, equipo_venta: str = None):
        """
        Obtiene metas de vendedores para un mes
        
        Args:
            mes: Formato 'YYYY-MM'
            equipo_venta: Opcional, filtrar por equipo
        
        Returns:
            Lista de diccionarios con metas de vendedores
        """
        if not self.enabled:
            return []
        
        try:
            # Extraer solo año-mes si viene con día
            if len(mes) > 7:
                mes = mes[:7]
            
            query = self.supabase.table('metas_vendedor_2026')\
                .select('*')\
                .eq('mes', mes)
            
            if equipo_venta:
                query = query.eq('equipo_venta', equipo_venta)
            
            result = query.order('vendedor_nombre').execute()
            
            print(f"📊 Metas vendedor obtenidas: {len(result.data)}")
            return result.data
        except Exception as e:
            print(f"❌ Error obteniendo metas vendedor: {e}")
            return []
    
    def obtener_meta_vendedor(self, mes: str, vendedor_id: int):
        """
        Obtiene la meta de un vendedor específico para un mes
        
        Args:
            mes: Formato 'YYYY-MM'
            vendedor_id: ID del vendedor
        
        Returns:
            Dict con la meta del vendedor o None
        """
        if not self.enabled:
            return None
        
        try:
            # Extraer solo año-mes si viene con día
            if len(mes) > 7:
                mes = mes[:7]
            
            result = self.supabase.table('metas_vendedor_2026')\
                .select('*')\
                .eq('mes', mes)\
                .eq('vendedor_id', vendedor_id)\
                .limit(1)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Error obteniendo meta vendedor: {e}")
            return None
    
    # ========== MÉTODOS PARA EQUIPOS DE VENDEDORES ==========
    
    def read_equipos(self):
        """
        Lee la asignación de equipos desde Supabase.
        Retorna: dict {equipo_id: [vendedor_id1, vendedor_id2, ...]}
        """
        if not self.enabled:
            return {}
        
        try:
            response = self.supabase.table('equipos_vendedores').select('*').execute()
            
            equipos_dict = {}
            for row in response.data:
                equipo_id = row.get('equipo_id')
                vendedor_id = row.get('vendedor_id')
                
                if equipo_id:
                    if equipo_id not in equipos_dict:
                        equipos_dict[equipo_id] = []
                    if vendedor_id:
                        equipos_dict[equipo_id].append(vendedor_id)
            
            return equipos_dict
            
        except Exception as e:
            print(f"Error al leer equipos de vendedores: {e}")
            return {}
    
    def write_equipos(self, equipos_data, todos_los_vendedores):
        """
        Escribe la asignación de equipos en Supabase.
        
        Args:
            equipos_data: dict {equipo_id: [vendedor_id1, vendedor_id2, ...]}
            todos_los_vendedores: lista de vendedores con {id, name}
        """
        if not self.enabled:
            return
        
        try:
            # Crear mapa de vendedores por ID
            vendedores_por_id = {v['id']: v['name'] for v in todos_los_vendedores}
            
            # Primero, eliminar todas las asignaciones existentes
            self.supabase.table('equipos_vendedores').delete().neq('equipo_id', '').execute()
            
            # Luego, insertar las nuevas asignaciones
            rows = []
            for equipo_id, vendedor_ids_list in equipos_data.items():
                # Nombre del equipo para mostrar
                equipo_nombre = equipo_id.replace('_', ' ').title()
                for vendedor_id in vendedor_ids_list:
                    vendedor_nombre = vendedores_por_id.get(vendedor_id, f'Vendedor {vendedor_id}')
                    rows.append({
                        'equipo_id': equipo_id,
                        'equipo_nombre': equipo_nombre,  # Campo requerido NOT NULL
                        'vendedor_id': vendedor_id,
                        'vendedor_nombre': vendedor_nombre
                    })
            
            if rows:
                self.supabase.table('equipos_vendedores').insert(rows).execute()
                print(f"✅ Guardadas {len(rows)} asignaciones de equipos en Supabase")
            
        except Exception as e:
            print(f"Error al escribir equipos de vendedores: {e}")
    
    def read_metas(self):
        """
        Lee las metas de vendedores y las retorna en formato anidado.
        Retorna: {equipo_id: {vendedor_id: {mes: {meta, meta_ipn}}}}
        """
        if not self.enabled:
            return {}
        
        try:
            response = self.supabase.table('metas_vendedor_2026').select('*').execute()
            
            metas_anidadas = {}
            for row in response.data:
                # Usar linea_comercial en lugar de equipo_venta, normalizar a lowercase
                linea_comercial = row.get('linea_comercial', '').lower()
                vendedor_id = str(row.get('vendedor_id', ''))
                mes = row.get('mes', '')
                
                if linea_comercial not in metas_anidadas:
                    metas_anidadas[linea_comercial] = {}
                if vendedor_id not in metas_anidadas[linea_comercial]:
                    metas_anidadas[linea_comercial][vendedor_id] = {}
                
                metas_anidadas[linea_comercial][vendedor_id][mes] = {
                    'meta': float(row.get('meta_total', 0)),
                    'meta_ipn': float(row.get('meta_ipn', 0))
                }
            
            return metas_anidadas
            
        except Exception as e:
            print(f"Error al leer metas de vendedores: {e}")
            return {}
    
    def write_metas(self, metas_anidadas):
        """
        Escribe las metas de vendedores desde formato anidado.
        
        Args:
            metas_anidadas: {equipo_id: {vendedor_id: {mes: {meta, meta_ipn}}}}
        """
        if not self.enabled:
            return
        
        try:
            rows = []
            for equipo_id, vendedores in metas_anidadas.items():
                for vendedor_id, meses in vendedores.items():
                    for mes, valores in meses.items():
                        rows.append({
                            'mes': mes,
                            'vendedor_id': int(vendedor_id),
                            'vendedor_nombre': f'Vendedor {vendedor_id}',  # Se necesita para NOT NULL constraint
                            'meta_total': float(valores.get('meta', 0)),
                            'meta_ipn': float(valores.get('meta_ipn', 0)),
                            'linea_comercial': equipo_id.upper()  # Usar equipo_id como línea comercial en UPPERCASE
                        })
            
            if rows:
                # Upsert cada meta
                for row in rows:
                    self.supabase.table('metas_vendedor_2026').upsert(
                        row,
                        on_conflict='mes,vendedor_id,linea_comercial'
                    ).execute()
                
                print(f"✅ Guardadas {len(rows)} metas de vendedores en Supabase")
            
        except Exception as e:
            print(f"Error al escribir metas de vendedores: {e}")
    
    # ========== MÉTODOS DE COMPATIBILIDAD CON GOOGLE SHEETS ==========
    
    def read_metas_por_linea(self):
        """
        Lee metas por línea en formato compatible con GoogleSheetsManager
        
        Returns:
            Dict con estructura: {mes: {'metas': {linea: meta}, 'metas_ipn': {linea: meta_ipn}, 'total': X, 'total_ipn': Y}}
        """
        if not self.enabled:
            return {}
        
        try:
            metas = self.obtener_todas_metas()
            
            # Convertir a formato esperado por el código existente
            metas_por_mes = {}
            for meta in metas:
                mes = meta['mes']
                linea = meta['linea_comercial']
                
                if mes not in metas_por_mes:
                    metas_por_mes[mes] = {'metas': {}, 'metas_ipn': {}, 'total': 0, 'total_ipn': 0}
                
                metas_por_mes[mes]['metas'][linea] = meta['meta_total']
                metas_por_mes[mes]['total'] += meta['meta_total']  # Sumar al total
                
                if meta.get('meta_ipn'):
                    metas_por_mes[mes]['metas_ipn'][linea] = meta['meta_ipn']
                    metas_por_mes[mes]['total_ipn'] += meta['meta_ipn']  # Sumar al total IPN
            
            return metas_por_mes
        except Exception as e:
            print(f"❌ Error en read_metas_por_linea: {e}")
            return {}
    
    def write_metas_por_linea(self, metas_data):
        """
        Escribe metas por línea (compatibilidad con GoogleSheetsManager)
        
        Args:
            metas_data: Dict con estructura {mes: {'metas': {linea: meta}, 'metas_ipn': {linea: meta_ipn}}}
        """
        if not self.enabled:
            print("⚠️ Supabase no disponible")
            return
        
        try:
            for mes, datos in metas_data.items():
                metas = datos.get('metas', {})
                metas_ipn = datos.get('metas_ipn', {})
                
                for linea, meta_total in metas.items():
                    meta_ipn = metas_ipn.get(linea, None)
                    # Normalizar línea a mayúsculas para consistencia
                    linea_normalizada = linea.upper()
                    self.guardar_meta_venta(mes, linea_normalizada, meta_total, meta_ipn)
            
            print("✅ Metas guardadas en Supabase")
        except Exception as e:
            print(f"❌ Error en write_metas_por_linea: {e}")
    
    def read_metas_vendedor(self):
        """
        Lee metas de vendedores en formato compatible con GoogleSheetsManager
        
        Returns:
            Dict con estructura: {equipo_id: {vendedor_id: {mes: {'meta': X, 'meta_ipn': Y}}}}
        """
        if not self.enabled:
            return {}
        
        try:
            result = self.supabase.table('metas_vendedor_2026')\
                .select('*')\
                .execute()
            
            # Convertir a formato anidado esperado
            metas_anidadas = {}
            for meta in result.data:
                equipo_id = meta.get('equipo_venta', 'SIN_EQUIPO')
                vendedor_id = str(meta['vendedor_id'])
                mes = meta['mes']
                
                if equipo_id not in metas_anidadas:
                    metas_anidadas[equipo_id] = {}
                if vendedor_id not in metas_anidadas[equipo_id]:
                    metas_anidadas[equipo_id][vendedor_id] = {}
                
                metas_anidadas[equipo_id][vendedor_id][mes] = {
                    'meta': meta['meta_total'],
                    'meta_ipn': meta.get('meta_ipn', 0)
                }
            
            return metas_anidadas
        except Exception as e:
            print(f"❌ Error en read_metas_vendedor: {e}")
            return {}
    
    def write_metas_vendedor(self, metas_data, vendedores_info=None):
        """
        Escribe metas de vendedores (compatibilidad con GoogleSheetsManager)
        
        Args:
            metas_data: Dict con estructura {equipo_id: {vendedor_id: {mes: {'meta': X, 'meta_ipn': Y}}}}
            vendedores_info: Dict opcional con info de vendedores {vendedor_id: {'name': ...}}
        """
        if not self.enabled:
            print("⚠️ Supabase no disponible")
            return
        
        try:
            for equipo_id, vendedores in metas_data.items():
                for vendedor_id, meses in vendedores.items():
                    vendedor_nombre = "Vendedor"
                    if vendedores_info and str(vendedor_id) in vendedores_info:
                        vendedor_nombre = vendedores_info[str(vendedor_id)].get('name', f'Vendedor {vendedor_id}')
                    
                    for mes, datos in meses.items():
                        self.guardar_meta_vendedor(
                            mes=mes,
                            vendedor_id=int(vendedor_id),
                            vendedor_nombre=vendedor_nombre,
                            meta_total=datos.get('meta', 0),
                            meta_ipn=datos.get('meta_ipn', 0),
                            equipo_venta=equipo_id
                        )
            
            print("✅ Metas de vendedores guardadas en Supabase")
        except Exception as e:
            print(f"❌ Error en write_metas_vendedor: {e}")
