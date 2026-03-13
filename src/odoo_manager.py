# odoo_manager.py - Versión Completa Restaurada

import requests
import json
import os
import logging
import pandas as pd
from datetime import datetime, timedelta

class OdooManager:
    def get_commercial_lines_stacked_data(self, date_from=None, date_to=None, linea_id=None, partner_id=None):
        """Devuelve datos para gráfico apilado por línea comercial y 5 categorías"""
        sales_lines = self.get_sales_lines(
            date_from=date_from,
            date_to=date_to,
            partner_id=partner_id,
            linea_id=linea_id,
            limit=5000
        )
        # Nombres de las categorías a apilar
        categories = [
            ('pharmaceutical_forms_id', 'Forma Farmacéutica'),
            ('pharmacological_classification_id', 'Clasificación Farmacológica'),
            ('administration_way_id', 'Vía de Administración'),
            ('categ_id', 'Categoría de Producto'),
            ('production_line_id', 'Línea de Producción')
        ]
        # Agrupar por línea comercial
        lines = {}
        for line in sales_lines:
            cl = line.get('commercial_line_national_id')
            if cl and isinstance(cl, list) and len(cl) > 1:
                line_name = cl[1]
            else:
                line_name = 'Sin Línea Comercial'
            if line_name not in lines:
                lines[line_name] = {cat[1]: 0 for cat in categories}
            for key, cat_name in categories:
                val = line.get(key)
                # Si el campo es una lista [id, nombre], sumar por cantidad
                if val and isinstance(val, list) and len(val) > 1:
                    lines[line_name][cat_name] += line.get('quantity', 0)
                elif val:
                    lines[line_name][cat_name] += line.get('quantity', 0)
        # Preparar formato para ECharts
        yAxis = list(lines.keys())
        series = []
        for key, cat_name in categories:
            data = [lines[line_name][cat_name] for line_name in yAxis]
            series.append({
                'name': cat_name,
                'type': 'bar',
                'stack': 'total',
                'label': {'show': True},
                'data': data
            })
        return {
            'yAxis': yAxis,
            'series': series,
            'legend': [cat[1] for cat in categories]
        }
    def __init__(self):
        # Configurar conexión a Odoo - Usar credenciales del .env
        try:
            # Cargar credenciales desde variables de entorno (sin valores por defecto)
            self.url = os.getenv('ODOO_URL')
            self.db = os.getenv('ODOO_DB')
            self.username = os.getenv('ODOO_USER')
            self.password = os.getenv('ODOO_PASSWORD')
            
            # Validar que todas las credenciales estén configuradas
            if not all([self.url, self.db, self.username, self.password]):
                missing = [var for var, val in [
                    ('ODOO_URL', self.url), ('ODOO_DB', self.db), 
                    ('ODOO_USER', self.username), ('ODOO_PASSWORD', self.password)
                ] if not val]
                raise ValueError(f"Variables de entorno faltantes: {', '.join(missing)}")
            
            # Timeout configurable para llamadas JSON-RPC (segundos)
            try:
                self.rpc_timeout = int(os.getenv('ODOO_RPC_TIMEOUT', '30'))
            except Exception:
                self.rpc_timeout = 30

            self.jsonrpc_url = f"{self.url}/jsonrpc"
            
            # Autenticar con JSON-RPC
            headers = {"Content-Type": "application/json"}
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
            
            try:
                response = requests.post(self.jsonrpc_url, json=payload, headers=headers, timeout=self.rpc_timeout)
                result = response.json()
                
                if "result" in result and result["result"]:
                    self.uid = result["result"]
                    self.models = self._create_jsonrpc_models_proxy()
                    print(f"✅ Odoo conectado (JSON-RPC). UID: {self.uid}")
                else:
                    self.uid = None
                    self.models = None
                    print("❌ Advertencia: Autenticación falló. Continuando en modo offline.")
            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout al conectar a Odoo después de {self.rpc_timeout}s. Continuando en modo offline.")
                self.uid = None
                self.models = None
            except Exception as auth_e:
                print(f"⚠️ Error durante authenticate() a Odoo: {auth_e}")
                self.uid = None
                self.models = None
                
        except Exception as e:
            print(f"Error en la conexión a Odoo: {e}")
            print("Continuando en modo offline.")
            self.uid = None
            self.models = None

    def _create_jsonrpc_models_proxy(self):
        """Wrapper para mantener compatibilidad con código existente"""
        class JSONRPCModelsProxy:
            def __init__(self, manager):
                self.manager = manager
            
            def execute_kw(self, db, uid, password, model, method, args, kwargs=None):
                if kwargs is None:
                    kwargs = {}
                
                headers = {"Content-Type": "application/json"}
                payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "service": "object",
                        "method": "execute_kw",
                        "args": [db, uid, password, model, method, args, kwargs]
                    },
                    "id": 1
                }
                
                response = requests.post(
                    self.manager.jsonrpc_url,
                    json=payload,
                    headers=headers,
                    timeout=self.manager.rpc_timeout
                )
                result = response.json()
                
                return result.get("result") if "result" in result else None
        
        return JSONRPCModelsProxy(self)

    def authenticate_user(self, username, password):
        """Autenticar usuario contra Odoo y devolver sus datos si es exitoso."""
        try:
            headers = {"Content-Type": "application/json"}
            auth_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "common",
                    "method": "authenticate",
                    "args": [self.db, username, password, {}]
                },
                "id": 1
            }
            
            response = requests.post(self.jsonrpc_url, json=auth_payload, headers=headers, timeout=self.rpc_timeout)
            result = response.json()
            
            if "result" in result and result["result"]:
                uid = result["result"]
                print(f"✅ Autenticación exitosa para usuario: {username} (UID: {uid})")
                
                # Una vez autenticado, obtener el nombre del usuario
                read_payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "service": "object",
                        "method": "execute_kw",
                        "args": [self.db, uid, password, 'res.users', 'read', [uid], {'fields': ['name', 'login']}]
                    },
                    "id": 2
                }
                
                response = requests.post(self.jsonrpc_url, json=read_payload, headers=headers, timeout=self.rpc_timeout)
                result = response.json()
                
                if "result" in result and result["result"]:
                    return result["result"][0]  # Devuelve {'id': uid, 'name': 'John Doe', 'login': '...'}
                else:
                    # Fallback si no se pueden leer los datos del usuario
                    return {'id': uid, 'name': username, 'login': username}
            else:
                print(f"❌ Credenciales incorrectas para usuario: {username}")
                return None
                
        except Exception as e:
            print(f"❌ Error en autenticación contra Odoo: {e}")
            # En caso de error de conexión, no se puede autenticar
            return None

    def get_sales_filter_options(self):
        """Obtener opciones para filtros de ventas"""
        try:
            # Obtener líneas comerciales
            lineas = []
            try:
                # Consulta directa a productos para obtener líneas comerciales
                products = self.models.execute_kw(
                    self.db, self.uid, self.password, 'product.product', 'search_read',
                    [[('commercial_line_national_id', '!=', False)]],
                    {'fields': ['commercial_line_national_id'], 'limit': 1000}
                )
                
                # Extraer líneas únicas
                unique_lines = {}
                for product in products:
                    if product.get('commercial_line_national_id'):
                        line_id, line_name = product['commercial_line_national_id']
                        unique_lines[line_id] = line_name
                
                # Formatear líneas
                lineas = [
                    {'id': line_id, 'display_name': line_name}
                    for line_id, line_name in unique_lines.items()
                ]
                lineas.sort(key=lambda x: x['display_name'])
                
            except Exception as product_error:
                print(f"Error obteniendo líneas de productos: {product_error}")

            # Para compatibilidad con diferentes templates
            commercial_lines = lineas
            
            # Obtener clientes
            partners = self.models.execute_kw(
                self.db, self.uid, self.password, 'res.partner', 'search_read',
                [[('customer_rank', '>', 0)]],
                {'fields': ['id', 'name'], 'limit': 100}
            )
            
            # Formatear clientes
            clientes = [
                {'id': p['id'], 'display_name': p['name']}
                for p in partners
            ]
            
            return {
                'commercial_lines': commercial_lines,
                'lineas': lineas,  # Para compatibilidad con meta.html
                'partners': partners,
                'clientes': clientes  # Para compatibilidad
            }
            
        except Exception as e:
            print(f"Error al obtener opciones de filtro de ventas: {e}")
            return {'commercial_lines': [], 'lineas': [], 'partners': [], 'clientes': []}

    def get_filter_options(self):
        """Alias para get_sales_filter_options para compatibilidad"""
        return self.get_sales_filter_options()

    def get_all_sellers(self):
        """Obtiene una lista única de todos los vendedores (invoice_user_id)."""
        try:
            if not self.uid or not self.models:
                return []
            
            # Usamos read_group para obtener vendedores únicos de forma eficiente
            seller_groups = self.models.execute_kw(
                self.db, self.uid, self.password, 'account.move', 'read_group',
                [[('invoice_user_id', '!=', False)]],
                {'fields': ['invoice_user_id'], 'groupby': ['invoice_user_id']}
            )
            
            # Formatear la lista para el frontend
            sellers = []
            for group in seller_groups:
                if group.get('invoice_user_id'):
                    seller_id, seller_name = group['invoice_user_id']
                    sellers.append({'id': seller_id, 'name': seller_name})
            
            return sorted(sellers, key=lambda x: x['name'])
        except Exception as e:
            print(f"Error obteniendo la lista de vendedores: {e}")
            return []

    def get_sales_lines(self, page=None, per_page=None, filters=None, date_from=None, date_to=None, partner_id=None, linea_id=None, search=None, limit=10000):
        """Obtener líneas de venta completas con todas las 27 columnas"""
        try:
            print(f"🔍 Obteniendo líneas de venta completas...")
            
            # Verificar conexión
            if not self.uid or not self.models:
                print("❌ No hay conexión a Odoo disponible")
                if page is not None and per_page is not None:
                    return [], {'page': page, 'per_page': per_page, 'total': 0, 'pages': 0}
                return []
            
            # Manejar parámetros de ambos formatos de llamada
            if filters:
                date_from = filters.get('date_from')
                date_to = filters.get('date_to')
                partner_id = filters.get('partner_id')
                linea_id = filters.get('linea_id')
                search = filters.get('search')
            
            # Construir dominio de filtro
            domain = [
                ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
                ('move_id.state', '=', 'posted'),
                ('product_id.default_code', '!=', False)  # Solo productos con código
            ]
            
            # Filtros de exclusión de categorías específicas
            excluded_categories = [315, 333, 304, 314, 318, 339]
            domain.append(('product_id.categ_id', 'not in', excluded_categories))
            
            # Filtros de fecha
            if date_from:
                domain.append(('move_id.invoice_date', '>=', date_from))
            else:
                # Si no hay fecha de inicio, por defecto buscar en los últimos 30 días
                if not date_to:
                    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                    domain.append(('move_id.invoice_date', '>=', thirty_days_ago))

            if date_to:
                domain.append(('move_id.invoice_date', '<=', date_to))
            
            # Filtro de cliente
            if partner_id:
                domain.append(('partner_id', '=', partner_id))
            
            # Filtro de línea comercial
            if linea_id:
                domain.append(('product_id.commercial_line_national_id', '=', linea_id))
            
            # Filtro de búsqueda general (nombre de producto, cliente, código, etc.)
            if search:
                search_domain = [
                    '|', ('product_id.name', 'ilike', search),
                    '|', ('product_id.default_code', 'ilike', search),
                    '|', ('partner_id.name', 'ilike', search),
                    ('move_name', 'ilike', search)
                ]
                domain.extend(search_domain)

            # Obtener líneas base con todos los campos necesarios
            query_options = {
                'fields': [
                    'move_id', 'partner_id', 'product_id', 'balance', 'move_name',
                    'quantity', 'price_unit', 'tax_ids'
                ],
                'context': {'lang': 'es_PE'}
            }
            
            # Solo agregar limit si no es None (XML-RPC no maneja None)
            if limit is not None:
                query_options['limit'] = limit
            
            sales_lines_base = self.models.execute_kw(
                self.db, self.uid, self.password, 'account.move.line', 'search_read',
                [domain],
                query_options
            )
            
            print(f"📊 Base obtenida: {len(sales_lines_base)} líneas")
            
            if not sales_lines_base:
                return []
            
            # Obtener IDs únicos para consultas relacionadas
            move_ids = list(set([line['move_id'][0] for line in sales_lines_base if line.get('move_id')]))
            product_ids = list(set([line['product_id'][0] for line in sales_lines_base if line.get('product_id')]))
            partner_ids = list(set([line['partner_id'][0] for line in sales_lines_base if line.get('partner_id')]))
            
            print(f"📊 IDs únicos: {len(move_ids)} facturas, {len(product_ids)} productos, {len(partner_ids)} clientes")
            
            # Obtener datos de facturas (account.move) - Asientos contables
            move_data = {}
            if move_ids:
                moves = self.models.execute_kw(
                    self.db, self.uid, self.password, 'account.move', 'search_read',
                    [[('id', 'in', move_ids)]],
                    {
                        'fields': [
                            'payment_state', 'team_id', 'invoice_user_id', 'invoice_origin',
                            'invoice_date', 'l10n_latam_document_type_id', 'origin_number',
                            'order_id', 'name', 'ref', 'journal_id', 'amount_total', 'state'
                        ],
                        'context': {'lang': 'es_PE'}
                    }
                )
                move_data = {m['id']: m for m in moves}
                print(f"✅ Asientos contables (account.move): {len(move_data)} registros")
            
            # Obtener datos de productos con todos los campos farmacéuticos
            product_data = {}
            if product_ids:
                products = self.models.execute_kw(
                    self.db, self.uid, self.password, 'product.product', 'search_read',
                    [[('id', 'in', product_ids)]],
                    {
                        'fields': [
                            'name', 'default_code', 'categ_id', 'commercial_line_national_id',
                            'pharmacological_classification_id', 'pharmaceutical_forms_id',
                            'administration_way_id', 'production_line_id', 'product_life_cycle',
                        ],
                        'context': {'lang': 'es_PE'}
                    }
                )
                product_data = {p['id']: p for p in products}
                # --- DEBUG: Imprimir los campos del primer producto para verificar el nombre del campo ---
                if products:
                    print("🔍 DEBUG: Campos del primer producto obtenido:")
                    print(products[0])
                # --- FIN DEBUG ---
                print(f"✅ Productos: {len(product_data)} registros")
            
            # Obtener datos de clientes
            partner_data = {}
            if partner_ids:
                partners = self.models.execute_kw(
                    self.db, self.uid, self.password, 'res.partner', 'search_read',
                    [[('id', 'in', partner_ids)]],
                    {'fields': ['vat', 'name'], 'context': {'lang': 'es_PE'}}
                )
                partner_data = {p['id']: p for p in partners}
                print(f"✅ Clientes: {len(partner_data)} registros")
            
            # Obtener datos de órdenes de venta con más campos
            order_ids = [move['order_id'][0] for move in move_data.values() if move.get('order_id')]
            order_data = {}
            if order_ids:
                orders = self.models.execute_kw(
                    self.db, self.uid, self.password, 'sale.order', 'search_read',
                    [[('id', 'in', list(set(order_ids)))]],
                    {
                        'fields': [
                            'name', 'delivery_observations', 'partner_supplying_agency_id', 
                            'partner_shipping_id', 'date_order', 'state', 'amount_total',
                            'user_id', 'team_id', 'warehouse_id', 'commitment_date',
                            'client_order_ref', 'origin',
                        ]
                    }
                )
                order_data = {o['id']: o for o in orders}
                print(f"✅ Órdenes de venta (sale.order): {len(order_data)} registros con observaciones de entrega")
            
            # Obtener datos de líneas de orden de venta con más campos
            sale_line_data = {}
            if order_ids and product_ids:
                try:
                    sale_lines = self.models.execute_kw(
                        self.db, self.uid, self.password, 'sale.order.line', 'search_read',
                        [[('order_id', 'in', list(set(order_ids))), ('product_id', 'in', product_ids)]],
                        {
                            'fields': [
                                'order_id', 'product_id', 'route_id', 'name', 'product_uom_qty',
                                'price_unit', 'price_subtotal', 'discount', 'product_uom',
                                'analytic_distribution', 'display_type'
                            ],
                            'context': {'lang': 'es_PE'}
                        }
                    )
                    for sl in sale_lines:
                        if sl.get('order_id') and sl.get('product_id'):
                            key = (sl['order_id'][0], sl['product_id'][0])
                            sale_line_data[key] = sl
                    print(f"✅ Líneas de orden de venta (sale.order.line): {len(sale_line_data)} registros con rutas")
                except Exception as e:
                    print(f"⚠️ Error obteniendo líneas de orden: {e}")
            
            # Obtener todos los tax_ids únicos de las líneas contables
            all_tax_ids = set()
            for line in sales_lines_base:
                if line.get('tax_ids'):
                    all_tax_ids.update(line['tax_ids'])
            tax_names = {}
            if all_tax_ids:
                taxes = self.models.execute_kw(
                    self.db, self.uid, self.password, 'account.tax', 'search_read',
                    [[('id', 'in', list(all_tax_ids))]],
                    {'fields': ['id', 'name'], 'context': {'lang': 'es_PE'}}
                )
                tax_names = {t['id']: t['name'] for t in taxes}
            
            # Procesar y combinar todos los datos para las 27 columnas
            sales_lines = []
            ecommerce_reassigned = 0
            print(f"🚀 Procesando {len(sales_lines_base)} líneas con 27 columnas...")
            
            for line in sales_lines_base:
                move_id = line.get('move_id')
                product_id = line.get('product_id')
                partner_id = line.get('partner_id')
                
                # Obtener datos relacionados
                move = move_data.get(move_id[0], {}) if move_id else {}
                product = product_data.get(product_id[0], {}) if product_id else {}
                partner = partner_data.get(partner_id[0], {}) if partner_id else {}
                
                # Obtener datos de orden de venta
                order_id = move.get('order_id')
                order = order_data.get(order_id[0], {}) if order_id else {}
                
                # Obtener datos de línea de orden
                sale_line_key = (order_id[0], product_id[0]) if order_id and product_id else None
                sale_line = sale_line_data.get(sale_line_key, {}) if sale_line_key else {}
                # Obtener nombres de impuestos
                imp_list = []
                for tid in line.get('tax_ids', []):
                    if tid in tax_names:
                        imp_list.append(tax_names[tid])
                imp_str = ', '.join(imp_list) if imp_list else ''
                # Filtrar por impuestos IGV o IGV_INC
                if 'IGV' in imp_list or 'IGV_INC' in imp_list:
                    # APLICAR CAMBIO: Reemplazar línea comercial para usuarios ECOMMERCE específicos
                    # Se hace aquí para que el commercial_line_national_id original esté disponible para otros cálculos si es necesario
                    commercial_line_id = product.get('commercial_line_national_id')
                    invoice_user = move.get('invoice_user_id')
                    
                    

                    # Crear registro completo con las 27 columnas
                    sales_lines.append({
                        # 1. Estado de Pago
                        'payment_state': move.get('payment_state'),
                        
                        # 2. Canal de Venta
                        'sales_channel_id': move.get('team_id'),
                        
                        # 3. Línea Comercial Local
                        'commercial_line_national_id': commercial_line_id,
                        
                        # 4. Vendedor
                        'invoice_user_id': move.get('invoice_user_id'),
                        
                        # 5. Socio
                        'partner_name': partner.get('name'),
                        
                        # 6. NIF
                        'vat': partner.get('vat'),
                        
                        # 7. Origen
                        'invoice_origin': move.get('invoice_origin'),
                        
                        # 7.1. Asiento Contable (move_id)
                        'move_name': move.get('name'),  # Número del asiento contable
                        'move_ref': move.get('ref'),    # Referencia del asiento
                        'move_state': move.get('state'), # Estado del asiento
                        
                        # 7.2. Orden de Venta (order_id) 
                        'order_name': order.get('name'),  # Número de la orden de venta
                        'order_origin': order.get('origin'), # Origen de la orden
                        'client_order_ref': order.get('client_order_ref'), # Referencia del cliente
                        
                        # 8. Producto
                        'name': product.get('name', ''),
                        
                        # 9. Referencia Interna
                        'default_code': product.get('default_code', ''),
                        
                        # 10. ID Producto
                        'product_id': line.get('product_id'),
                        
                        # 11. Fecha Factura
                        'invoice_date': move.get('invoice_date'),
                        
                        # 12. Tipo Documento
                        'l10n_latam_document_type_id': move.get('l10n_latam_document_type_id'),
                        
                        # 13. Número
                        'move_name': line.get('move_name'),
                        
                        # 14. Ref. Doc. Rectificado
                        'origin_number': move.get('origin_number'),
                        
                        # 15. Saldo
                        'balance': -line.get('balance', 0) if line.get('balance') is not None else 0,
                        
                        # 16. Clasificación Farmacológica
                        'pharmacological_classification_id': product.get('pharmacological_classification_id'),
                        
                        # 17. Observaciones Entrega (delivery_observations)
                        'delivery_observations': order.get('delivery_observations'),
                        
                        # 17.1. Información adicional de la orden
                        'order_date': order.get('date_order'),  # Fecha de la orden
                        'order_state': order.get('state'),      # Estado de la orden
                        'commitment_date': order.get('commitment_date'),  # Fecha compromiso
                        'order_user_id': order.get('user_id'),  # Vendedor de la orden
                        
                        # 18. Agencia
                        'partner_supplying_agency_id': order.get('partner_supplying_agency_id'),
                        
                        # 19. Formas Farmacéuticas
                        'pharmaceutical_forms_id': product.get('pharmaceutical_forms_id'),
                        
                        # 20. Vía Administración
                        'administration_way_id': product.get('administration_way_id'),
                        
                        # 21. Categoría Producto
                        'categ_id': product.get('categ_id'),
                        
                        # 22. Línea Producción
                        'production_line_id': product.get('production_line_id'),
                        
                        # 23. Cantidad
                        'quantity': line.get('quantity'),
                        
                        # 24. Precio Unitario
                        'price_unit': line.get('price_unit'),
                        
                        # 25. Dirección Entrega
                        'partner_shipping_id': order.get('partner_shipping_id'),
                        
                        # 26. Ruta
                        'route_id': sale_line.get('route_id'),
                        
                        # 27. Ciclo de Vida
                        'product_life_cycle': product.get('product_life_cycle'),
                        
                        # 28. IMP (Impuesto)
                        'tax_id': imp_str,
                        
                        # Campos adicionales para compatibilidad
                        'move_id': line.get('move_id'),
                        'partner_id': line.get('partner_id')
                    })
            
            print(f"✅ Procesadas {len(sales_lines)} líneas con 27 columnas completas")
            print(f"🔄 Reasignadas {ecommerce_reassigned} líneas a ECOMMERCE (usuarios específicos)")
            
            # Si se solicita paginación, devolver tupla (datos, paginación)
            if page is not None and per_page is not None:
                # Calcular paginación
                total_items = len(sales_lines)
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_data = sales_lines[start_idx:end_idx]
                
                pagination = {
                    'page': page,
                    'per_page': per_page,
                    'total': total_items,
                    'pages': (total_items + per_page - 1) // per_page
                }
                
                return paginated_data, pagination
            
            # Si no se solicita paginación, devolver solo los datos
            return sales_lines
            
        except Exception as e:
            print(f"Error al obtener las líneas de venta de Odoo: {e}")
            # Devolver formato apropiado según si se solicitó paginación
            if page is not None and per_page is not None:
                return [], {'page': page, 'per_page': per_page, 'total': 0, 'pages': 0}
            return []

    def get_sales_dashboard_data(self, date_from=None, date_to=None, linea_id=None, partner_id=None):
        """Obtener datos para el dashboard de ventas"""
        try:
            # Obtener líneas de venta
            sales_lines = self.get_sales_lines(
                date_from=date_from,
                date_to=date_to,
                partner_id=partner_id,
                linea_id=linea_id,
                limit=5000
            )
            
            # Filtrar VENTA INTERNACIONAL (exportaciones)
            sales_lines_filtered = []
            for line in sales_lines:
                # Filtrar por línea comercial
                linea_comercial = line.get('commercial_line_national_id')
                if linea_comercial and isinstance(linea_comercial, list) and len(linea_comercial) > 1:
                    nombre_linea = linea_comercial[1].upper()
                    if 'VENTA INTERNACIONAL' in nombre_linea:
                        continue
                
                # Filtrar por canal de ventas
                canal_ventas = line.get('sales_channel_id')
                if canal_ventas and isinstance(canal_ventas, list) and len(canal_ventas) > 1:
                    nombre_canal = canal_ventas[1].upper()
                    if 'VENTA INTERNACIONAL' in nombre_canal or 'INTERNACIONAL' in nombre_canal:
                        continue
                
                sales_lines_filtered.append(line)
            
            sales_lines = sales_lines_filtered  # Usar los datos filtrados
            
            if not sales_lines:
                return self._get_empty_dashboard_data()
            
            # Calcular métricas básicas
            total_sales = sum([abs(line.get('balance', 0)) for line in sales_lines])
            total_quantity = sum([line.get('quantity', 0) for line in sales_lines])
            total_lines = len(sales_lines)
            
            # Métricas por cliente
            clients_data = {}
            for line in sales_lines:
                client_name = line.get('partner_name', 'Sin Cliente')
                if client_name not in clients_data:
                    clients_data[client_name] = {'sales': 0, 'quantity': 0}
                clients_data[client_name]['sales'] += abs(line.get('balance', 0))
                clients_data[client_name]['quantity'] += line.get('quantity', 0)
            
            # Top clientes
            top_clients = sorted(clients_data.items(), key=lambda x: x[1]['sales'], reverse=True)[:10]
            
            # Métricas por producto
            products_data = {}
            for line in sales_lines:
                product_name = line.get('name', 'Sin Producto')
                if product_name not in products_data:
                    products_data[product_name] = {'sales': 0, 'quantity': 0}
                products_data[product_name]['sales'] += abs(line.get('balance', 0))
                products_data[product_name]['quantity'] += line.get('quantity', 0)
            
            # Top productos
            top_products = sorted(products_data.items(), key=lambda x: x[1]['sales'], reverse=True)[:10]
            
            # Métricas por canal
            channels_data = {}
            for line in sales_lines:
                channel = line.get('sales_channel_id')
                channel_name = channel[1] if channel and len(channel) > 1 else 'Sin Canal'
                if channel_name not in channels_data:
                    channels_data[channel_name] = {'sales': 0, 'quantity': 0}
                channels_data[channel_name]['sales'] += abs(line.get('balance', 0))
                channels_data[channel_name]['quantity'] += line.get('quantity', 0)
            
            sales_by_channel = list(channels_data.items())
            
            # Métricas por línea comercial (NUEVO)
            commercial_lines_data = {}
            for line in sales_lines:
                commercial_line = line.get('commercial_line_national_id')
                if commercial_line:
                    line_name = commercial_line[1] if commercial_line and len(commercial_line) > 1 else 'Sin Línea'
                else:
                    line_name = 'Sin Línea Comercial'
                
                if line_name not in commercial_lines_data:
                    commercial_lines_data[line_name] = {'sales': 0, 'quantity': 0}
                commercial_lines_data[line_name]['sales'] += abs(line.get('balance', 0))
                commercial_lines_data[line_name]['quantity'] += line.get('quantity', 0)
            
            # Preparar datos de líneas comerciales para el gráfico
            commercial_lines_sorted = sorted(commercial_lines_data.items(), key=lambda x: x[1]['sales'], reverse=True)
            commercial_lines = [
                {
                    'name': line_name,
                    'amount': data['sales'],
                    'quantity': data['quantity']
                } 
                for line_name, data in commercial_lines_sorted
            ]
            
            # Estadísticas de líneas comerciales
            commercial_lines_stats = {
                'total_lines': len(commercial_lines),
                'top_line_name': commercial_lines[0]['name'] if commercial_lines else 'N/A',
                'top_line_amount': commercial_lines[0]['amount'] if commercial_lines else 0
            }
            
            # Métricas por vendedor (NUEVO)
            sellers_data = {}
            for line in sales_lines:
                seller = line.get('invoice_user_id')
                if seller:
                    seller_name = seller[1] if seller and len(seller) > 1 else 'Sin Vendedor'
                else:
                    seller_name = 'Sin Vendedor Asignado'
                
                if seller_name not in sellers_data:
                    sellers_data[seller_name] = {'sales': 0, 'quantity': 0}
                sellers_data[seller_name]['sales'] += abs(line.get('balance', 0))
                sellers_data[seller_name]['quantity'] += line.get('quantity', 0)
            
            # Preparar datos de vendedores para el gráfico (Top 8 vendedores)
            sellers_sorted = sorted(sellers_data.items(), key=lambda x: x[1]['sales'], reverse=True)[:8]
            sellers = [
                {
                    'name': seller_name,
                    'amount': data['sales'],
                    'quantity': data['quantity']
                } 
                for seller_name, data in sellers_sorted
            ]
            
            # Estadísticas de vendedores
            sellers_stats = {
                'total_sellers': len(sellers_data),
                'top_seller_name': sellers[0]['name'] if sellers else 'N/A',
                'top_seller_amount': sellers[0]['amount'] if sellers else 0
            }
            
            return {
                'total_sales': total_sales,
                'total_quantity': total_quantity,
                'total_lines': total_lines,
                'top_clients': top_clients,
                'top_products': top_products,
                'sales_by_month': [],  # Puede implementarse después
                'sales_by_channel': sales_by_channel,
                # Datos específicos para líneas comerciales
                'commercial_lines': commercial_lines,
                'commercial_lines_stats': commercial_lines_stats,
                # Datos específicos para vendedores
                'sellers': sellers,
                'sellers_stats': sellers_stats,
                # Campos KPI para el template
                'kpi_total_sales': total_sales,
                'kpi_total_invoices': total_lines,
                'kpi_total_quantity': total_quantity
            }
            
        except Exception as e:
            print(f"Error obteniendo datos del dashboard: {e}")
            return self._get_empty_dashboard_data()

    def _get_empty_dashboard_data(self):
        """Datos vacíos para el dashboard"""
        return {
            'total_sales': 0,
            'total_quantity': 0,
            'total_lines': 0,
            'top_clients': [],
            'top_products': [],
            'sales_by_month': [],
            'sales_by_channel': [],
            # Datos vacíos para líneas comerciales
            'commercial_lines': [],
            'commercial_lines_stats': {
                'total_lines': 0,
                'top_line_name': 'N/A',
                'top_line_amount': 0
            },
            # Datos vacíos para vendedores
            'sellers': [],
            'sellers_stats': {
                'total_sellers': 0,
                'top_seller_name': 'N/A',
                'top_seller_amount': 0
            },
            # Campos KPI para el template
            'kpi_total_sales': 0,
            'kpi_total_invoices': 0,
            'kpi_total_quantity': 0
        }
