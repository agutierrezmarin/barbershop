# Dos proyectos Django en el mismo VPS OVH — Sin dominio, solo IP

> **Proyecto 1 (ya desplegado):** Tienda de Abarrotes → `http://66.70.189.161/`  
> **Proyecto 2 (nuevo):** AdmiDent — Sistema Dental → `http://66.70.189.161:8080/`  
> **IP del servidor:** `66.70.189.161`  
> **OS:** Debian 13 / Ubuntu 24.04  
> **Stack compartido:** Nginx · PostgreSQL

---

## Estrategia: puertos diferentes

Sin dominio no es posible usar `server_name` para separar proyectos en el puerto 80.
La solución es asignar un **puerto diferente** a cada proyecto:

```
Internet
   │
   ▼
 Nginx  ◄─── escucha en :80 y :8080
   │
   ├── 66.70.189.161:80    ──►  /run/tienda.sock     ──►  Gunicorn (tienda)    ← YA FUNCIONA
   │
   └── 66.70.189.161:8080  ──►  /run/dentalcare.sock ──►  Gunicorn (dentalcare) ← NUEVO

PostgreSQL
   ├── tienda_db       ← usuario: tienda_user   (sin cambios)
   └── dentalcare_db   ← usuario: dentalcare_user (nuevo)
```

**Lo que NO se toca del proyecto existente:**
- Su servicio Gunicorn y socket
- Su bloque Nginx en puerto 80
- Su base de datos y usuario PostgreSQL
- Su directorio y entorno virtual

---

## Paso 1 — Verificar el estado actual

Antes de tocar nada, confirmar que la tienda sigue funcionando:

```bash
sudo systemctl status nginx
sudo systemctl status postgresql
curl -I http://66.70.189.161/
# Debe responder HTTP 200 o 302
```

Ver los sockets activos y los bloques Nginx habilitados:

```bash
ls /run/*.sock
ls /etc/nginx/sites-enabled/
```

Anotar el nombre del servicio Gunicorn de la tienda (lo necesitarás para no confundirte):

```bash
sudo systemctl list-units --type=service | grep -i gunicorn
```

---

## Paso 2 — Abrir el puerto 8080 en el firewall

```bash
sudo ufw allow 8080/tcp
sudo ufw status
# Debe mostrar 8080/tcp ALLOW
```

---

## Paso 3 — Crear usuario del sistema para AdmiDent

```bash
sudo adduser dentalcare
sudo usermod -aG www-data dentalcare
```

---

## Paso 4 — Crear la base de datos PostgreSQL para AdmiDent

PostgreSQL ya está corriendo. Solo agregar una BD nueva, **sin tocar la de la tienda**:

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE dentalcare_db;
CREATE USER dentalcare_user WITH PASSWORD 'PASSWORD_MUY_SEGURO';
ALTER ROLE dentalcare_user SET client_encoding TO 'utf8';
ALTER ROLE dentalcare_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE dentalcare_user SET timezone TO 'America/La_Paz';
GRANT ALL PRIVILEGES ON DATABASE dentalcare_db TO dentalcare_user;
\q
```

Verificar que la BD de la tienda sigue intacta:

```bash
sudo -u postgres psql -c "\l"
# Deben aparecer AMBAS bases de datos
```

---

## Paso 5 — Subir el código de AdmiDent

```bash
su - dentalcare
cd /home/dentalcare
git clone https://github.com/TU_USUARIO/dentalcare.git app
```

O copiar desde tu máquina local por SCP:

```bash
# Ejecutar en tu máquina local (Linux/Mac)
scp -r /home/alejandro/Documents/proyectos-django/dentalcare \
       dentalcare@66.70.189.161:/home/dentalcare/app
```

---

## Paso 6 — Entorno virtual y dependencias

```bash
cd /home/dentalcare/app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

---

## Paso 7 — Archivo .env de AdmiDent

```bash
nano /home/dentalcare/.env
```

```ini
SECRET_KEY=genera-una-clave-nueva-aqui
DEBUG=False
ALLOWED_HOSTS=66.70.189.161

DB_NAME=dentalcare_db
DB_USER=dentalcare_user
DB_PASSWORD=PASSWORD_MUY_SEGURO
DB_HOST=localhost
DB_PORT=5432
```

```bash
chmod 600 /home/dentalcare/.env
```

Generar una `SECRET_KEY` segura:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Paso 8 — Migraciones, estáticos y superusuario

```bash
cd /home/dentalcare/app
source venv/bin/activate

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

mkdir -p media
chmod 755 media
```

---

## Paso 9 — Servicio Gunicorn para AdmiDent

Nombres de socket y servicio completamente diferentes a los de la tienda.

### 9.1 Socket

```bash
sudo nano /etc/systemd/system/dentalcare.socket
```

```ini
[Unit]
Description=Gunicorn socket — AdmiDent

[Socket]
ListenStream=/run/dentalcare.sock

[Install]
WantedBy=sockets.target
```

### 9.2 Servicio

```bash
sudo nano /etc/systemd/system/dentalcare.service
```

