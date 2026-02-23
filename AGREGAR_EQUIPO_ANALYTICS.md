# Cómo agregar la columna "Equipo" en Usuarios Más Activos (Analytics)

Esta guía explica cómo mostrar la columna "Equipo" en la tabla de "Usuarios Más Activos" del dashboard de analytics, mostrando el equipo (ejemplo: PETMEDICA) al que pertenece cada usuario, o vacío si no tiene.

---

## 1. Modificación en el backend (`app.py`)

Busca la función de la vista `/analytics` donde se construye el diccionario `stats` (usualmente cerca de:
`'visits_by_user': [dict(row) for row in analytics_db.get_visits_by_user(days)]`).

Agrega el siguiente bloque después de construir `stats` y antes de renderizar el template:

```python
# Obtener todos los vendedores y equipos
todos_los_vendedores = data_manager.get_all_sellers()
vendedores_por_email = {v['email'].lower(): v for v in todos_los_vendedores if v.get('email')}
equipos_guardados = supabase_manager.read_equipos()  # {equipo_id: [vendedor_id, ...]}
equipos_definidos = [
    {'id': 'petmedica', 'nombre': 'PETMEDICA'},
    {'id': 'agrovet', 'nombre': 'AGROVET'},
    {'id': 'avivet', 'nombre': 'AVIVET'},
    {'id': 'petnutriscience', 'nombre': 'PET NUTRISCIENCE'},
    {'id': 'ecommerce', 'nombre': 'ECOMMERCE'},
]
# Crear un mapa vendedor_id -> equipo_nombre
equipo_por_vendedor = {}
for equipo in equipos_definidos:
    for vendedor_id in equipos_guardados.get(equipo['id'], []):
        equipo_por_vendedor[str(vendedor_id)] = equipo['nombre']
# Asignar equipo a cada usuario activo
for visit in stats['visits_by_user']:
    email = visit.get('user_email', '').lower()
    vendedor = vendedores_por_email.get(email)
    equipo_nombre = ''
    if vendedor:
        vendedor_id = str(vendedor['id'])
        equipo_nombre = equipo_por_vendedor.get(vendedor_id, '')
    visit['equipo'] = equipo_nombre
```

---

## 2. Modificación en el template (`analytics.html`)

Agrega la columna "Equipo" en la tabla de usuarios más activos:

```html
<thead>
    <tr>
        <th>#</th>
        <th>Usuario</th>
        <th>Email</th>
        <th>Equipo</th> <!-- NUEVA COLUMNA -->
        <th>Visitas</th>
        <th>Última Visita</th>
    </tr>
</thead>
<tbody>
    {% for user in stats.visits_by_user %}
    <tr>
        <td>{{ loop.index }}</td>
        <td>{{ user.user_name or 'N/A' }}</td>
        <td>{{ user.user_email }}</td>
        <td>{{ user.equipo or '' }}</td> <!-- NUEVA COLUMNA -->
        <td><span class="badge badge-primary">{{ user.visit_count }}</span></td>
        <td>{{ user.last_visit.strftime('%d/%m/%Y %H:%M') if user.last_visit else 'N/A' }}</td>
    </tr>
    {% endfor %}
</tbody>
```

---

## 3. Resultado esperado

- La tabla mostrará una columna adicional "Equipo".
- Si el usuario pertenece a un equipo, se mostrará el nombre (ejemplo: PETMEDICA).
- Si no pertenece a ningún equipo, la celda aparecerá vacía.

---

**Última actualización:** 19/02/2026
