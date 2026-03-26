"""
Script de configuración inicial del sistema Cuervo Negro.
Ejecutar con: python manage.py shell < setup_inicial.py
"""
from django.contrib.auth import get_user_model
from apps.servicios.models import CategoriaServicio, Servicio
from apps.inventario.models import CategoriaProducto, Producto

User = get_user_model()

print("=== CUERVO NEGRO - Setup Inicial ===")

# ── Superusuario admin ──────────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@cuervonegro.bo',
        password='admin123',
        first_name='Administrador',
        last_name='General',
        rol='admin'
    )
    print("✔ Usuario admin creado (admin / admin123)")
else:
    print("  Usuario admin ya existe")

# ── Categorías de servicio ──────────────────────────────────────────────────────
categorias_svc = ['Corte', 'Barba', 'Combos', 'Tattoo', 'Tratamientos']
for nombre in categorias_svc:
    cat, created = CategoriaServicio.objects.get_or_create(nombre=nombre)
    if created:
        print(f"✔ Categoría servicio: {nombre}")

# ── Servicios ───────────────────────────────────────────────────────────────────
corte_cat = CategoriaServicio.objects.get(nombre='Corte')
barba_cat = CategoriaServicio.objects.get(nombre='Barba')
combo_cat = CategoriaServicio.objects.get(nombre='Combos')

servicios_data = [
    ('Corte Clásico', corte_cat, 50, 30),
    ('Corte Degradado', corte_cat, 60, 45),
    ('Corte + Estilo', corte_cat, 70, 45),
    ('Arreglo de Barba', barba_cat, 40, 20),
    ('Barba Completa', barba_cat, 55, 30),
    ('Combo Corte + Barba', combo_cat, 90, 60),
    ('Combo Premium', combo_cat, 110, 75),
]
for nombre, cat, precio, duracion in servicios_data:
    svc, created = Servicio.objects.get_or_create(
        nombre=nombre,
        defaults={'categoria': cat, 'precio': precio, 'duracion_minutos': duracion}
    )
    if created:
        print(f"✔ Servicio: {nombre} (Bs.{precio})")

# ── Productos inventario ────────────────────────────────────────────────────────
cat_prod, _ = CategoriaProducto.objects.get_or_create(nombre='Cuidado Capilar')
cat_acc, _ = CategoriaProducto.objects.get_or_create(nombre='Accesorios')

productos_data = [
    ('Pomada Fijadora', cat_prod, 25, 55, 10, 5),
    ('Cera para Cabello', cat_prod, 20, 45, 8, 3),
    ('Gel Fuerte', cat_prod, 15, 35, 15, 5),
    ('Aceite de Barba', cat_prod, 30, 70, 6, 3),
    ('Shampoo Hombre', cat_prod, 40, 80, 10, 4),
    ('Peine de Madera', cat_acc, 10, 25, 20, 5),
]
for nombre, cat, precio_c, precio_v, stock, stock_min in productos_data:
    prod, created = Producto.objects.get_or_create(
        nombre=nombre,
        defaults={
            'categoria': cat, 'precio_compra': precio_c,
            'precio_venta': precio_v, 'stock_actual': stock, 'stock_minimo': stock_min
        }
    )
    if created:
        print(f"✔ Producto: {nombre} (Stock:{stock})")

print("\n✔ Setup completado. Accede en: http://127.0.0.1:8000")
print("  Usuario: admin | Contraseña: admin123")
print("  Crea barberos desde: /admin/ → Barberos → Añadir barbero")
