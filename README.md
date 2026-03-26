# ☠ CUERVO NEGRO — Sistema de Gestión Barber & Tattoo

Sistema de gestión integral para la barbería **Cuervo Negro Barber-Tattoo**, desarrollado con **Django 5 + PostgreSQL**.

---

## 🛠 Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Backend | Django 5.0 |
| Base de datos | PostgreSQL |
| Frontend | Bootstrap 5 + Bootstrap Icons |
| Tipografía | Bebas Neue + Rajdhani + Share Tech Mono |
| Servidor | Gunicorn + Nginx |

---

## 📦 Módulos del Sistema

| Módulo | App Django | Descripción |
|--------|-----------|-------------|
| Autenticación | `apps.accounts` | Usuarios con roles: Admin, Barbero, Recepcionista |
| Citas | `apps.citas` | Agendamiento con detección de conflictos |
| Clientes | `apps.clientes` | Fichas, historial, preferencias, notas |
| Barberos | `apps.barberos` | Perfiles, horarios laborales, asistencia |
| Servicios | `apps.servicios` | Catálogo de servicios y precios |
| Ventas | `apps.ventas` | Registro de cobros, métodos de pago, corte de caja |
| Inventario | `apps.inventario` | Productos, stock, alertas, movimientos |
| Reportes | `apps.reportes` | Ingresos, servicios más vendidos, barberos top |
| Notificaciones | `apps.notificaciones` | Base para integración WhatsApp/SMS |

---

## ⚡ Instalación Rápida

### 1. Crear entorno virtual e instalar dependencias

```bash
cd cuervo_negro/
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 2. Configurar PostgreSQL

```sql
-- En psql como superusuario:
CREATE DATABASE cuervo_negro_db;
CREATE USER cuervo_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE cuervo_negro_db TO cuervo_user;
```

Luego editar `cuervo_negro/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cuervo_negro_db',
        'USER': 'cuervo_user',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Migraciones y setup inicial

```bash
python manage.py migrate
python manage.py shell < setup_inicial.py
```

### 4. Iniciar servidor de desarrollo

```bash
python manage.py runserver
```

Accede en: **http://127.0.0.1:8000**

- Usuario: `admin`
- Contraseña: `admin123`

---

## 👥 Roles y Permisos

| Rol | Acceso |
|-----|--------|
| **Admin** | Todo el sistema, incluyendo reportes financieros |
| **Barbero** | Su agenda, clientes, registro de servicios |
| **Recepcionista** | Citas, clientes, ventas. Sin reportes financieros |

---

## 🗓 Flujo Principal

```
Cliente llama → Recepcionista abre Nueva Cita
  → Sistema valida disponibilidad del barbero
  → Sistema detecta conflictos de horario
  → Cita queda en estado PENDIENTE

Día del servicio:
  → Barbero atiende → Estado: ATENDIDO
  → Recepcionista registra venta (servicio + productos)
  → Stock de productos se descuenta automáticamente
  → Al final del día: Corte de Caja
```

---

## 📁 Estructura del Proyecto

```
cuervo_negro/
├── apps/
│   ├── accounts/       # Modelo de usuario personalizado
│   ├── citas/          # Agendamiento y agenda por barbero
│   ├── clientes/       # Fichas de clientes
│   ├── barberos/       # Perfiles, horarios, asistencia
│   ├── servicios/      # Catálogo de servicios
│   ├── ventas/         # Ventas y corte de caja
│   ├── inventario/     # Productos y stock
│   ├── reportes/       # Reportes y estadísticas
│   └── notificaciones/ # Base para WhatsApp/SMS
├── templates/          # Templates HTML con diseño dark
├── static/             # CSS, JS, imágenes
├── cuervo_negro/       # Configuración del proyecto
├── requirements.txt
├── setup_inicial.py    # Datos de ejemplo
└── manage.py
```

---

## 🚀 Despliegue en Producción (VPS Debian/Ubuntu)

```bash
# Gunicorn como servicio
gunicorn --workers 3 --bind unix:/run/cuervonegro.sock cuervo_negro.wsgi:application

# Nginx virtualhost apunta al socket
# DEBUG = False en settings.py
# ALLOWED_HOSTS = ['tu-dominio.com', 'IP_del_servidor']
# Ejecutar: python manage.py collectstatic
```

---

## 🔮 Próximas Funcionalidades

- [ ] Integración WhatsApp API (recordatorios de citas)
- [ ] App móvil para clientes (agendamiento online)
- [ ] Módulo de tattoo con galería de diseños
- [ ] Facturación electrónica

---

**☠ Cuervo Negro Barber-Tattoo** — Sistema desarrollado con Django 5 by Example
