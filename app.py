# app.py - Dashboard de Ventas Farmacéuticas

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, g
from dotenv import load_dotenv
from odoo_manager import OdooManager
from google_sheets_manager import GoogleSheetsManager
from analytics_db import AnalyticsDB
import os
import pandas as pd
import json
import io
import calendar
from datetime import datetime, timedelta
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
import pytz

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Timezone de Perú
PERU_TZ = pytz.timezone('America/Lima')
UTC_TZ = pytz.UTC

# Configuración para deshabilitar cache de templates
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# --- Inicialización de Managers ---
try:
    data_manager = OdooManager()
except Exception as e:
    print(f"⚠️ No se pudo inicializar OdooManager: {e}. Continuando en modo offline.")
    # Crear un stub mínimo con las funciones usadas en la app para evitar fallos
    class _StubManager:
        def get_filter_options(self):
            return {'lineas': [], 'clients': []}
        def get_sales_lines(self, *args, **kwargs):
            return []
        def get_all_sellers(self):
            return []
        def get_commercial_lines_stacked_data(self, *args, **kwargs):
            return {'yAxis': [], 'series': [], 'legend': []}
    data_manager = _StubManager()
gs_manager = GoogleSheetsManager(
    credentials_file='credentials.json',
    sheet_name=os.getenv('GOOGLE_SHEET_NAME')
)

# Inicializar sistema de analytics
analytics_db = AnalyticsDB()

# --- Middleware para Analytics ---

@app.before_request
def before_request():
    """Registra información de la petición antes de procesarla."""
    g.start_time = datetime.now()

@app.after_request
def after_request(response):
    """Registra la visita después de procesar la petición."""
    # Solo registrar si el usuario está logueado y la petición es exitosa
    if 'username' in session and response.status_code == 200:
        # No registrar peticiones a archivos estáticos
        if not request.path.startswith('/static/'):
            try:
                # Mapeo de rutas a títulos
                page_titles = {
                    '/': 'Dashboard Principal',
                    '/dashboard': 'Dashboard de Ventas',
                    '/equipo-ventas': 'Equipo de Ventas',
                    '/meta': 'Metas de Ventas',
                    '/sales': 'Ventas Detalladas',
                    '/metas-vendedor': 'Metas por Vendedor',
                    '/dashboard-linea': 'Dashboard por Línea',
                    '/analytics': 'Analytics y Estadísticas'
                }
                
                page_title = page_titles.get(request.path, request.path)
                
                analytics_db.log_visit(
                    user_email=session.get('username'),
                    user_name=session.get('user_name'),
                    page_url=request.path,
                    page_title=page_title,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    referrer=request.referrer,
                    method=request.method
                )
            except Exception as e:
                print(f"⚠️ Error al registrar analytics: {e}")
    
    return response

# --- Funciones Auxiliares ---

def get_meses_del_año(año):
    """Genera una lista de meses para un año específico."""
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

def normalizar_linea_comercial(nombre_linea):
    """
    Normaliza nombres de líneas comerciales agrupando GENVET y MARCA BLANCA como TERCEROS.
    
    Ejemplos:
    - GENVET → TERCEROS
    - MARCA BLANCA → TERCEROS
    - GENVET PERÚ → TERCEROS
    - PETMEDICA → PETMEDICA (sin cambios)
    """
    if not nombre_linea:
        return nombre_linea
    
    nombre_upper = nombre_linea.upper().strip()
    
    # Agrupar GENVET y MARCA BLANCA como TERCEROS
    if 'GENVET' in nombre_upper or 'MARCA BLANCA' in nombre_upper:
        return 'TERCEROS'
    
    return nombre_linea.upper().strip()