```ini
[Unit]
Description=Gunicorn daemon — AdmiDent
Requires=dentalcare.socket
After=network.target

[Service]
User=dentalcare
Group=www-data
WorkingDirectory=/home/dentalcare/app
EnvironmentFile=/home/dentalcare/.env
ExecStart=/home/dentalcare/app/venv/bin/gunicorn \
          --access-logfile - \
          --workers 2 \
          --bind unix:/run/dentalcare.sock \
          dentalcare.wsgi:application

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### 9.3 Activar

```bash
sudo systemctl daemon-reload
sudo systemctl enable dentalcare.socket
sudo systemctl start  dentalcare.socket
sudo systemctl enable dentalcare
sudo systemctl start  dentalcare
```

Verificar que ambos sockets existen:

```bash
ls /run/*.sock
# tienda.sock  dentalcare.sock
```

---

## Paso 10 — Bloque Nginx para AdmiDent en puerto 8080

Se agrega un **archivo nuevo**. El bloque de la tienda en puerto 80 no se toca.

```bash
sudo nano /etc/nginx/sites-available/dentalcare
```

```nginx
server {
    listen 8080;
    server_name 66.70.189.161;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/dentalcare/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/dentalcare/app/media/;
        expires 7d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/dentalcare.sock;
        proxy_read_timeout    300;
        proxy_connect_timeout 300;
    }
}
```

Habilitar solo este nuevo bloque:

```bash
sudo ln -s /etc/nginx/sites-available/dentalcare /etc/nginx/sites-enabled/
```

Verificar la configuración **antes** de recargar:

```bash
sudo nginx -t
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

Recargar Nginx sin cortar conexiones de la tienda:

```bash
sudo systemctl reload nginx
```

---

## Paso 11 — Permisos de acceso para Nginx

```bash
sudo chmod 710 /home/dentalcare
sudo chmod -R 755 /home/dentalcare/app/staticfiles
sudo chmod -R 755 /home/dentalcare/app/media
```

---

## Paso 12 — Verificación final

### Tienda — debe seguir funcionando igual que antes

```bash
curl -I http://66.70.189.161/
# HTTP/1.1 302 Found  (redirige a /login/)
```

### AdmiDent — debe responder en el puerto 8080

```bash
curl -I http://66.70.189.161:8080/
# HTTP/1.1 302 Found  (redirige a /login/)
```

Abrir en el navegador:
- **Tienda:** `http://66.70.189.161/`
- **AdmiDent:** `http://66.70.189.161:8080/`

Estado global de todos los servicios:

```bash
sudo systemctl status nginx postgresql
sudo journalctl -u dentalcare -n 30
ls -la /run/*.sock
```

---

## Resumen: qué tiene cada proyecto por separado

| Componente | Tienda (proyecto 1) | AdmiDent (proyecto 2) |
|---|---|---|
| URL de acceso | `http://66.70.189.161/` | `http://66.70.189.161:8080/` |
| Puerto Nginx | `80` | `8080` |
| Usuario del sistema | (el que ya tienes) | `dentalcare` |
| Entorno virtual | su propio `venv/` | `/home/dentalcare/app/venv/` |
| Archivo `.env` | su propio `.env` | `/home/dentalcare/.env` |
| BD PostgreSQL | `tienda_db` | `dentalcare_db` |
| Usuario PostgreSQL | `tienda_user` | `dentalcare_user` |
| Socket Gunicorn | `/run/tienda.sock` | `/run/dentalcare.sock` |
| Servicio systemd | `tienda.service` | `dentalcare.service` |
| Bloque Nginx | `sites-available/tienda` | `sites-available/dentalcare` |
| SSL | No aplica (sin dominio) | No aplica (sin dominio) |

---

## Comandos de mantenimiento para AdmiDent

```bash
# Actualizar código
cd /home/dentalcare/app && git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart dentalcare      # solo reinicia AdmiDent, no toca la tienda

# Ver logs en tiempo real
sudo journalctl -u dentalcare -f

# Backup de la BD de AdmiDent
sudo -u postgres pg_dump dentalcare_db > ~/backup_dental_$(date +%Y%m%d).sql
```

---

## Problemas comunes

### `curl http://66.70.189.161:8080/` no responde (connection refused)
El puerto no está abierto o Nginx no escucha en él:
```bash
sudo ufw allow 8080/tcp
sudo ufw status
sudo nginx -t && sudo systemctl reload nginx
```

### Nginx devuelve 502 Bad Gateway
Gunicorn no está corriendo:
```bash
sudo systemctl status dentalcare
sudo systemctl restart dentalcare
sudo journalctl -u dentalcare -n 20
```

### Nginx devuelve 403 en /static/ o /media/
```bash
sudo chmod 710 /home/dentalcare
sudo chmod -R 755 /home/dentalcare/app/staticfiles
sudo chmod -R 755 /home/dentalcare/app/media
```

### Error `DisallowedHost` en los logs
La IP no está en `ALLOWED_HOSTS` del `.env`:
```bash
nano /home/dentalcare/.env
# ALLOWED_HOSTS=66.70.189.161
sudo systemctl restart dentalcare
```

### La tienda dejó de funcionar
Verificar que su bloque Nginx sigue habilitado y que `nginx -t` no reporta errores:
```bash
ls /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

*La regla de oro: cada proyecto es una isla — usuario, entorno, BD, socket y puerto propios.*
