# Ventas 2025 - Dashboard Farmacéuticas (Proyecto Principal)

## 📊 Resumen Ejecutivo

**Total Año 2025:** S/ 54,721,292

Este documento contiene los valores de referencia del proyecto principal de Dashboard de Ventas Farmacéuticas para comparación con otros proyectos.

---

## 📅 Ventas Mensuales 2025

| Mes | Venta Total (S/) | Registros |
|-----|------------------|-----------|
| Enero | 1,723,599 | 1,047 |
| Febrero | 4,355,482 | 2,330 |
| Marzo | 5,204,492 | 2,833 |
| Abril | 4,299,838 | 2,350 |
| Mayo | 5,561,739 | 2,796 |
| Junio | 3,348,956 | 2,250 |
| Julio | 3,459,387 | 2,522 |
| Agosto | 4,027,793 | 3,048 |
| Septiembre | 4,709,979 | 3,451 |
| Octubre | 4,151,104 | 3,349 |
| Noviembre | 5,999,186 | 2,949 |
| Diciembre | 7,880,135 | 3,057 |
| **TOTAL** | **54,721,292** | **31,982** |

---

## 🏢 Ventas por Línea Comercial - Enero 2025

| Línea Comercial | Venta (S/) |
|-----------------|------------|
| PETMEDICA | 903,847 |
| AGROVET | 761,069 |
| AVIVET | 44,050 |
| PET NUTRISCIENCE | 14,633 |
| INTERPET | 0 |
| OTROS | 0 |
| TERCEROS | 0 |
| **Total** | **1,723,599** |

---

## 🏢 Ventas por Línea Comercial - Diciembre 2025

| Línea Comercial | Venta (S/) |
|-----------------|------------|
| PETMEDICA | 5,207,323 |
| AGROVET | 1,986,712 |
| TERCEROS | 302,810 |
| INTERPET | 202,970 |
| PET NUTRISCIENCE | 83,759 |
| AVIVET | 65,795 |
| OTROS | 30,766 |
| **Total** | **7,880,135** |

---

## 🔍 Metodología de Cálculo

### Campo Utilizado
- **Campo:** `balance` (del modelo `account.move.line` en Odoo)
- **Transformación:** `abs(balance)` - Valor absoluto del balance
- **Razón:** Los asientos de ventas tienen balance negativo en Odoo, se convierte a positivo con `abs()`

### Filtros Aplicados

1. **move_type:** `['out_invoice', 'out_refund']` - Solo facturas de venta y notas de crédito
2. **state:** `'posted'` - Solo asientos contables confirmados
3. **Categorías excluidas:** `[315, 333, 304, 314, 318, 339]` - Categorías específicas del negocio
4. **Línea comercial:** Excluye `'VENTA INTERNACIONAL'`
5. **Canal:** **NO filtra por canal** (incluye todos: NACIONAL, INTERNACIONAL, etc.)
6. **Producto:** Solo productos con `default_code` definido

### Procesamiento Adicional
- Se normaliza líneas comerciales: GENVET y MARCA BLANCA → TERCEROS
- Se excluyen líneas procesadas con columnas incompletas
- Los valores IPN (Productos Nuevos) se calculan sobre productos con `product_life_cycle = 'nuevo'`

---

## ⚠️ Diferencias Conocidas con Otros Proyectos

### ⚠️ IMPORTANTE: Límite de Registros Corregido

**Problema detectado:** El dashboard principal tenía un límite de 5,000 registros, pero diciembre 2025 generó 5,364 líneas de venta, causando pérdida de 364 registros.

**Solución aplicada:** Límite aumentado a 10,000 registros para prevenir pérdida de datos en meses con alto volumen.

**Impacto en datos históricos:**
- Los valores reportados en este documento **pueden tener discrepancias** con los valores reales para diciembre 2025
- Ejemplo detectado: AGROVET diciembre mostró S/ 1,986,712 pero el valor real es S/ 2,098,765 (diferencia: +S/ 112,053)
- **Recomendación:** Re-ejecutar consultas de diciembre 2025 después de esta corrección

### Si otro proyecto muestra números diferentes, verificar:

1. **Filtro de Canal:**
   - Este proyecto: **NO filtra** por canal
   - Si el otro proyecto filtra por `sales_channel = 'NACIONAL'`, tendrá menos ventas

2. **Categorías Excluidas:**
   - Verificar que ambos proyectos excluyan las mismas categorías `[315, 333, 304, 314, 318, 339]`

3. **Campo de Cálculo:**
   - Este proyecto usa: `abs(balance)`
   - Alternativas: `-balance`, `price_subtotal`, `price_total`
   - Diferencia esperada si usan `-balance`: ~1-5% de variación por notas de crédito

4. **Línea Internacional:**
   - Este proyecto excluye ventas donde `commercial_line_national_id.name` contiene 'VENTA INTERNACIONAL'

---

## 📈 Tendencia de Ventas 2025

```
Diciembre: ████████████████████████ 7.9M (pico)
Noviembre: ████████████████ 6.0M
Mayo:      ████████████████ 5.6M
Marzo:     ████████████████ 5.2M
Febrero:   ████████████ 4.4M
Abril:     ████████████ 4.3M
Septiembre:████████████ 4.7M
Octubre:   ███████████ 4.2M
Agosto:    ███████████ 4.0M
Julio:     ██████████ 3.5M
Junio:     █████████ 3.3M
Enero:     █████ 1.7M (inicio de operaciones)
```

**Crecimiento anual:** Enero (1.7M) → Diciembre (7.9M) = **+362%**

---

## 🛠️ Para Comparar con Otro Proyecto

### Paso 1: Ejecutar consulta similar
```python
# En el otro proyecto, ejecutar:
from odoo_manager import OdooManager
om = OdooManager()

# Total 2025
sales = om.get_sales_lines(date_from='2025-01-01', date_to='2025-12-31', limit=50000)
total = sum(abs(float(s.get('balance', 0))) for s in sales)
print(f"Total 2025: S/ {total:,.0f}")
print(f"Registros: {len(sales)}")
```

### Paso 2: Comparar resultados
- Si el total es **mayor** → el otro proyecto incluye ventas adicionales (ej: canal internacional)
- Si el total es **menor** → el otro proyecto tiene filtros más estrictos
- Si hay **pequeñas diferencias** (±5%) → probablemente diferencias en el manejo de notas de crédito

### Paso 3: Verificar filtros
Use el script `verificar_filtros_otro_proyecto.py` incluido en este repositorio para comparar los filtros aplicados.

---

## 📝 Notas Adicionales

- **Fecha de generación:** 16 de enero de 2026
- **Fuente de datos:** Odoo ERP (amah.odoo.com)
- **Base de datos:** amah-main-9110254
- **Proyecto:** Dashboard de Ventas Farmacéuticas - Backup
- **Repositorio:** https://github.com/jonathancerda-hub/dashboard-ventas

---

## 🔗 Archivos Relacionados

- `script_para_otro_proyecto.py` - Script de diagnóstico para ejecutar en otro proyecto
- `verificar_filtros_otro_proyecto.py` - Script para comparar filtros entre proyectos
- `manual.html` - Documentación del sistema explicando la inversión de balance
- `odoo_manager.py` - Clase con la lógica de extracción de datos de Odoo

---

**Última actualización:** 16 de enero de 2026
