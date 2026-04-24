"""
generar_informe_pdf_usuarios.py

Genera informe PDF de usuarios habilitados sin ingreso con nombres completos desde Odoo.

Autor: Jonathan Cerda
Fecha: Abril 2026
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from src.permissions_manager import PermissionsManager
from src.supabase_manager import SupabaseManager
from src.odoo_jsonrpc_client import OdooJSONRPCClient
from src.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


def obtener_nombres_completos_odoo(emails: list) -> dict:
    """
    Consulta Odoo para obtener nombres completos de usuarios.
    
    Args:
        emails: Lista de emails a buscar
        
    Returns:
        Dict con {email: nombre_completo}
    """
    nombres = {}
    
    try:
        # Conectar a Odoo
        odoo = OdooJSONRPCClient(
            url=os.getenv('ODOO_URL'),
            db=os.getenv('ODOO_DB'),
            username=os.getenv('ODOO_USER'),
            password=os.getenv('ODOO_PASSWORD')
        )
        
        print(f"🔍 Consultando {len(emails)} usuarios en Odoo...")
        
        # Buscar usuarios en res.users
        usuarios = odoo.search_read(
            'res.users',
            domain=[('login', 'in', emails)],
            fields=['login', 'name'],
            limit=len(emails)
        )
        
        # Mapear email -> nombre
        for user in usuarios:
            nombres[user['login']] = user['name']
        
        print(f"✅ {len(nombres)} nombres encontrados en Odoo")
        
        # Para emails no encontrados, usar parte antes del @
        for email in emails:
            if email not in nombres:
                nombre_base = email.split('@')[0].replace('.', ' ').title()
                nombres[email] = f"{nombre_base} (Sin registro Odoo)"
                
        return nombres
        
    except Exception as e:
        logger.error(f"Error consultando Odoo: {e}", exc_info=True)
        print(f"⚠️  Error consultando Odoo, usando emails como nombres")
        
        # Fallback: usar emails
        return {email: email.split('@')[0].replace('.', ' ').title() for email in emails}


def generar_pdf_usuarios_sin_ingreso(archivo: str = "informe_usuarios_sin_ingreso.pdf"):
    """
    Genera PDF profesional con usuarios sin ingreso.
    
    Args:
        archivo: Nombre del archivo PDF a generar
    """
    try:
        print("\n" + "="*70)
        print("📄 GENERANDO INFORME PDF DE USUARIOS SIN INGRESO")
        print("="*70 + "\n")
        
        # 1. Obtener datos
        perm_manager = PermissionsManager()
        supabase = SupabaseManager()
        
        print("🔍 Obteniendo usuarios habilitados...")
        usuarios_habilitados = perm_manager.get_all_users(include_inactive=False)
        
        print("🔍 Consultando visitas registradas...")
        response = supabase.supabase.table('page_visits_ventas_locales')\
            .select('user_email')\
            .execute()
        
        usuarios_con_visitas = set()
        if response.data:
            usuarios_con_visitas = {row['user_email'] for row in response.data if row.get('user_email')}
        
        # Identificar usuarios sin ingreso
        usuarios_sin_ingreso = []
        for user in usuarios_habilitados:
            if user['user_email'] not in usuarios_con_visitas:
                usuarios_sin_ingreso.append(user)
        
        if not usuarios_sin_ingreso:
            print("✅ Todos los usuarios han ingresado al menos una vez.")
            return
        
        print(f"📊 {len(usuarios_sin_ingreso)} usuarios sin ingreso detectados")
        
        # 2. Obtener nombres completos desde Odoo
        emails = [u['user_email'] for u in usuarios_sin_ingreso]
        nombres_completos = obtener_nombres_completos_odoo(emails)
        
        # 3. Crear PDF
        print(f"\n📝 Generando PDF: {archivo}...")
        
        doc = SimpleDocTemplate(
            archivo,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitulo_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Elementos del documento
        elements = []
        
        # Logo/Header (si existe)
        logo_path = "static/img/logo.png"
        if os.path.exists(logo_path):
            from reportlab.platypus import Image
            logo = Image(logo_path, width=1.5*inch, height=0.5*inch)
            elements.append(logo)
            elements.append(Spacer(1, 12))
        
        # Título
        titulo = Paragraph("Informe de Usuarios sin Ingreso al Sistema", titulo_style)
        elements.append(titulo)
        
        # Fecha
        fecha_actual = datetime.now().strftime('%d de %B de %Y, %H:%M')
        subtitulo = Paragraph(f"Generado: {fecha_actual}", subtitulo_style)
        elements.append(subtitulo)
        elements.append(Spacer(1, 20))
        
        # Resumen estadístico
        stats_heading = Paragraph("📊 Resumen Estadístico", heading_style)
        elements.append(stats_heading)
        
        total_habilitados = len(usuarios_habilitados)
        total_con_ingreso = len(usuarios_con_visitas)
        total_sin_ingreso = len(usuarios_sin_ingreso)
        porcentaje_sin_ingreso = (total_sin_ingreso / total_habilitados * 100) if total_habilitados > 0 else 0
        
        stats_data = [
            ['Métrica', 'Valor'],
            ['Total usuarios habilitados', str(total_habilitados)],
            ['Usuarios con al menos 1 ingreso', f"{total_con_ingreso} ({total_con_ingreso/total_habilitados*100:.1f}%)"],
            ['Usuarios SIN ningún ingreso', f"{total_sin_ingreso} ({porcentaje_sin_ingreso:.1f}%)"]
        ]
        
        stats_table = Table(stats_data, colWidths=[4*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 30))
        
        # Tabla de usuarios sin ingreso
        users_heading = Paragraph(f"👥 Detalle de Usuarios sin Ingreso ({len(usuarios_sin_ingreso)})", heading_style)
        elements.append(users_heading)
        elements.append(Spacer(1, 10))
        
        # Preparar datos de la tabla
        table_data = [
            ['#', 'Nombre Completo', 'Email', 'Rol', 'Fecha Creación']
        ]
        
        # Ordenar por fecha de creación (más reciente primero)
        usuarios_sin_ingreso_sorted = sorted(
            usuarios_sin_ingreso,
            key=lambda x: x['created_at'],
            reverse=True
        )
        
        for idx, user in enumerate(usuarios_sin_ingreso_sorted, 1):
            email = user['user_email']
            nombre = nombres_completos.get(email, email.split('@')[0])
            rol = user['role_display_name']
            fecha = user['created_at_formatted']
            
            # Acortar email si es muy largo
            email_corto = email if len(email) <= 35 else email[:32] + '...'
            
            table_data.append([
                str(idx),
                nombre,
                email_corto,
                rol,
                fecha
            ])
        
        # Crear tabla con anchos específicos
        users_table = Table(
            table_data,
            colWidths=[0.4*inch, 2*inch, 2.2*inch, 1.5*inch, 0.9*inch]
        )
        
        # Estilo de la tabla
        users_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Cuerpo
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Columna #
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#c0392b')),
            
            # Alternancia de colores
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
        ]))
        
        elements.append(users_table)
        elements.append(Spacer(1, 30))
        
        # Recomendaciones
        recom_heading = Paragraph("💡 Recomendaciones", heading_style)
        elements.append(recom_heading)
        
        recomendaciones = [
            "1. Enviar correo de bienvenida con instrucciones de acceso detalladas",
            "2. Verificar que los usuarios recibieron el email de invitación en su bandeja",
            "3. Revisar posibles problemas de autenticación OAuth (cookies, permisos)",
            "4. Contactar directamente a usuarios administradores que no han ingresado",
            "5. Considerar desactivar cuentas sin uso después de 30 días",
            "6. Programar sesión de capacitación o demo del sistema",
            "7. Validar que los correos electrónicos sean correctos y activos"
        ]
        
        for recom in recomendaciones:
            p = Paragraph(recom, styles['Normal'])
            elements.append(p)
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 20))
        
        # Pie de página
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        footer = Paragraph(
            f"Dashboard Ventas Farmacéuticas - Agrovet Market | Generado automáticamente",
            footer_style
        )
        elements.append(footer)
        
        # Construir PDF
        doc.build(elements)
        
        print(f"\n✅ PDF generado exitosamente: {archivo}")
        print(f"📍 Ubicación: {os.path.abspath(archivo)}")
        print(f"📄 Total de páginas estimadas: {len(usuarios_sin_ingreso)//20 + 1}")
        print("="*70 + "\n")
        
        return archivo
        
    except Exception as e:
        logger.error(f"Error generando PDF: {e}", exc_info=True)
        print(f"\n❌ Error generando PDF: {e}\n")
        return None


if __name__ == "__main__":
    print("\n🚀 Iniciando generación de informe PDF...\n")
    
    archivo_generado = generar_pdf_usuarios_sin_ingreso()
    
    if archivo_generado:
        print("✅ Proceso completado exitosamente.\n")
        print(f"💡 Puedes abrir el archivo con: start {archivo_generado}\n")
    else:
        print("❌ No se pudo generar el PDF.\n")
