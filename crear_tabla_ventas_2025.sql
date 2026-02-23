-- Crear tabla para almacenar todas las ventas del 2025 desde Odoo
-- Esta tabla replica la estructura de datos que usa el dashboard

CREATE TABLE IF NOT EXISTS Ventas_Odoo_2025 (
    -- ID único del registro
    id BIGSERIAL PRIMARY KEY,
    
    -- 1. Estado de Pago
    payment_state TEXT,
    
    -- 2. Canal de Venta (team_id)
    sales_channel_id INTEGER,
    sales_channel_name TEXT,
    
    -- 3. Línea Comercial Local
    commercial_line_national_id INTEGER,
    commercial_line_name TEXT,
    
    -- 4. Vendedor (invoice_user_id)
    invoice_user_id INTEGER,
    invoice_user_name TEXT,
    
    -- 5. Socio (Cliente)
    partner_id INTEGER,
    partner_name TEXT,
    
    -- 6. NIF (RUC/DNI)
    vat TEXT,
    
    -- 7. Origen
    invoice_origin TEXT,
    
    -- 7.1. Asiento Contable (move_id)
    move_id INTEGER,
    move_name TEXT,
    move_ref TEXT,
    move_state TEXT,
    
    -- 7.2. Orden de Venta
    order_id INTEGER,
    order_name TEXT,
    order_origin TEXT,
    client_order_ref TEXT,
    order_date TIMESTAMP,
    order_state TEXT,
    commitment_date TIMESTAMP,
    order_user_id INTEGER,
    order_user_name TEXT,
    
    -- 8. Producto
    product_id INTEGER,
    product_name TEXT,
    
    -- 9. Referencia Interna (Código)
    default_code TEXT,
    
    -- 11. Fecha Factura
    invoice_date DATE,
    
    -- 12. Tipo Documento
    l10n_latam_document_type_id INTEGER,
    document_type_name TEXT,
    
    -- 14. Ref. Doc. Rectificado
    origin_number TEXT,
    
    -- 15. Saldo (Monto de venta)
    balance NUMERIC(12, 2),
    price_subtotal NUMERIC(12, 2),
    
    -- 16. Clasificación Farmacológica
    pharmacological_classification_id INTEGER,
    pharmacological_classification_name TEXT,
    
    -- 17. Observaciones Entrega
    delivery_observations TEXT,
    
    -- 18. Agencia
    partner_supplying_agency_id INTEGER,
    partner_supplying_agency_name TEXT,
    
    -- 19. Formas Farmacéuticas
    pharmaceutical_forms_id INTEGER,
    pharmaceutical_forms_name TEXT,
    
    -- 20. Vía Administración
    administration_way_id INTEGER,
    administration_way_name TEXT,
    
    -- 21. Categoría Producto
    categ_id INTEGER,
    categ_name TEXT,
    
    -- 22. Línea Producción
    production_line_id INTEGER,
    production_line_name TEXT,
    
    -- 23. Cantidad
    quantity NUMERIC(12, 4),
    
    -- 24. Precio Unitario
    price_unit NUMERIC(12, 2),
    
    -- 25. Dirección Entrega
    partner_shipping_id INTEGER,
    partner_shipping_name TEXT,
    
    -- 26. Ruta
    route_id INTEGER,
    route_name TEXT,
    
    -- 27. Ciclo de Vida
    product_life_cycle TEXT,
    
    -- 28. IMP (Impuesto)
    tax_id TEXT,
    tax_ids INTEGER[],
    
    -- Campos de auditoría
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_ventas_2025_invoice_date ON Ventas_Odoo_2025(invoice_date);
CREATE INDEX IF NOT EXISTS idx_ventas_2025_commercial_line ON Ventas_Odoo_2025(commercial_line_national_id);
CREATE INDEX IF NOT EXISTS idx_ventas_2025_partner ON Ventas_Odoo_2025(partner_id);
CREATE INDEX IF NOT EXISTS idx_ventas_2025_product ON Ventas_Odoo_2025(product_id);
CREATE INDEX IF NOT EXISTS idx_ventas_2025_vendedor ON Ventas_Odoo_2025(invoice_user_id);
CREATE INDEX IF NOT EXISTS idx_ventas_2025_canal ON Ventas_Odoo_2025(sales_channel_id);
CREATE INDEX IF NOT EXISTS idx_ventas_2025_order ON Ventas_Odoo_2025(order_id);
CREATE INDEX IF NOT EXISTS idx_ventas_2025_move ON Ventas_Odoo_2025(move_id);

-- Habilitar RLS (Row Level Security)
ALTER TABLE Ventas_Odoo_2025 ENABLE ROW LEVEL SECURITY;

-- Crear política para permitir lectura a todos los usuarios autenticados
CREATE POLICY "Permitir lectura de ventas 2025"
ON Ventas_Odoo_2025
FOR SELECT
USING (true);

-- Comentarios en la tabla
COMMENT ON TABLE Ventas_Odoo_2025 IS 'Almacena todas las líneas de venta del año 2025 extraídas desde Odoo';
COMMENT ON COLUMN Ventas_Odoo_2025.balance IS 'Monto de venta (balance negativo convertido a positivo)';
COMMENT ON COLUMN Ventas_Odoo_2025.invoice_date IS 'Fecha de la factura';
COMMENT ON COLUMN Ventas_Odoo_2025.commercial_line_name IS 'Nombre de la línea comercial (PETMEDICA, AGROVET, etc.)';