def limpiar_nombre_atrevia(nombre_producto):
    """
    Limpia los nombres de productos ATREVIA eliminando indicadores de tamaño/presentación.
    
    Ejemplos:
    - ATREVIA ONE MEDIUM → ATREVIA ONE
    - ATREVIA XR LARGE → ATREVIA XR  
    - ATREVIA 360° MEDIUM → ATREVIA 360°
    - ATREVIA TRIO CATS SPOT ON MEDIUM → ATREVIA TRIO CATS
    """
    if not nombre_producto or 'ATREVIA' not in nombre_producto.upper():
        return nombre_producto
    
    # Lista de palabras que indican tamaño/presentación a eliminar
    tamanos_presentaciones = [
        'MEDIUM', 'LARGE', 'SMALL', 'MINI', 'EXTRA LARGE', 'XL', 'L', 'M', 'S', 
        'SPOT ON MEDIUM', 'SPOT ON LARGE', 'SPOT ON SMALL', 'SPOT ON MINI',
        'CATS SPOT ON MEDIUM', 'CATS SPOT ON LARGE', 'CATS SPOT ON SMALL', 'CATS SPOT ON MINI',
        'SPOT ON'
    ]
    
    nombre_limpio = nombre_producto.strip()
    
    # Procesar solo si contiene ATREVIA
    if 'ATREVIA' in nombre_limpio.upper():
        # Ordenar por longitud descendente para procesar primero las frases más largas
        tamanos_ordenados = sorted(tamanos_presentaciones, key=len, reverse=True)
        
        for tamano in tamanos_ordenados:
            # Buscar y eliminar el tamaño/presentación al final del nombre
            if nombre_limpio.upper().endswith(' ' + tamano):
                nombre_limpio = nombre_limpio[:-(len(tamano) + 1)].strip()
                break
    
    return nombre_limpio

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = data_manager.authenticate_user(username, password)
        
        if user_data:
            # --- Verificación de Lista Blanca ---
            try:
                # Intentar leer desde variable de entorno primero
                allowed_emails_env = os.getenv('ALLOWED_USERS')
                if allowed_emails_env:
                    # Si existe la variable de entorno, parsear la lista separada por comas
                    allowed_emails = [email.strip() for email in allowed_emails_env.split(',')]
                else:
                    # Fallback: leer desde el archivo JSON local
                    with open('allowed_users.json', 'r') as f:
                        allowed_emails = json.load(f).get('allowed_emails', [])
                
                user_login = user_data.get('login')
                if user_login and user_login in allowed_emails:
                    # Usuario autenticado y autorizado
                    session['username'] = user_login
                    session['user_name'] = user_data.get('name', username)
                    flash('¡Inicio de sesión exitoso!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    # Usuario autenticado pero no autorizado
                    flash('No tienes permiso para acceder a esta aplicación.', 'warning')
            except FileNotFoundError:
                flash('Error de configuración: El archivo de usuarios permitidos no se encuentra.', 'danger')
            except Exception as e:
                flash(f'Error al verificar permisos: {str(e)}', 'danger')
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    # Redirigir la ruta raíz al dashboard
    return redirect(url_for('dashboard'))

@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # --- Verificación de Permisos ---
    admin_users = ["jonathan.cerda@agrovetmarket.com", "janet.hueza@agrovetmarket.com", "juan.portal@agrovetmarket.com"]
    is_admin = session.get('username') in admin_users
    if not is_admin:
        flash('No tienes permiso para acceder a esta página.', 'warning')
        return redirect(url_for('dashboard'))
    # --- Fin Verificación ---
    
    try:
        # Obtener opciones de filtro
        filter_options = data_manager.get_filter_options()
        
        if request.method == 'POST':
            # For POST, get filters from the form
            selected_filters = {
                'date_from': request.form.get('date_from') or None,
                'date_to': request.form.get('date_to') or None,
                'search_term': request.form.get('search_term') or None
            }
        else:
            # For GET, start with no filters, so defaults will be used
            selected_filters = {
                'date_from': request.args.get('date_from') or None,
                'date_to': request.args.get('date_to') or None,
                'search_term': request.args.get('search_term') or None
            }

        # Create a clean copy for the database query
        query_filters = selected_filters.copy()

        # Clean up filter values for the query
        for key, value in query_filters.items():
            if not value:  # Handles empty strings and None
                query_filters[key] = None
        
        # Fetch data on every page load (GET and POST)
        # On GET, filters are None, so odoo_manager will use defaults (last 30 days)
        sales_data = data_manager.get_sales_lines(
            date_from=query_filters.get('date_from'),
            date_to=query_filters.get('date_to'),
            partner_id=None,
            search=query_filters.get('search_term'),
            linea_id=None,
            limit=1000
        )
        
        # Filtrar VENTA INTERNACIONAL (exportaciones)
        sales_data_filtered = []
        for sale in sales_data:
            linea_comercial = sale.get('commercial_line_national_id')
            if linea_comercial and isinstance(linea_comercial, list) and len(linea_comercial) > 1:
                nombre_linea = linea_comercial[1].upper()
                if 'VENTA INTERNACIONAL' in nombre_linea:
                    continue
            
            # También filtrar por canal de ventas
            canal_ventas = sale.get('sales_channel_id')
            if canal_ventas and isinstance(canal_ventas, list) and len(canal_ventas) > 1:
                nombre_canal = canal_ventas[1].upper()
                if 'VENTA INTERNACIONAL' in nombre_canal or 'INTERNACIONAL' in nombre_canal:
                    continue
            
            sales_data_filtered.append(sale)
        
        return render_template('sales.html', 
                             sales_data=sales_data_filtered,
                             filter_options=filter_options,
                             selected_filters=selected_filters,
                             fecha_actual=datetime.now(),
                             is_admin=is_admin) # Pasar el flag a la plantilla
    
    except Exception as e:
        flash(f'Error al obtener datos: {str(e)}', 'danger')
        return render_template('sales.html', 
                             sales_data=[],
                             filter_options={'lineas': [], 'clientes': []},
                             selected_filters={},
                             fecha_actual=datetime.now(),
                             is_admin=is_admin) # Pasar el flag a la plantilla

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # --- Lógica de Permisos de Administrador ---
        admin_users = ["jonathan.cerda@agrovetmarket.com", "janet.hueza@agrovetmarket.com", "juan.portal@agrovetmarket.com", "AMAHOdoo@agrovetmarket.com"]
        is_admin = session.get('username') in admin_users

        # Obtener año seleccionado (parámetro o año actual por defecto)
        fecha_actual = datetime.now()
        año_seleccionado = request.args.get('año', str(fecha_actual.year))
        try:
            año_seleccionado = int(año_seleccionado)
        except (ValueError, TypeError):
            año_seleccionado = fecha_actual.year
        
        # Generar lista de años disponibles (desde 2025 hasta año actual)
        años_disponibles = list(range(2025, fecha_actual.year + 1))
        
        # Obtener mes seleccionado
        mes_seleccionado = request.args.get('mes', f"{año_seleccionado}-{fecha_actual.month:02d}" if año_seleccionado == fecha_actual.year else f"{año_seleccionado}-01")
        
        # --- NUEVA LÓGICA DE FILTRADO POR DÍA ---
        # Obtener el día final del filtro, si existe
        dia_fin_param = request.args.get('dia_fin')

        # Crear todos los meses del año seleccionado
        meses_disponibles = get_meses_del_año(año_seleccionado)
        
        # Obtener nombre del mes seleccionado
        mes_obj = next((m for m in meses_disponibles if m['key'] == mes_seleccionado), None)
        mes_nombre = mes_obj['nombre'] if mes_obj else "Mes Desconocido"
        
        año_sel, mes_sel = mes_seleccionado.split('-')
        
        # Determinar el día a usar para los cálculos y la fecha final
        if dia_fin_param:
            try:
                dia_actual = int(dia_fin_param)
                fecha_fin = f"{año_sel}-{mes_sel}-{str(dia_actual).zfill(2)}"
            except (ValueError, TypeError):
                # Si el parámetro no es un número válido, usar el comportamiento por defecto
                dia_fin_param = None # Resetear para que entre al siguiente bloque
        
        if not dia_fin_param:
            # Comportamiento original si no hay filtro de día
            if mes_seleccionado == fecha_actual.strftime('%Y-%m'):
                # Mes actual: usar día actual
                dia_actual = fecha_actual.day
            else:
                # Mes pasado: usar último día del mes
                ultimo_dia_mes = calendar.monthrange(int(año_sel), int(mes_sel))[1]
                dia_actual = ultimo_dia_mes
            fecha_fin = f"{año_sel}-{mes_sel}-{str(dia_actual).zfill(2)}"

        fecha_inicio = f"{año_sel}-{mes_sel}-01"
        # --- FIN DE LA NUEVA LÓGICA ---

        # Obtener metas del mes seleccionado desde la sesión
        metas_historicas = gs_manager.read_metas_por_linea()
        metas_del_mes_raw = metas_historicas.get(mes_seleccionado, {}).get('metas', {})
        metas_ipn_del_mes_raw = metas_historicas.get(mes_seleccionado, {}).get('metas_ipn', {})
        
        # Consolidar metas de GENVET con TERCEROS
        metas_del_mes = {}
        metas_ipn_del_mes = {}
        
        for linea_id, valor in metas_del_mes_raw.items():
            if linea_id == 'genvet':
                # Sumar la meta de genvet a terceros
                metas_del_mes['terceros'] = metas_del_mes.get('terceros', 0) + valor
            else:
                metas_del_mes[linea_id] = valor
        
        for linea_id, valor in metas_ipn_del_mes_raw.items():
            if linea_id == 'genvet':
                # Sumar la meta IPN de genvet a terceros
                metas_ipn_del_mes['terceros'] = metas_ipn_del_mes.get('terceros', 0) + valor
            else:
                metas_ipn_del_mes[linea_id] = valor
        
        # Las líneas comerciales se generan dinámicamente más adelante.
        
        # Obtener datos reales de ventas desde Odoo
        try:
            # Las fechas de inicio y fin ahora se calculan más arriba
            
            # Obtener datos de ventas reales desde Odoo
            sales_data = data_manager.get_sales_lines(
                date_from=fecha_inicio,
                date_to=fecha_fin,
                limit=10000
            )
            
            print(f"📊 Obtenidas {len(sales_data)} líneas de ventas para el dashboard")
            
        except Exception as e:
            print(f"⚠️ Error obteniendo datos de Odoo: {e}")
            sales_data = []
        
        # Procesar datos de ventas por línea comercial
        datos_lineas = []
        total_venta = 0
        total_vencimiento = 0
        total_venta_pn = 0
        
        # --- CÁLCULO DE TOTALES ---
        # Calcular totales de metas ANTES de filtrar las líneas para la tabla.
        # Esto asegura que ECOMMERCE se incluya en el total general del KPI.
        total_meta = sum(metas_del_mes.values())
        total_meta_pn = sum(metas_ipn_del_mes.values())
        
        # Mapeo de líneas comerciales de Odoo a IDs locales
        mapeo_lineas = {
            'PETMEDICA': 'petmedica',
            'AGROVET': 'agrovet', 
            'PET NUTRISCIENCE': 'pet_nutriscience',
            'AVIVET': 'avivet',
            'OTROS': 'otros',
            'TERCEROS': 'terceros',
            'INTERPET': 'interpet',
        }
        
        # Calcular ventas reales por línea comercial
        ventas_por_linea = {}
        ventas_por_ruta = {}
        ventas_ipn_por_linea = {} # Nueva variable para ventas de productos nuevos
        ventas_por_producto = {}
        ciclo_vida_por_producto = {}
        ventas_por_ciclo_vida = {}
        ventas_por_forma = {}
        for sale in sales_data:
            # Excluir VENTA INTERNACIONAL (exportaciones)
            linea_comercial = sale.get('commercial_line_national_id')
            nombre_linea_actual = None
            if linea_comercial and isinstance(linea_comercial, list) and len(linea_comercial) > 1:
                nombre_linea_original = linea_comercial[1].upper()
                if 'VENTA INTERNACIONAL' in nombre_linea_original:
                    continue
                # Aplicar normalización para agrupar GENVET y MARCA BLANCA como TERCEROS
                nombre_linea_actual = normalizar_linea_comercial(nombre_linea_original)
            
            # También filtrar por canal de ventas
            canal_ventas = sale.get('sales_channel_id')
            if canal_ventas and isinstance(canal_ventas, list) and len(canal_ventas) > 1:
                nombre_canal = canal_ventas[1].upper()
                if 'VENTA INTERNACIONAL' in nombre_canal or 'INTERNACIONAL' in nombre_canal:
                    continue
            
            # Procesar el balance de la venta
            balance_float = float(sale.get('balance', 0))
            if balance_float != 0:
                
                # Sumar a ventas totales por línea
                if nombre_linea_actual:
                    ventas_por_linea[nombre_linea_actual] = ventas_por_linea.get(nombre_linea_actual, 0) + balance_float
                
                # LÓGICA FINAL: Sumar si la RUTA (route_id) coincide con los valores especificados
                ruta = sale.get('route_id')
                # Se cambia la comparación al ID de la ruta (ruta[0]) para evitar problemas con traducciones.
                if isinstance(ruta, list) and len(ruta) > 0 and ruta[0] in [18, 19]:
                    if nombre_linea_actual:
                        ventas_por_ruta[nombre_linea_actual] = ventas_por_ruta.get(nombre_linea_actual, 0) + balance_float
                
                # Sumar a ventas de productos nuevos (IPN) - Lógica restaurada
                ciclo_vida = sale.get('product_life_cycle')
                if ciclo_vida and ciclo_vida == 'nuevo':
                    if nombre_linea_actual:
                        ventas_ipn_por_linea[nombre_linea_actual] = ventas_ipn_por_linea.get(nombre_linea_actual, 0) + balance_float
                
                # Agrupar por producto para Top 7
                producto_nombre = sale.get('name', '').strip()
                if producto_nombre:
                    # Limpiar nombres de ATREVIA eliminando indicadores de tamaño/presentación
                    producto_nombre_limpio = limpiar_nombre_atrevia(producto_nombre)
                    ventas_por_producto[producto_nombre_limpio] = ventas_por_producto.get(producto_nombre_limpio, 0) + balance_float
                    if producto_nombre_limpio not in ciclo_vida_por_producto:
                        ciclo_vida_por_producto[producto_nombre_limpio] = ciclo_vida
                
                # Agrupar por ciclo de vida para el gráfico de dona
                ciclo_vida_grafico = ciclo_vida if ciclo_vida else 'No definido'
                ventas_por_ciclo_vida[ciclo_vida_grafico] = ventas_por_ciclo_vida.get(ciclo_vida_grafico, 0) + balance_float

        print(f"💰 Ventas por línea comercial: {ventas_por_linea}")
        print(f"📦 Ventas por Vencimiento (Ciclo de Vida): {ventas_por_ruta}")
        print(f"✨ Ventas IPN (Productos Nuevos): {ventas_ipn_por_linea}")

        # --- Procesamiento de datos para gráficos (después del bucle) ---

        # 1. Procesar datos para la tabla principal
        # Generar dinámicamente las líneas comerciales a partir de ventas y metas
        all_lines = {}  # Usar un dict para evitar duplicados, con el id como clave

        # Añadir líneas desde las ventas reales
        for nombre_linea_venta in ventas_por_linea.keys():
            linea_id = nombre_linea_venta.lower().replace(' ', '_')
            all_lines[linea_id] = {'nombre': nombre_linea_venta.upper(), 'id': linea_id}

        # Añadir líneas desde las metas (para aquellas que no tuvieron ventas)
        for linea_id_meta in metas_del_mes.keys():
            # Convertir genvet a terceros si existe en las metas
            if linea_id_meta == 'genvet':
                linea_id_meta = 'terceros'
            
            if linea_id_meta not in all_lines:
                # Reconstruir el nombre desde el ID de la meta
                nombre_reconstruido = linea_id_meta.replace('_', ' ').upper()
                all_lines[linea_id_meta] = {'nombre': nombre_reconstruido, 'id': linea_id_meta}
        
        # Convertir el diccionario de líneas a una lista ordenada por nombre
        lineas_comerciales_dinamicas = sorted(all_lines.values(), key=lambda x: x['nombre'])

        # Excluir líneas no deseadas que pueden venir de los datos
        lineas_a_excluir = ['LICITACION', 'NINGUNO', 'ECOMMERCE', 'GENVET', 'MARCA BLANCA']
        lineas_comerciales_filtradas = [
            linea for linea in lineas_comerciales_dinamicas
            if linea['nombre'].upper() not in lineas_a_excluir
        ]

        # Pre-calcular la venta total para el cálculo de porcentajes
        total_venta = sum(ventas_por_linea.values())
        total_venta_calculado = total_venta # Renombrar para claridad en el bucle
        
        print(f"🔍 DEBUG: lineas_comerciales_filtradas = {[l['nombre'] for l in lineas_comerciales_filtradas]}")
        print(f"🔍 DEBUG: total_venta = {total_venta}")

        for linea in lineas_comerciales_filtradas:
            meta = metas_del_mes.get(linea['id'], 0)
            nombre_linea = linea['nombre'].upper()
            
            # Usar ventas reales de Odoo
            venta = ventas_por_linea.get(nombre_linea, 0)
            print(f"🔍 DEBUG BUCLE: {nombre_linea} - meta={meta}, venta={venta}")
            
            # Usar la meta IPN registrada por el usuario
            meta_pn = metas_ipn_del_mes.get(linea['id'], 0)
            venta_pn = ventas_ipn_por_linea.get(nombre_linea, 0) # Usar el cálculo real de ventas de productos nuevos
            vencimiento = ventas_por_ruta.get(nombre_linea, 0) # Usamos el nuevo cálculo
            
            porcentaje_total = (venta / meta * 100) if meta > 0 else 0
            porcentaje_pn = (venta_pn / meta_pn * 100) if meta_pn > 0 else 0
            porcentaje_sobre_total = (venta / total_venta_calculado * 100) if total_venta_calculado > 0 else 0

            datos_lineas.append({
                'nombre': linea['nombre'],
                'meta': meta,
                'venta': venta, # Ahora es positivo
                'porcentaje_total': porcentaje_total,
                'porcentaje_sobre_total': porcentaje_sobre_total,
                'meta_pn': meta_pn,
                'venta_pn': venta_pn,
                'porcentaje_pn': porcentaje_pn,
                'vencimiento_6_meses': vencimiento
            })
            
            # Los totales de metas ya se calcularon. Aquí solo sumamos los totales de ventas.
            total_venta_pn += venta_pn
            total_vencimiento += vencimiento
        
        # --- 2. Calcular KPIs ---
        # Días laborables restantes (Lunes a Sábado)
        dias_restantes = 0
        ritmo_diario_requerido = 0
        if mes_seleccionado == fecha_actual.strftime('%Y-%m'):
            hoy = fecha_actual.day
            ultimo_dia_mes = calendar.monthrange(año_seleccionado, fecha_actual.month)[1]
            for dia in range(hoy, ultimo_dia_mes + 1):
                # weekday() -> Lunes=0, Domingo=6
                if datetime(año_seleccionado, fecha_actual.month, dia).weekday() < 6:
                    dias_restantes += 1
            
            porcentaje_restante = 100 - ((total_venta / total_meta * 100) if total_meta > 0 else 100)
            if porcentaje_restante > 0 and dias_restantes > 0:
                ritmo_diario_requerido = porcentaje_restante / dias_restantes

        # Calcular KPIs
        kpis = {
            'meta_total': total_meta,
            'venta_total': total_venta,
            'porcentaje_avance': (total_venta / total_meta * 100) if total_meta > 0 else 0,
            'meta_ipn': total_meta_pn,
            'venta_ipn': total_venta_pn,
            'porcentaje_avance_ipn': (total_venta_pn / total_meta_pn * 100) if total_meta_pn > 0 else 0,
            'vencimiento_6_meses': total_vencimiento,
            'avance_diario_total': ((total_venta / total_meta * 100) / dia_actual) if total_meta > 0 and dia_actual > 0 else 0,
            'avance_diario_ipn': ((total_venta_pn / total_meta_pn * 100) / dia_actual) if total_meta_pn > 0 and dia_actual > 0 else 0,
            'ritmo_diario_requerido': ritmo_diario_requerido
        }

        # --- Avance lineal: proyección de cierre y faltante ---
        # Proyección mensual lineal: proyectar ventas actuales al mes completo
        try:
            dias_en_mes = calendar.monthrange(int(año_sel), int(mes_sel))[1]
        except Exception:
            dias_en_mes = 30

        if dia_actual > 0:
            proyeccion_mensual = (total_venta / dia_actual) * dias_en_mes
        else:
            proyeccion_mensual = 0

        avance_lineal_pct = (proyeccion_mensual / total_meta * 100) if total_meta > 0 else 0
        faltante_meta = max(total_meta - total_venta, 0)

        # Cálculos específicos para IPN (usando las variables ya calculadas)
        # total_meta_pn ya está calculado arriba
        # total_venta_pn ya está calculado arriba
        
        # Proyección lineal IPN
        if dia_actual > 0:
            promedio_diario_ipn = total_venta_pn / dia_actual
            proyeccion_mensual_ipn = promedio_diario_ipn * dias_en_mes
        else:
            proyeccion_mensual_ipn = 0

        avance_lineal_ipn_pct = (proyeccion_mensual_ipn / total_meta_pn * 100) if total_meta_pn > 0 else 0
        faltante_meta_ipn = max(total_meta_pn - total_venta_pn, 0)

        
        # 3. Ordenar productos para el gráfico Top 7
        # Ordenar productos por ventas y tomar los top 7
        productos_ordenados = sorted(ventas_por_producto.items(), key=lambda x: x[1], reverse=True)[:7]
        
        datos_productos = []
        for nombre_producto, venta in productos_ordenados:
            datos_productos.append({
                'nombre': nombre_producto,
                'venta': venta,
                'ciclo_vida': ciclo_vida_por_producto.get(nombre_producto, 'No definido')
            })
        
        print(f"🏆 Top 7 productos por ventas: {[p['nombre'] for p in datos_productos]}")
        
        # 4. Ordenar datos para el gráfico de Ciclo de Vida
        # Convertir a lista ordenada por ventas
        datos_ciclo_vida = []
        for ciclo, venta in sorted(ventas_por_ciclo_vida.items(), key=lambda x: x[1], reverse=True):
            datos_ciclo_vida.append({
                'ciclo': ciclo,
                'venta': venta
            })
        
        print(f"📈 Ventas por Ciclo de Vida: {datos_ciclo_vida}")
        
        # --- INICIO: LÓGICA PARA LA TABLA DEL EQUIPO ECOMMERCE ---
        datos_ecommerce = []
        kpis_ecommerce = {'meta_total': 0, 'venta_total': 0, 'porcentaje_avance': 0}

        # 1. Obtener miembros y metas del equipo ECOMMERCE
        equipos_guardados = gs_manager.read_equipos()        
        ecommerce_vendor_ids = [str(vid) for vid in equipos_guardados.get('ecommerce', [])]
        
        if ecommerce_vendor_ids:
            # 2. Obtener la meta total de ECOMMERCE desde las metas por línea
            meta_ecommerce = metas_del_mes.get('ecommerce', 0)
            kpis_ecommerce['meta_total'] = meta_ecommerce

            # 3. Calcular ventas del equipo ECOMMERCE, agrupadas por LÍNEA COMERCIAL
            ventas_por_linea_ecommerce = {}
            for sale in sales_data:
                user_info = sale.get('invoice_user_id')
                if user_info and isinstance(user_info, list) and len(user_info) > 1:
                    vendedor_id = str(user_info[0])
                    # Si la venta pertenece a un vendedor de ECOMMERCE
                    if vendedor_id in ecommerce_vendor_ids:
                        balance = float(sale.get('balance', 0))
                        
                        # Agrupar por línea comercial con normalización
                        linea_info = sale.get('commercial_line_national_id')
                        linea_nombre = 'N/A'
                        if linea_info and isinstance(linea_info, list) and len(linea_info) > 1:
                            linea_nombre_original = linea_info[1].upper()
                            # Aplicar normalización para agrupar GENVET y MARCA BLANCA como TERCEROS
                            linea_nombre = normalizar_linea_comercial(linea_nombre_original)
                        
                        ventas_por_linea_ecommerce[linea_nombre] = ventas_por_linea_ecommerce.get(linea_nombre, 0) + balance

            # 4. Construir la tabla de datos para la plantilla
            for linea, venta in ventas_por_linea_ecommerce.items():
                datos_ecommerce.append({
                    'nombre': linea, # Ahora es el nombre de la línea comercial
                    'venta': venta
                })
                kpis_ecommerce['venta_total'] += venta

            # 5. Calcular el porcentaje de avance total del equipo
            if kpis_ecommerce['meta_total'] > 0:
                kpis_ecommerce['porcentaje_avance'] = (kpis_ecommerce['venta_total'] / kpis_ecommerce['meta_total']) * 100

            # 6. Calcular el porcentaje de participación de cada línea sobre el total del equipo
            if kpis_ecommerce['venta_total'] > 0:
                for linea_data in datos_ecommerce:
                    linea_data['porcentaje_sobre_total'] = (linea_data['venta'] / kpis_ecommerce['venta_total']) * 100
            else:
                for linea_data in datos_ecommerce:
                    linea_data['porcentaje_sobre_total'] = 0

            # Ordenar las líneas por venta descendente
            datos_ecommerce = sorted(datos_ecommerce, key=lambda x: x['venta'], reverse=True)

        # --- FIN: LÓGICA PARA LA TABLA DEL EQUIPO ECOMMERCE ---

        # Ordenar los datos de la tabla por venta descendente
        datos_lineas_tabla_sorted = sorted(datos_lineas, key=lambda x: x['venta'], reverse=True)
        
        print(f"🔍 DEBUG: datos_lineas tiene {len(datos_lineas)} elementos")
        print(f"🔍 DEBUG: datos_lineas_tabla_sorted tiene {len(datos_lineas_tabla_sorted)} elementos")
        if len(datos_lineas_tabla_sorted) > 0:
            print(f"🔍 DEBUG: Primera línea: {datos_lineas_tabla_sorted[0]}")

        return render_template('dashboard_clean.html',
                             meses_disponibles=meses_disponibles,
                             mes_seleccionado=mes_seleccionado,
                             mes_nombre=mes_nombre,
                             dia_actual=dia_actual,
                             años_disponibles=años_disponibles,
                             año_seleccionado=año_seleccionado,
                             kpis=kpis,
                             datos_lineas=datos_lineas, # Para gráficos, mantener el orden original (alfabético por nombre)
                             datos_lineas_tabla=datos_lineas_tabla_sorted, # Para la tabla, usar los datos ordenados por venta
                             datos_productos=datos_productos,
                             datos_ciclo_vida=datos_ciclo_vida if 'datos_ciclo_vida' in locals() else [],
                             fecha_actual=fecha_actual,
                             avance_lineal_pct=avance_lineal_pct,
                             faltante_meta=faltante_meta,
                             avance_lineal_ipn_pct=avance_lineal_ipn_pct,
                             faltante_meta_ipn=faltante_meta_ipn,
                             datos_ecommerce=datos_ecommerce,
                             kpis_ecommerce=kpis_ecommerce,
                             is_admin=is_admin) # Pasar el flag a la plantilla
    
    except Exception as e:
        print(f"❌ ERROR CAPTURADO: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error al obtener datos del dashboard: {str(e)}', 'danger')
        
        # Crear datos por defecto para evitar errores
        fecha_actual = datetime.now()
        kpis_default = {
            'meta_total': 0,
            'venta_total': 0,
            'porcentaje_avance': 0,
            'meta_ipn': 0,
            'venta_ipn': 0,
            'porcentaje_avance_ipn': 0,
            'vencimiento_6_meses': 0,
            'avance_diario_total': 0,
            'avance_diario_ipn': 0
        }
        
        return render_template('dashboard_clean.html',
                             meses_disponibles=[{
                                 'key': fecha_actual.strftime('%Y-%m'),
                                 'nombre': f"{fecha_actual.strftime('%B')} {fecha_actual.year}"
                             }],
                             mes_seleccionado=fecha_actual.strftime('%Y-%m'),
                             mes_nombre=f"{fecha_actual.strftime('%B').upper()} {fecha_actual.year}",
                             dia_actual=fecha_actual.day,
                             años_disponibles=list(range(2025, fecha_actual.year + 1)),
                             año_seleccionado=fecha_actual.year,
                             kpis=kpis_default,
                             datos_lineas=[], # Se mantiene vacío en caso de error
                             datos_lineas_tabla=[],
                             datos_productos=[],
                             datos_ciclo_vida=[],
                             fecha_actual=fecha_actual,
                             avance_lineal_pct=0,
                             faltante_meta=0,
                             datos_ecommerce=[],
                             kpis_ecommerce={},
                             is_admin=is_admin) # Pasar el flag a la plantilla


@app.route('/dashboard_linea')
def dashboard_linea():
    if 'username' not in session:
        return redirect(url_for('login'))

    # --- Lógica de Permisos de Administrador ---
    admin_users = ["jonathan.cerda@agrovetmarket.com", "janet.hueza@agrovetmarket.com", "juan.portal@agrovetmarket.com", "AMAHOdoo@agrovetmarket.com"]
    is_admin = session.get('username') in admin_users

    try:
        # --- 1. OBTENER FILTROS ---
        fecha_actual = datetime.now()
        mes_seleccionado = request.args.get('mes', fecha_actual.strftime('%Y-%m'))
        año_actual = fecha_actual.year
        meses_disponibles = get_meses_del_año(año_actual)

        linea_seleccionada_nombre = request.args.get('linea_nombre', 'PETMEDICA') # Default a PETMEDICA si no se especifica

        # --- NUEVA LÓGICA DE FILTRADO POR DÍA ---
        dia_fin_param = request.args.get('dia_fin')
        año_sel, mes_sel = mes_seleccionado.split('-')

        if dia_fin_param:
            try:
                dia_actual = int(dia_fin_param)
                fecha_fin = f"{año_sel}-{mes_sel}-{str(dia_actual).zfill(2)}"
            except (ValueError, TypeError):
                dia_fin_param = None
        
        if not dia_fin_param:
            if mes_seleccionado == fecha_actual.strftime('%Y-%m'):
                dia_actual = fecha_actual.day
            else:
                ultimo_dia_mes = calendar.monthrange(int(año_sel), int(mes_sel))[1]
                dia_actual = ultimo_dia_mes
            fecha_fin = f"{año_sel}-{mes_sel}-{str(dia_actual).zfill(2)}"
        
        fecha_inicio = f"{año_sel}-{mes_sel}-01"
        # --- FIN DE LA NUEVA LÓGICA ---

        # Mapeo de nombre de línea a ID para cargar metas
        mapeo_nombre_a_id = {
            'PETMEDICA': 'petmedica', 'AGROVET': 'agrovet', 'PET NUTRISCIENCE': 'pet_nutriscience',
            'AVIVET': 'avivet', 'OTROS': 'otros',
            'TERCEROS': 'terceros', 'INTERPET': 'interpet',
        }
        linea_seleccionada_id = mapeo_nombre_a_id.get(linea_seleccionada_nombre.upper(), 'petmedica')

        # --- 2. OBTENER DATOS ---
        # fecha_inicio y fecha_fin se calculan arriba usando la lógica de dia_fin.
        # Asegurar que fecha_inicio siempre esté definida
        año_sel, mes_sel = mes_seleccionado.split('-')
        fecha_inicio = f"{año_sel}-{mes_sel}-01"
        # Si no se definió fecha_fin arriba (por alguna razón), usar el último día del mes
        if 'fecha_fin' not in locals():
            ultimo_dia = calendar.monthrange(int(año_sel), int(mes_sel))[1]
            fecha_fin = f"{año_sel}-{mes_sel}-{ultimo_dia}"

        # Cargar metas de vendedores para el mes y línea seleccionados
        # La estructura es metas[equipo_id][vendedor_id][mes_key]
        metas_vendedores_historicas = gs_manager.read_metas()
        # 1. Obtener todas las metas del equipo/línea
        metas_del_equipo = metas_vendedores_historicas.get(linea_seleccionada_id, {})

        # Obtener todos los vendedores de Odoo
        todos_los_vendedores = {str(v['id']): v['name'] for v in data_manager.get_all_sellers()}

        # Obtener ventas del mes
        sales_data = data_manager.get_sales_lines(
            date_from=fecha_inicio,
            date_to=fecha_fin,
            limit=10000
        )

        # --- PRE-FILTRAR VENTAS INTERNACIONALES PARA EFICIENCIA ---
        sales_data_processed = []
        for sale in sales_data:
            # Excluir VENTA INTERNACIONAL (exportaciones) por línea comercial
            linea_comercial = sale.get('commercial_line_national_id')
            if linea_comercial and isinstance(linea_comercial, list) and len(linea_comercial) > 1:
                if 'VENTA INTERNACIONAL' in linea_comercial[1].upper():
                    continue
            
            # Excluir VENTA INTERNACIONAL por canal de ventas
            canal_ventas = sale.get('sales_channel_id')
            if canal_ventas and isinstance(canal_ventas, list) and len(canal_ventas) > 1:
                nombre_canal = canal_ventas[1].upper()
                if 'VENTA INTERNACIONAL' in nombre_canal or 'INTERNACIONAL' in nombre_canal:
                    continue
            
            sales_data_processed.append(sale)

        # --- 3. PROCESAR Y AGREGAR DATOS POR VENDEDOR ---
        ventas_por_vendedor = {}
        ventas_ipn_por_vendedor = {}
        ventas_vencimiento_por_vendedor = {}
        ventas_por_producto = {}
        ventas_por_ciclo_vida = {}
        ventas_por_forma = {}
        ajustes_sin_vendedor = 0 # Para notas de crédito sin vendedor
        nombres_vendedores_con_ventas = {} # BUGFIX: Guardar nombres de vendedores con ventas

        for sale in sales_data_processed: # Usar los datos pre-filtrados
            linea_comercial = sale.get('commercial_line_national_id')
            if linea_comercial and isinstance(linea_comercial, list) and len(linea_comercial) > 1:
                nombre_linea_original = linea_comercial[1].upper()
                # Aplicar normalización para agrupar GENVET y MARCA BLANCA como TERCEROS
                nombre_linea_actual = normalizar_linea_comercial(nombre_linea_original)

                # Filtrar por la línea comercial seleccionada
                if nombre_linea_actual == linea_seleccionada_nombre.upper():
                    balance = float(sale.get('balance', 0))
                    user_info = sale.get('invoice_user_id')

                    # Si hay un vendedor asignado, se procesa normalmente
                    if user_info and isinstance(user_info, list) and len(user_info) > 1:
                        vendedor_id = str(user_info[0])
                        nombres_vendedores_con_ventas[vendedor_id] = user_info[1] # Guardar el nombre

                        # Agrupar ventas totales
                        ventas_por_vendedor[vendedor_id] = ventas_por_vendedor.get(vendedor_id, 0) + balance

                        # Agrupar ventas IPN
                        if sale.get('product_life_cycle') == 'nuevo':
                            ventas_ipn_por_vendedor[vendedor_id] = ventas_ipn_por_vendedor.get(vendedor_id, 0) + balance
                        
                        # Agrupar ventas por vencimiento < 6 meses
                        ruta = sale.get('route_id')
                        if isinstance(ruta, list) and len(ruta) > 0 and ruta[0] in [18, 19]:
                            ventas_vencimiento_por_vendedor[vendedor_id] = ventas_vencimiento_por_vendedor.get(vendedor_id, 0) + balance
                    
                    # Si NO hay vendedor, se agrupa como un ajuste (ej. Nota de Crédito)
                    else:
                        ajustes_sin_vendedor += balance

                    # Agrupar para gráficos (Top Productos, Ciclo Vida, Forma Farmacéutica)
                    # Esto se hace para todas las transacciones de la línea, con o sin vendedor
                    producto_nombre = sale.get('name', '').strip()
                    if producto_nombre:
                        # Limpiar nombres de ATREVIA eliminando indicadores de tamaño/presentación
                        producto_nombre_limpio = limpiar_nombre_atrevia(producto_nombre)
                        ventas_por_producto[producto_nombre_limpio] = ventas_por_producto.get(producto_nombre_limpio, 0) + balance

                    ciclo_vida = sale.get('product_life_cycle', 'No definido')
                    ventas_por_ciclo_vida[ciclo_vida] = ventas_por_ciclo_vida.get(ciclo_vida, 0) + balance

                    forma_farma = sale.get('pharmaceutical_forms_id')
                    nombre_forma = forma_farma[1] if forma_farma and len(forma_farma) > 1 else 'Instrumental'
                    ventas_por_forma[nombre_forma] = ventas_por_forma.get(nombre_forma, 0) + balance

        # --- 4. CONSTRUIR ESTRUCTURA DE DATOS PARA LA PLANTILLA ---
        datos_vendedores = []
        total_meta = 0
        total_venta = 0
        total_meta_ipn = 0
        total_venta_ipn = 0
        total_vencimiento = 0

        # --- 4.1. UNIFICAR VENDEDORES ---
        # Combinar los vendedores oficiales del equipo con los que tuvieron ventas reales en la línea.
        # Esto asegura que mostremos a todos los miembros del equipo (incluso con 0 ventas)
        # y también a cualquier otra persona que haya vendido en esta línea sin ser miembro oficial.
        equipos_guardados = gs_manager.read_equipos()
        miembros_oficiales_ids = {str(vid) for vid in equipos_guardados.get(linea_seleccionada_id, [])}
        vendedores_con_ventas_ids = set(ventas_por_vendedor.keys())
        
        todos_los_vendedores_a_mostrar_ids = sorted(list(miembros_oficiales_ids | vendedores_con_ventas_ids))

        # --- 4.2. CONSTRUIR LA TABLA DE VENDEDORES ---
        for vendedor_id in todos_los_vendedores_a_mostrar_ids:
            # BUGFIX: Priorizar el nombre de la venta, luego la lista general, y como último recurso el ID.
            vendedor_nombre = nombres_vendedores_con_ventas.get(vendedor_id, 
                                todos_los_vendedores.get(vendedor_id, f"Vendedor ID {vendedor_id}"))

            
            # Obtener ventas (será 0 si es un miembro oficial sin ventas)
            venta = ventas_por_vendedor.get(vendedor_id, 0)
            venta_ipn = ventas_ipn_por_vendedor.get(vendedor_id, 0)
            vencimiento = ventas_vencimiento_por_vendedor.get(vendedor_id, 0)

            # Asignar meta SOLO si el vendedor es un miembro oficial del equipo
            meta = 0
            meta_ipn = 0
            if vendedor_id in miembros_oficiales_ids:
                meta_guardada = metas_del_equipo.get(vendedor_id, {}).get(mes_seleccionado, {})
                meta = float(meta_guardada.get('meta', 0))
                meta_ipn = float(meta_guardada.get('meta_ipn', 0))

            # Añadir la fila del vendedor a la tabla
            datos_vendedores.append({
                'id': vendedor_id,
                'nombre': vendedor_nombre,
                'meta': meta,
                'venta': venta,
                'porcentaje_avance': (venta / meta * 100) if meta > 0 else 0,
                'meta_ipn': meta_ipn,
                'venta_ipn': venta_ipn,
                'porcentaje_avance_ipn': (venta_ipn / meta_ipn * 100) if meta_ipn > 0 else 0,
                'vencimiento_6_meses': vencimiento
            })

            # Sumar a los totales generales de la línea.
            # La meta solo se suma si fue asignada (es decir, si es miembro oficial).
            # La venta se suma siempre.
            total_meta += meta
            total_venta += venta
            total_meta_ipn += meta_ipn
            total_venta_ipn += venta_ipn
            total_vencimiento += vencimiento

        # --- 4.3. AÑADIR AJUSTES SIN VENDEDOR ---
        if ajustes_sin_vendedor != 0:
            datos_vendedores.append({
                'id': 'ajustes',
                'nombre': 'Ajustes y Notas de Crédito (Sin Vendedor)',
                'meta': 0, 'venta': ajustes_sin_vendedor, 'porcentaje_avance': 0,
                'meta_ipn': 0, 'venta_ipn': 0, 'porcentaje_avance_ipn': 0,
                'vencimiento_6_meses': 0
            })
            # Sumar los ajustes al total de ventas de la línea
            total_venta += ajustes_sin_vendedor

        # Añadir porcentaje sobre el total a cada vendedor
        if total_venta > 0:
            for v in datos_vendedores:
                v['porcentaje_sobre_total'] = (v.get('venta', 0) / total_venta) * 100
        else:
            for v in datos_vendedores:
                v['porcentaje_sobre_total'] = 0

        # --- 4.4. FILTRAR VENDEDORES CON VENTA NEGATIVA ---
        # Si un vendedor solo tiene notas de crédito (venta < 0), no se muestra en la tabla,
        # pero su valor ya fue sumado (restado) al total_venta para mantener la consistencia.
        datos_vendedores_final = [v for v in datos_vendedores if v['venta'] >= 0 or v['id'] == 'ajustes']

        # Ordenar por venta descendente
        datos_vendedores_final = sorted(datos_vendedores_final, key=lambda x: x['venta'], reverse=True)

        # --- 5. CALCULAR KPIs DE LÍNEA ---
        ritmo_diario_requerido_linea = 0
        if mes_seleccionado == fecha_actual.strftime('%Y-%m'):
            hoy = fecha_actual.day
            ultimo_dia_mes = calendar.monthrange(año_actual, fecha_actual.month)[1]
            dias_restantes = 0
            for dia in range(hoy, ultimo_dia_mes + 1):
                if datetime(año_actual, fecha_actual.month, dia).weekday() < 6: # L-S
                    dias_restantes += 1
            
            porcentaje_restante = 100 - ((total_venta / total_meta * 100) if total_meta > 0 else 100)
            if porcentaje_restante > 0 and dias_restantes > 0:
                ritmo_diario_requerido_linea = porcentaje_restante / dias_restantes

        # KPIs generales para la línea
        kpis = {
            'meta_total': total_meta,
            'venta_total': total_venta,
            'porcentaje_avance': (total_venta / total_meta * 100) if total_meta > 0 else 0,
            'meta_ipn': total_meta_ipn,
            'venta_ipn': total_venta_ipn,
            'porcentaje_avance_ipn': (total_venta_ipn / total_meta_ipn * 100) if total_meta_ipn > 0 else 0,
            'vencimiento_6_meses': total_vencimiento,
            'avance_diario_total': ((total_venta / total_meta * 100) / dia_actual) if total_meta > 0 and dia_actual > 0 else 0,
            'avance_diario_ipn': ((total_venta_ipn / total_meta_ipn * 100) / dia_actual) if total_meta_ipn > 0 and dia_actual > 0 else 0,
            'ritmo_diario_requerido': ritmo_diario_requerido_linea
        }

        # --- Avance lineal específico de la línea: proyección de cierre y faltante ---
        try:
            dias_en_mes = calendar.monthrange(int(año_sel), int(mes_sel))[1]
        except Exception:
            dias_en_mes = 30

        if dia_actual > 0:
            proyeccion_mensual_linea = (total_venta / dia_actual) * dias_en_mes
        else:
            proyeccion_mensual_linea = 0

        avance_lineal_pct = (proyeccion_mensual_linea / total_meta * 100) if total_meta > 0 else 0
        faltante_meta = max(total_meta - total_venta, 0)

        # Cálculos específicos para IPN de la línea
        if dia_actual > 0:
            promedio_diario_ipn_linea = total_venta_ipn / dia_actual
            proyeccion_mensual_ipn_linea = promedio_diario_ipn_linea * dias_en_mes
        else:
            proyeccion_mensual_ipn_linea = 0

        avance_lineal_ipn_pct = (proyeccion_mensual_ipn_linea / total_meta_ipn * 100) if total_meta_ipn > 0 else 0
        faltante_meta_ipn = max(total_meta_ipn - total_venta_ipn, 0)

        # Datos para gráficos
        productos_ordenados = sorted(ventas_por_producto.items(), key=lambda x: x[1], reverse=True)[:7]
        datos_productos = [{'nombre': n, 'venta': v} for n, v in productos_ordenados]

        datos_ciclo_vida = [{'ciclo': c, 'venta': v} for c, v in ventas_por_ciclo_vida.items()]
        datos_forma_farmaceutica = [{'forma': f, 'venta': v} for f, v in ventas_por_forma.items()]

        # --- LÓGICA MEJORADA PARA OBTENER LÍNEAS COMERCIALES DISPONIBLES ---
        # Replicar la misma lógica del dashboard principal para consistencia.
        
        # 1. Obtener metas del mes para incluir líneas con metas pero sin ventas.
        metas_historicas = gs_manager.read_metas_por_linea()
        metas_del_mes = metas_historicas.get(mes_seleccionado, {}).get('metas', {})
        
        # 2. Unificar líneas desde ventas y metas.
        all_lines_dict = {}

        # Desde ventas (aplicando normalización)
        for sale in sales_data_processed: # Usar datos ya filtrados de ventas internacionales
            linea_obj = sale.get('commercial_line_national_id')
            if linea_obj and isinstance(linea_obj, list) and len(linea_obj) > 1:
                linea_nombre_original = linea_obj[1].upper()
                # Aplicar normalización para agrupar GENVET y MARCA BLANCA como TERCEROS
                linea_nombre = normalizar_linea_comercial(linea_nombre_original)
                if linea_nombre not in all_lines_dict:
                    all_lines_dict[linea_nombre] = linea_nombre

        # Desde metas
        for linea_id_meta in metas_del_mes.keys():
            nombre_linea_meta = linea_id_meta.replace('_', ' ').upper()
            if nombre_linea_meta not in all_lines_dict:
                all_lines_dict[nombre_linea_meta] = nombre_linea_meta

        # 3. Filtrar y ordenar
        lineas_a_excluir = ['LICITACION', 'NINGUNO', 'ECOMMERCE', 'VENTA INTERNACIONAL']
        lineas_disponibles = sorted([nombre for nombre in all_lines_dict.values() if nombre not in lineas_a_excluir])
        # --- FIN DE LA LÓGICA MEJORADA ---
        return render_template('dashboard_linea.html',
                               linea_nombre=linea_seleccionada_nombre,
                               mes_seleccionado=mes_seleccionado,
                               meses_disponibles=meses_disponibles,
                               kpis=kpis,
                               datos_vendedores=datos_vendedores_final,
                               datos_productos=datos_productos,
                               datos_ciclo_vida=datos_ciclo_vida,
                               datos_forma_farmaceutica=datos_forma_farmaceutica,
                               lineas_disponibles=lineas_disponibles,
                               fecha_actual=fecha_actual,
                               dia_actual=dia_actual,
                               avance_lineal_pct=avance_lineal_pct,
                               faltante_meta=faltante_meta,
                               avance_lineal_ipn_pct=avance_lineal_ipn_pct,
                               faltante_meta_ipn=faltante_meta_ipn,
                               is_admin=is_admin) # Pasar el flag a la plantilla

    except Exception as e:
        flash(f'Error al generar el dashboard para la línea: {str(e)}', 'danger')
        # En caso de error, renderizar la plantilla con datos vacíos para no romper la UI
        fecha_actual = datetime.now()
        año_actual = fecha_actual.year
        meses_disponibles = get_meses_del_año(año_actual)
        linea_seleccionada_nombre = request.args.get('linea_nombre', 'PETMEDICA')
        lineas_disponibles = [
            'PETMEDICA', 'AGROVET', 'PET NUTRISCIENCE', 'AVIVET', 'OTROS', 'TERCEROS', 'INTERPET'
        ]
        dia_actual = fecha_actual.day
        kpis_default = {
            'meta_total': 0, 'venta_total': 0, 'porcentaje_avance': 0,
            'meta_ipn': 0, 'venta_ipn': 0, 'porcentaje_avance_ipn': 0,
            'vencimiento_6_meses': 0, 'avance_diario_total': 0, 'avance_diario_ipn': 0
        }
        
        return render_template('dashboard_linea.html',
                               linea_nombre=linea_seleccionada_nombre,
                               mes_seleccionado=fecha_actual.strftime('%Y-%m'),
                               meses_disponibles=meses_disponibles,
                               kpis=kpis_default,
                               datos_vendedores=[],
                               datos_productos=[],
                               datos_ciclo_vida=[],
                               datos_forma_farmaceutica=[],
                               lineas_disponibles=lineas_disponibles,
                               fecha_actual=fecha_actual,
                               dia_actual=dia_actual,
                               avance_lineal_pct=0,
                               faltante_meta=0,
                               avance_lineal_ipn_pct=0,
                               faltante_meta_ipn=0,
                               is_admin=is_admin) # Pasar el flag a la plantilla


@app.route('/meta', methods=['GET', 'POST'])
def meta():
    if 'username' not in session:
        return redirect(url_for('login'))

    # --- Verificación de Permisos ---
    admin_users = ["jonathan.cerda@agrovetmarket.com", "janet.hueza@agrovetmarket.com", "juan.portal@agrovetmarket.com", "AMAHOdoo@agrovetmarket.com"]
    is_admin = session.get('username') in admin_users
    if not is_admin:
        flash('No tienes permiso para acceder a esta página.', 'warning')
        return redirect(url_for('dashboard'))
    # --- Fin Verificación ---
    
    try:
        # Líneas comerciales estáticas de la empresa
        lineas_comerciales_estaticas = [
            {'nombre': 'PETMEDICA', 'id': 'petmedica'},
            {'nombre': 'AGROVET', 'id': 'agrovet'},
            {'nombre': 'PET NUTRISCIENCE', 'id': 'pet_nutriscience'},
            {'nombre': 'AVIVET', 'id': 'avivet'},
            {'nombre': 'OTROS', 'id': 'otros'},
            {'nombre': 'TERCEROS', 'id': 'terceros'},
            {'nombre': 'INTERPET', 'id': 'interpet'},
        ]
        
        # Obtener año actual y mes seleccionado
        fecha_actual = datetime.now()
        año_actual = fecha_actual.year
        mes_seleccionado = request.args.get('mes', fecha_actual.strftime('%Y-%m'))
        
        # Crear todos los meses del año actual
        meses_año = [{'es_actual': m['key'] == fecha_actual.strftime('%Y-%m'), **m} for m in get_meses_del_año(año_actual)]
        
        if request.method == 'POST':
            # Obtener el mes del formulario
            mes_formulario = request.form.get('mes_seleccionado', mes_seleccionado)
            
            # Procesar metas enviadas
            metas_data = {}
            metas_ipn_data = {}
            total_meta = 0
            total_meta_ipn = 0
            
            for linea in lineas_comerciales_estaticas:
                # Procesar Meta Total
                meta_value = request.form.get(f"meta_{linea['id']}", '0')
                try:
                    clean_value = str(meta_value).replace(',', '') if meta_value else '0'
                    valor = float(clean_value) if clean_value else 0.0
                    metas_data[linea['id']] = valor
                    total_meta += valor
                except (ValueError, TypeError):
                    metas_data[linea['id']] = 0.0
                
                # Procesar Meta IPN
                meta_ipn_value = request.form.get(f"meta_ipn_{linea['id']}", '0')
                try:
                    clean_value_ipn = str(meta_ipn_value).replace(',', '') if meta_ipn_value else '0'
                    valor_ipn = float(clean_value_ipn) if clean_value_ipn else 0.0
                    metas_ipn_data[linea['id']] = valor_ipn
                    total_meta_ipn += valor_ipn
                except (ValueError, TypeError):
                    metas_ipn_data[linea['id']] = 0.0
            
            # --- Procesar Meta ECOMMERCE (campo estático) ---
            # Procesar Meta Total ECOMMERCE
            meta_ecommerce_value = request.form.get('meta_ecommerce', '0')
            try:
                clean_value_ecommerce = str(meta_ecommerce_value).replace(',', '') if meta_ecommerce_value else '0'
                valor_ecommerce = float(clean_value_ecommerce) if clean_value_ecommerce else 0.0
                metas_data['ecommerce'] = valor_ecommerce
                total_meta += valor_ecommerce
            except (ValueError, TypeError):
                metas_data['ecommerce'] = 0.0

            # Procesar Meta IPN ECOMMERCE
            meta_ipn_ecommerce_value = request.form.get('meta_ipn_ecommerce', '0')
            try:
                clean_value_ipn_ecommerce = str(meta_ipn_ecommerce_value).replace(',', '') if meta_ipn_ecommerce_value else '0'
                valor_ipn_ecommerce = float(clean_value_ipn_ecommerce) if clean_value_ipn_ecommerce else 0.0
                metas_ipn_data['ecommerce'] = valor_ipn_ecommerce
                total_meta_ipn += valor_ipn_ecommerce
            except (ValueError, TypeError):
                metas_ipn_data['ecommerce'] = 0.0
            # --- Fin del procesamiento de ECOMMERCE ---

            # Encontrar el nombre del mes
            mes_obj = next((m for m in meses_año if m['key'] == mes_formulario), None)
            mes_nombre_formulario = mes_obj['nombre'] if mes_obj else ""
            
            metas_historicas = gs_manager.read_metas_por_linea()
            metas_historicas[mes_formulario] = {
                'metas': metas_data,
                'metas_ipn': metas_ipn_data,
                'total': total_meta,
                'total_ipn': total_meta_ipn,
                'mes_nombre': mes_nombre_formulario
            }
            gs_manager.write_metas_por_linea(metas_historicas)
            
            flash(f'Metas guardadas exitosamente para {mes_nombre_formulario}. Total: S/ {total_meta:,.0f}', 'success')
            
            # Actualizar mes seleccionado después de guardar
            mes_seleccionado = mes_formulario
        
        # Obtener todas las metas históricas
        metas_historicas = gs_manager.read_metas_por_linea()
        
        # Obtener metas y total del mes seleccionado
        metas_actuales = metas_historicas.get(mes_seleccionado, {}).get('metas', {})
        metas_ipn_actuales = metas_historicas.get(mes_seleccionado, {}).get('metas_ipn', {})
        total_actual = sum(metas_actuales.values()) if metas_actuales else 0
        total_ipn_actual = sum(metas_ipn_actuales.values()) if metas_ipn_actuales else 0
        
        # Encontrar el nombre del mes seleccionado
        mes_obj_seleccionado = next((m for m in meses_año if m['key'] == mes_seleccionado), meses_año[fecha_actual.month - 1])
        
        return render_template('meta.html',
                             lineas_comerciales=lineas_comerciales_estaticas,
                             metas_actuales=metas_actuales,
                             metas_ipn_actuales=metas_ipn_actuales,
                             metas_historicas=metas_historicas,
                             meses_año=meses_año,
                             mes_seleccionado=mes_seleccionado,
                             mes_nombre=mes_obj_seleccionado['nombre'],
                             total_actual=total_actual,
                             total_ipn_actual=total_ipn_actual,
                             fecha_actual=fecha_actual,
                             is_admin=is_admin) # Pasar el flag a la plantilla
    
    except Exception as e:
        flash(f'Error al procesar metas: {str(e)}', 'danger')
        return render_template('meta.html',
                             lineas_comerciales=[],
                             metas_actuales={},
                             metas_ipn_actuales={},
                             metas_historicas={},
                             meses_año=[],
                             mes_seleccionado="",
                             mes_nombre="",
                             total_actual=0,
                             total_ipn_actual=0,
                             fecha_actual=datetime.now(),
                             is_admin=is_admin) # Pasar el flag a la plantilla

@app.route('/export/excel/sales')
def export_excel_sales():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # Obtener filtros de la URL
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        linea_id = request.args.get('linea_id')
        partner_id = request.args.get('partner_id')
        
        # Convertir a tipos apropiados
        if linea_id:
            try:
                linea_id = int(linea_id)
            except (ValueError, TypeError):
                linea_id = None
        
        if partner_id:
            try:
                partner_id = int(partner_id)
            except (ValueError, TypeError):
                partner_id = None
        
        # Obtener datos
        sales_data = data_manager.get_sales_lines(
            date_from=date_from,
            date_to=date_to,
            partner_id=partner_id,
            linea_id=linea_id,
            limit=10000  # Más datos para export
        )
        
        # Filtrar VENTA INTERNACIONAL (exportaciones)
        sales_data_filtered = []
        for sale in sales_data:
            linea_comercial = sale.get('commercial_line_national_id')
            if linea_comercial and isinstance(linea_comercial, list) and len(linea_comercial) > 1:
                nombre_linea = linea_comercial[1].upper()
                if 'VENTA INTERNACIONAL' in nombre_linea:
                    continue
            
            # También filtrar por canal de ventas
            canal_ventas = sale.get('sales_channel_id')
            if canal_ventas and isinstance(canal_ventas, list) and len(canal_ventas) > 1:
                nombre_canal = canal_ventas[1].upper()
                if 'VENTA INTERNACIONAL' in nombre_canal or 'INTERNACIONAL' in nombre_canal:
                    continue
            
            sales_data_filtered.append(sale)
        
        # Crear DataFrame
        df = pd.DataFrame(sales_data_filtered)
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ventas', index=False)
        
        output.seek(0)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'ventas_farmaceuticas_{timestamp}.xlsx'
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'Error al exportar datos: {str(e)}', 'danger')
        return redirect(url_for('sales'))

@app.route('/metas_vendedor', methods=['GET', 'POST'])
def metas_vendedor():
    if 'username' not in session:
        return redirect(url_for('login'))

    # --- Verificación de Permisos ---
    admin_users = ["jonathan.cerda@agrovetmarket.com", "janet.hueza@agrovetmarket.com", "juan.portal@agrovetmarket.com", "AMAHOdoo@agrovetmarket.com"]
    is_admin = session.get('username') in admin_users
    if not is_admin:
        flash('No tienes permiso para acceder a esta página.', 'warning')
        return redirect(url_for('dashboard'))
    # --- Fin Verificación ---

    # Obtener meses y líneas comerciales para los filtros
    fecha_actual = datetime.now()
    año_actual = fecha_actual.year
    meses_disponibles = get_meses_del_año(año_actual)
    lineas_comerciales_estaticas = [
        {'nombre': 'PETMEDICA', 'id': 'petmedica'},
        {'nombre': 'AGROVET', 'id': 'agrovet'},
        {'nombre': 'PET NUTRISCIENCE', 'id': 'pet_nutriscience'},
        {'nombre': 'AVIVET', 'id': 'avivet'},
        {'nombre': 'OTROS', 'id': 'otros'},
        {'nombre': 'TERCEROS', 'id': 'terceros'},
        {'nombre': 'INTERPET', 'id': 'interpet'},
    ]
    equipos_definidos = [
        {'id': 'petmedica', 'nombre': 'PETMEDICA'},
        {'id': 'agrovet', 'nombre': 'AGROVET'},
        {'id': 'pet_nutriscience', 'nombre': 'PET NUTRISCIENCE'},
        {'id': 'avivet', 'nombre': 'AVIVET'},
        {'id': 'otros', 'nombre': 'OTROS'},
        {'id': 'terceros', 'nombre': 'TERCEROS'},
        {'id': 'interpet', 'nombre': 'INTERPET'},
    ]

    # Determinar mes y línea seleccionados (desde form o por defecto)
    mes_seleccionado = request.form.get('mes_seleccionado', fecha_actual.strftime('%Y-%m'))
    linea_seleccionada = request.form.get('linea_seleccionada', lineas_comerciales_estaticas[0]['id'])

    if request.method == 'POST':
        # --- 1. GUARDAR ASIGNACIONES DE EQUIPOS ---
        equipo_actualizado_id = request.form.get('guardar_equipo') # Para el mensaje flash
        todos_los_vendedores_para_guardar = data_manager.get_all_sellers()
        equipos_guardados = gs_manager.read_equipos()

        for equipo in equipos_definidos:
            campo_vendedores = f'vendedores_{equipo["id"]}'
            if campo_vendedores in request.form:
                vendedores_str = request.form.get(campo_vendedores, '')
                if vendedores_str:
                    vendedores_ids = [int(vid) for vid in vendedores_str.split(',') if vid.isdigit()]
                    equipos_guardados[equipo['id']] = vendedores_ids
                else:
                    equipos_guardados[equipo['id']] = []
        gs_manager.write_equipos(equipos_guardados, todos_los_vendedores_para_guardar)

        # --- 2. GUARDAR TODAS LAS METAS (ESTRUCTURA PIVOT) ---
        metas_vendedores_historicas = gs_manager.read_metas()
        
        for equipo in equipos_definidos:
            equipo_id = equipo['id']
            if equipo_id not in metas_vendedores_historicas:
                metas_vendedores_historicas[equipo_id] = {}

            vendedores_ids_en_equipo = equipos_guardados.get(equipo_id, [])
            for vendedor_id in vendedores_ids_en_equipo:
                vendedor_id_str = str(vendedor_id)
                if vendedor_id_str not in metas_vendedores_historicas[equipo_id]:
                    metas_vendedores_historicas[equipo_id][vendedor_id_str] = {}

                for mes in meses_disponibles:
                    mes_key = mes['key']
                    # No es necesario crear la clave del mes aquí, se crea si hay datos

                    meta_valor_str = request.form.get(f'meta_{equipo_id}_{vendedor_id_str}_{mes_key}')
                    meta_ipn_valor_str = request.form.get(f'meta_ipn_{equipo_id}_{vendedor_id_str}_{mes_key}')

                    # Convertir a float, manejar valores vacíos como None para no guardar ceros innecesarios
                    meta = float(meta_valor_str) if meta_valor_str else None
                    meta_ipn = float(meta_ipn_valor_str) if meta_ipn_valor_str else None

                    if meta is not None or meta_ipn is not None:
                        # Si la clave del mes no existe, créala
                        if mes_key not in metas_vendedores_historicas[equipo_id][vendedor_id_str]:
                             metas_vendedores_historicas[equipo_id][vendedor_id_str][mes_key] = {}
                        metas_vendedores_historicas[equipo_id][vendedor_id_str][mes_key] = {
                            'meta': meta or 0.0,
                            'meta_ipn': meta_ipn or 0.0
                        }
                    # Si ambos son None y la clave existe, se elimina para limpiar el JSON
                    elif mes_key in metas_vendedores_historicas[equipo_id][vendedor_id_str]:
                        del metas_vendedores_historicas[equipo_id][vendedor_id_str][mes_key]

        gs_manager.write_metas(metas_vendedores_historicas)
        
        if equipo_actualizado_id:
            flash(f'Miembros del equipo actualizados. Ahora puedes asignar sus metas.', 'info')
        else:
            flash('Equipos y metas guardados correctamente.', 'success')

        # Redirigir con los parámetros para recargar la página con los filtros correctos
        return redirect(url_for('metas_vendedor'))

    # GET o después de POST
    todos_los_vendedores = data_manager.get_all_sellers()
    vendedores_por_id = {v['id']: v for v in todos_los_vendedores}
    equipos_guardados = gs_manager.read_equipos()

    # Construir la estructura de datos para la plantilla
    equipos_con_vendedores = []
    for equipo_def in equipos_definidos:
        equipo_id = equipo_def['id']
        vendedores_ids = equipos_guardados.get(equipo_id, [])
        vendedores_de_equipo = [vendedores_por_id[vid] for vid in vendedores_ids if vid in vendedores_por_id]
        
        equipos_con_vendedores.append({
            'id': equipo_id,
            'nombre': equipo_def['nombre'],
            'vendedores_ids': [str(vid) for vid in vendedores_ids], # Para Tom-Select
            'vendedores': sorted(vendedores_de_equipo, key=lambda v: v['name']) # Para la tabla
        })

    # Para la vista, pasamos todas las metas cargadas
    metas_guardadas = gs_manager.read_metas()

    return render_template('metas_vendedor.html',
                           meses_disponibles=meses_disponibles,
                           lineas_comerciales=lineas_comerciales_estaticas,
                           equipos_con_vendedores=equipos_con_vendedores,
                           todos_los_vendedores=todos_los_vendedores,
                           metas_guardadas=metas_guardadas,
                           is_admin=is_admin) # Pasar el flag a la plantilla

@app.route('/export/dashboard/details')
def export_dashboard_details():
    """Exporta los detalles del dashboard a un archivo Excel formateado."""
    if 'username' not in session:
        return redirect(url_for('login'))

    # --- Verificación de Permisos ---
    admin_users = ["jonathan.cerda@agrovetmarket.com", "janet.hueza@agrovetmarket.com", "juan.portal@agrovetmarket.com", "AMAHOdoo@agrovetmarket.com"]
    is_admin = session.get('username') in admin_users
    if not is_admin:
        flash('No tienes permiso para realizar esta acción.', 'warning')
        return redirect(url_for('dashboard'))
    # --- Fin Verificación ---

    try:
        # Obtener el mes seleccionado de los parámetros de la URL
        mes_seleccionado = request.args.get('mes')
        if not mes_seleccionado:
            flash('No se especificó un mes para la exportación.', 'danger')
            return redirect(url_for('dashboard'))

        # --- Lógica de Fechas (incluyendo filtro de día) ---
        año_sel, mes_sel = mes_seleccionado.split('-')
        fecha_inicio = f"{año_sel}-{mes_sel}-01"

        # Usar el día del parámetro si está disponible, si no, el último día del mes
        dia_fin_param = request.args.get('dia_fin')
        if dia_fin_param and dia_fin_param.isdigit():
            dia_fin = int(dia_fin_param)
            fecha_fin = f"{año_sel}-{mes_sel}-{str(dia_fin).zfill(2)}"
        else:
            # Comportamiento por defecto: mes completo
            ultimo_dia = calendar.monthrange(int(año_sel), int(mes_sel))[1]
            fecha_fin = f"{año_sel}-{mes_sel}-{ultimo_dia}"

        # Obtener datos de ventas reales desde Odoo para ese mes
        sales_data = data_manager.get_sales_lines(
            date_from=fecha_inicio,
            date_to=fecha_fin,
            limit=10000  # Límite alto para exportación
        )

        # Filtrar VENTA INTERNACIONAL (exportaciones), igual que en el dashboard
        sales_data_filtered = []
        for sale in sales_data:
            linea_comercial = sale.get('commercial_line_national_id')
            if linea_comercial and isinstance(linea_comercial, list) and len(linea_comercial) > 1:
                if 'VENTA INTERNACIONAL' in linea_comercial[1].upper():
                    continue
            
            canal_ventas = sale.get('sales_channel_id')
            if canal_ventas and isinstance(canal_ventas, list) and len(canal_ventas) > 1:
                nombre_canal = canal_ventas[1].upper()
                if 'VENTA INTERNACIONAL' in nombre_canal or 'INTERNACIONAL' in nombre_canal:
                    continue
            
            sales_data_filtered.append(sale)

        # --- Procesar datos para un formato legible en Excel ---
        processed_for_excel = []
        for record in sales_data_filtered:
            processed_record = {}
            for key, value in record.items():
                # Si el valor es una lista como [id, 'nombre'], extrae solo el nombre
                if isinstance(value, list) and len(value) > 1:
                    processed_record[key] = value[1]
                else:
                    processed_record[key] = value
            
            # Asegurar que el balance sea un número para el formato de moneda
            if 'balance' in processed_record:
                try:
                    processed_record['balance'] = float(processed_record['balance'])
                except (ValueError, TypeError):
                    processed_record['balance'] = 0.0
            
            processed_for_excel.append(processed_record)

        # Crear DataFrame de Pandas con los datos ya procesados
        df = pd.DataFrame(processed_for_excel)

        # --- TRADUCCIÓN Y ORDEN DE COLUMNAS ---
        column_translations = {
            'invoice_date': 'Fecha Factura',
            'l10n_latam_document_type_id': 'Tipo Documento',
            'move_name': 'Número Documento',
            'partner_name': 'Cliente',
            'vat': 'RUC/DNI Cliente',
            'invoice_user_id': 'Vendedor',
            'default_code': 'Código Producto',
            'name': 'Descripción Producto',
            'quantity': 'Cantidad',
            'price_unit': 'Precio Unitario',
            'balance': 'Importe Total',
            'commercial_line_national_id': 'Línea Comercial',
            'sales_channel_id': 'Canal de Venta',
            'payment_state': 'Estado de Pago',
            'invoice_origin': 'Documento Origen',
            'product_life_cycle': 'Ciclo de Vida Producto',
            'pharmacological_classification_id': 'Clasificación Farmacológica',
            'pharmaceutical_forms_id': 'Forma Farmacéutica',
            'administration_way_id': 'Vía de Administración',
            'production_line_id': 'Línea de Producción',
            'categ_id': 'Categoría de Producto',
            'route_id': 'Ruta de Venta'
        }

        # Filtrar el DataFrame para mantener solo las columnas que vamos a usar
        df = df[list(column_translations.keys())]

        # Renombrar las columnas
        df.rename(columns=column_translations, inplace=True)
        
        # El orden de las columnas en el Excel será el mismo que en el diccionario
        # --- FIN DE TRADUCCIÓN Y ORDEN ---

        # --- Creación y Formateo del Archivo Excel ---
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sheet_name = f'Detalle Ventas {mes_seleccionado}'
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Obtener el workbook y la worksheet para aplicar estilos
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            # --- Definir Estilos ---
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="875A7B", end_color="875A7B", fill_type="solid")
            currency_format = 'S/ #,##0.00;[Red]-S/ #,##0.00'
            date_format = 'YYYY-MM-DD'
            number_format = '#,##0'

            # --- Aplicar Estilos al Encabezado ---
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill

            # --- Aplicar Formato a Columnas y Ajustar Ancho ---
            for col_idx, column in enumerate(df.columns, 1):
                col_letter = get_column_letter(col_idx)
                max_length = 0
                
                # Encontrar el ancho máximo
                if len(df[column]) > 0:
                    max_length = max(df[column].astype(str).map(len).max(), len(column)) + 2
                else:
                    max_length = len(column) + 2
                
                worksheet.column_dimensions[col_letter].width = max_length

                # Aplicar formato a celdas específicas
                if column.lower() == 'balance':
                    for cell in worksheet[col_letter][1:]:
                        cell.number_format = currency_format
                elif column.lower() == 'price_unit':
                    for cell in worksheet[col_letter][1:]:
                        cell.number_format = currency_format
                elif column.lower() == 'quantity':
                    for cell in worksheet[col_letter][1:]:
                        cell.number_format = number_format
                elif 'date' in column.lower():
                    for cell in worksheet[col_letter][1:]:
                        # Convertir texto a objeto datetime si es necesario
                        if isinstance(cell.value, str):
                            try:
                                cell.value = datetime.strptime(cell.value, '%Y-%m-%d')
                            except ValueError:
                                pass # Dejar como texto si no se puede convertir
                        cell.number_format = date_format

            # --- Congelar Panel Superior ---
            worksheet.freeze_panes = 'A2'

        # Mover el cursor al inicio del stream para enviarlo
        output.seek(0)
        # --- Fin del Formateo ---

        # Generar nombre de archivo
        filename = f'detalle_ventas_{mes_seleccionado}.xlsx'

        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        flash(f'Error al exportar los detalles del dashboard: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


# --- Ruta de Analytics ---
@app.route('/analytics')
def analytics():
    """Dashboard de estadísticas de uso del sistema."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Lista de administradores que pueden ver analytics
    admin_emails = [
        'jonathan.cerda@agrovetmarket.com',
        'juan.portal@agrovetmarket.com'
    ]
    
    # Verificar si el usuario es administrador
    if session.get('username') not in admin_emails:
        flash('No tienes permisos para acceder a esta sección.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener período de análisis
    period = request.args.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    # Contar usuarios permitidos en allowed_users.json
    total_allowed_users = 0
    try:
        with open('allowed_users.json', 'r', encoding='utf-8') as f:
            allowed_users_data = json.load(f)
            total_allowed_users = len(allowed_users_data.get('allowed_emails', []))
    except:
        total_allowed_users = 0
    
    # Obtener estadísticas y convertir RealDictRow a diccionarios normales
    stats = {
        'total_visits': analytics_db.get_total_visits(days),
        'unique_users': analytics_db.get_unique_users(days),
        'total_allowed_users': total_allowed_users,
        'visits_by_user': [dict(row) for row in analytics_db.get_visits_by_user(days)],
        'visits_by_page': [dict(row) for row in analytics_db.get_visits_by_page(days)],
        'visits_by_day': [dict(row) for row in analytics_db.get_visits_by_day(days)],
        'visits_by_hour': [dict(row) for row in analytics_db.get_visits_by_hour(min(days, 7))],
        'recent_visits': [dict(row) for row in analytics_db.get_recent_visits(50)]
    }
    
    # Convertir y formatear fechas para compatibilidad con el template
    # IMPORTANTE: Convertir timestamps de UTC a hora de Perú
    for visit in stats['visits_by_user']:
        if visit.get('last_visit'):
            if isinstance(visit['last_visit'], datetime):
                # Asumir que viene en UTC, convertir a Perú
                if visit['last_visit'].tzinfo is None:
                    utc_time = UTC_TZ.localize(visit['last_visit'])
                    peru_time = utc_time.astimezone(PERU_TZ)
                    visit['last_visit'] = peru_time.replace(tzinfo=None)
            elif isinstance(visit['last_visit'], str):
                try:
                    dt = datetime.strptime(visit['last_visit'], '%Y-%m-%d %H:%M:%S')
                    utc_time = UTC_TZ.localize(dt)
                    peru_time = utc_time.astimezone(PERU_TZ)
                    visit['last_visit'] = peru_time.replace(tzinfo=None)
                except:
                    pass
    
    for visit in stats['recent_visits']:
        if visit.get('visit_timestamp'):
            if isinstance(visit['visit_timestamp'], datetime):
                # Asumir que viene en UTC, convertir a Perú
                if visit['visit_timestamp'].tzinfo is None:
                    utc_time = UTC_TZ.localize(visit['visit_timestamp'])
                    peru_time = utc_time.astimezone(PERU_TZ)
                    visit['visit_timestamp'] = peru_time.replace(tzinfo=None)
            elif isinstance(visit['visit_timestamp'], str):
                try:
                    dt = datetime.strptime(visit['visit_timestamp'], '%Y-%m-%d %H:%M:%S')
                    utc_time = UTC_TZ.localize(dt)
                    peru_time = utc_time.astimezone(PERU_TZ)
                    visit['visit_timestamp'] = peru_time.replace(tzinfo=None)
                except:
                    pass
    
    # Ajustar horas de UTC a Perú (restar 5 horas)
    for hour_stat in stats['visits_by_hour']:
        if hour_stat.get('hour') is not None:
            utc_hour = int(hour_stat['hour'])
            peru_hour = (utc_hour - 5) % 24  # Perú es UTC-5
            hour_stat['hour'] = peru_hour
    
    # Preparar datos limpios para los gráficos (solo strings y números)
    chart_labels = []
    chart_visits = []
    chart_unique_users = []
    
    for day in reversed(stats['visits_by_day']):
        if day.get('visit_date'):
            if hasattr(day['visit_date'], 'strftime'):
                chart_labels.append(day['visit_date'].strftime('%d/%m'))
            else:
                chart_labels.append(str(day['visit_date']))
        else:
            chart_labels.append('N/A')
        
        chart_visits.append(day.get('visit_count', 0))
        chart_unique_users.append(day.get('unique_users', 0))
    
    # Generar JavaScript completo en Python
    import json
    chart_js_code = f"""
// Gráfico generado desde Python
if (document.getElementById('visitsPerDayChart')) {{
    new Chart(document.getElementById('visitsPerDayChart'), {{
        type: 'line',
        data: {{
            labels: {json.dumps(chart_labels)},
            datasets: [{{
                label: 'Visitas',
                data: {json.dumps(chart_visits)},
                borderColor: '#875A7B',
                backgroundColor: 'rgba(135, 90, 123, 0.1)',
                tension: 0.4,
                fill: true
            }}, {{
                label: 'Usuarios Únicos',
                data: {json.dumps(chart_unique_users)},
                borderColor: '#00A09D',
                backgroundColor: 'rgba(0, 160, 157, 0.1)',
                tension: 0.4,
                fill: true
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    position: 'top',
                }}
            }},
            scales: {{
                y: {{
                    beginAtZero: true,
                    ticks: {{
                        precision: 0
                    }}
                }}
            }}
        }}
    }});
}} else {{
    console.error('Canvas visitsPerDayChart no encontrado');
}}
"""
    
    stats['chart_js_code'] = chart_js_code
    
    return render_template('analytics.html', stats=stats, period=days)


if __name__ == '__main__':
    print("🚀 Iniciando Dashboard de Ventas Farmacéuticas...")
    print("📊 Disponible en: http://127.0.0.1:5000")
    print("🔐 Usuario: configurado en .env")
    app.run(debug=True)
