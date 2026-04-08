# Tercer Proyecto Django en el mismo VPS OVH — Cuervo Negro

> **Proyecto 1 (ya desplegado):** Tienda de Abarrotes → `http://66.70.189.161/`
> **Proyecto 2 (ya desplegado):** AdmiDent — Sistema Dental → `http://66.70.189.161:8080/`
> **Proyecto 3 (nuevo):** Cuervo Negro — Barber & Tattoo → `http://66.70.189.161:8081/`
> **IP del servidor:** `66.70.189.161`
> **OS:** Debian 13 / Ubuntu 24.04
> **Stack compartido:** Nginx · PostgreSQL

---

## Estrategia: un puerto más

Sin dominio no es posible usar `server_name` para separar proyectos en el puerto 80.
Cada proyecto ocupa un puerto distinto:

```
Internet
   │
   ▼
 Nginx  ◄─── escucha en :80, :8080 y :8081
   │
   ├── 66.70.189.161:80    ──►  /run/tienda.sock       ──►  Gunicorn (tienda)       ← YA FUNCIONA
   ├── 66.70.189.161:8080  ──►  /run/dentalcare.sock   ──►  Gunicorn (dentalcare)   ← YA FUNCIONA
   └── 66.70.189.161:8081  ──►  /run/cuervo_negro.sock ──►  Gunicorn (cuervo_negro) ← NUEVO

PostgreSQL
   ├── tienda_db        ← usuario: tienda_user      (sin cambios)
   ├── dentalcare_db    ← usuario: dentalcare_user  (sin cambios)
   └── cuervo_negro_db  ← usuario: cuervo_negro_user (nuevo)
```

**Lo que NO se toca de los proyectos existentes:**
- Sus servicios Gunicorn y sockets
- Sus bloques Nginx en puertos 80 y 8080
- Sus bases de datos y usuarios PostgreSQL
- Sus directorios y entornos virtuales

---

## Paso 1 — Verificar el estado actual

Antes de tocar nada, confirmar que los dos proyectos existentes siguen funcionando:

```bash
sudo systemctl status nginx
sudo systemctl status postgresql
curl -I http://66.70.189.161/
curl -I http://66.70.189.161:8080/
# Ambos deben responder HTTP 200 o 302
```

Ver los sockets activos y los bloques Nginx habilitados:

```bash
ls /run/*.sock
ls /etc/nginx/sites-enabled/
```

Listar los servicios Gunicorn existentes para no confundirse:

```bash
sudo systemctl list-units --type=service | grep -i gunicorn
```

---

## Paso 2 — Abrir el puerto 8081 en el firewall

```bash
sudo ufw allow 8081/tcp
sudo ufw status
# Debe mostrar 8081/tcp ALLOW
```

---

## Paso 3 — Crear usuario del sistema para Cuervo Negro

```bash
sudo adduser cuervo_negro
sudo usermod -aG www-data cuervo_negro
```

---

## Paso 4 — Crear la base de datos PostgreSQL para Cuervo Negro

PostgreSQL ya está corriendo. Solo agregar una BD nueva, **sin tocar las de tienda y dentalcare**:

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE cuervo_negro_db;
CREATE USER cuervo_negro_user WITH PASSWORD 'PASSWORD_MUY_SEGURO';
ALTER ROLE cuervo_negro_user SET client_encoding TO 'utf8';
ALTER ROLE cuervo_negro_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE cuervo_negro_user SET timezone TO 'America/La_Paz';
GRANT ALL PRIVILEGES ON DATABASE cuervo_negro_db TO cuervo_negro_user;
\q
```

Verificar que las otras BDs siguen intactas:

```bash
sudo -u postgres psql -c "\l"
# Deben aparecer las TRES bases de datos
```

---

## Paso 5 — Subir el código de Cuervo Negro

### Opción A — Git

```bash
su - cuervo_negro
cd /home/cuervo_negro
git clone https://github.com/TU_USUARIO/cuervo_negro.git app
```

### Opción B — rsync desde tu máquina local

```bash
# Ejecutar en tu máquina local
rsync -avz \
  --exclude 'venv_barber/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'media/' \
  --exclude 'staticfiles/' \
  --exclude '.env' \
  /home/alejandro/Documents/proyectos-django/cuervo_negro/ \
  cuervo_negro@66.70.189.161:/home/cuervo_negro/app/
```

---

## Paso 6 — Entorno virtual y dependencias

```bash
cd /home/cuervo_negro/app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

El `requirements.txt` incluye:
- `Django==5.0.6`
- `psycopg2-binary`
- `Pillow`
- `gunicorn==22.0.0`
- `python-decouple==3.8`

---

## Paso 7 — Archivo .env de Cuervo Negro

```bash
nano /home/cuervo_negro/.env
```

```ini
SECRET_KEY=genera-una-clave-nueva-aqui
DEBUG=False
ALLOWED_HOSTS=66.70.189.161

DB_ENGINE=django.db.backends.postgresql
DB_NAME=cuervo_negro_db
DB_USER=cuervo_negro_user
DB_PASSWORD=PASSWORD_MUY_SEGURO
DB_HOST=localhost
DB_PORT=5432

LANGUAGE_CODE=es-bo
TIME_ZONE=America/La_Paz
```

```bash
chmod 600 /home/cuervo_negro/.env
```

Generar una `SECRET_KEY` segura:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Paso 8 — Migraciones, estáticos y superusuario

```bash
cd /home/cuervo_negro/app
source venv/bin/activate

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

mkdir -p media
chmod 755 media
```

---

## Paso 9 — Servicio Gunicorn para Cuervo Negro

Nombres de socket y servicio completamente diferentes a los de tienda y dentalcare.

### 9.1 Socket

```bash
sudo nano /etc/systemd/system/cuervo_negro.socket
```

```ini
[Unit]
Description=Gunicorn socket — Cuervo Negro

[Socket]
ListenStream=/run/cuervo_negro.sock

[Install]
WantedBy=sockets.target
```

### 9.2 Servicio

```bash
sudo nano /etc/systemd/system/cuervo_negro.service
```

```ini
[Unit]
Description=Gunicorn daemon — Cuervo Negro Barber & Tattoo
Requires=cuervo_negro.socket
After=network.target

[Service]
User=cuervo_negro
Group=www-data
WorkingDirectory=/home/cuervo_negro/app
EnvironmentFile=/home/cuervo_negro/.env
ExecStart=/home/cuervo_negro/app/venv/bin/gunicorn \
          --access-logfile - \
          --workers 2 \
          --bind unix:/run/cuervo_negro.sock \
          cuervo_negro.wsgi:application

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### 9.3 Activar

```bash
sudo systemctl daemon-reload
sudo systemctl enable cuervo_negro.socket
sudo systemctl start  cuervo_negro.socket
sudo systemctl enable cuervo_negro
sudo systemctl start  cuervo_negro
```

Verificar que los tres sockets existen:

```bash
ls /run/*.sock
# tienda.sock  dentalcare.sock  cuervo_negro.sock
```

---

## Paso 10 — Bloque Nginx para Cuervo Negro en puerto 8081

Se agrega un **archivo nuevo**. Los bloques de tienda (80) y dentalcare (8080) no se tocan.

```bash
sudo nano /etc/nginx/sites-available/cuervo_negro
```

```nginx
server {
    listen 8081;
    server_name 66.70.189.161;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/cuervo_negro/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/cuervo_negro/app/media/;
        expires 7d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/cuervo_negro.sock;
        proxy_read_timeout    300;
        proxy_connect_timeout 300;
    }
}
```

Habilitar solo este nuevo bloque:

```bash
sudo ln -s /etc/nginx/sites-available/cuervo_negro /etc/nginx/sites-enabled/
```

Verificar la configuración **antes** de recargar:

```bash
sudo nginx -t
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

Recargar Nginx sin cortar conexiones de los proyectos existentes:

```bash
sudo systemctl reload nginx
```

---

## Paso 11 — Permisos de acceso para Nginx

```bash
sudo chmod 710 /home/cuervo_negro
sudo chmod -R 755 /home/cuervo_negro/app/staticfiles
sudo chmod -R 755 /home/cuervo_negro/app/media
```

---

## Paso 12 — Verificación final

### Tienda — debe seguir funcionando igual que antes

```bash
curl -I http://66.70.189.161/
# HTTP/1.1 302 Found
```

### AdmiDent — debe seguir funcionando igual que antes

```bash
curl -I http://66.70.189.161:8080/
# HTTP/1.1 302 Found
```

### Cuervo Negro — debe responder en el puerto 8081

```bash
curl -I http://66.70.189.161:8081/
# HTTP/1.1 302 Found  (redirige a /accounts/login/)
```

Abrir en el navegador:
- **Tienda:** `http://66.70.189.161/`
- **AdmiDent:** `http://66.70.189.161:8080/`
- **Cuervo Negro:** `http://66.70.189.161:8081/`

Estado global de todos los servicios:

```bash
sudo systemctl status nginx postgresql
sudo journalctl -u cuervo_negro -n 30
ls -la /run/*.sock
```

---

## Resumen: qué tiene cada proyecto por separado

| Componente | Tienda | AdmiDent | Cuervo Negro |
|---|---|---|---|
| URL de acceso | `:80` | `:8080` | `:8081` |
| Puerto Nginx | `80` | `8080` | `8081` |
| Usuario del sistema | (el tuyo) | `dentalcare` | `cuervo_negro` |
| Directorio | `/home/.../tienda` | `/home/dentalcare/app` | `/home/cuervo_negro/app` |
| Archivo `.env` | su propio `.env` | `/home/dentalcare/.env` | `/home/cuervo_negro/.env` |
| BD PostgreSQL | `tienda_db` | `dentalcare_db` | `cuervo_negro_db` |
| Usuario PostgreSQL | `tienda_user` | `dentalcare_user` | `cuervo_negro_user` |
| Socket Gunicorn | `/run/tienda.sock` | `/run/dentalcare.sock` | `/run/cuervo_negro.sock` |
| Servicio systemd | `tienda.service` | `dentalcare.service` | `cuervo_negro.service` |
| Bloque Nginx | `sites-available/tienda` | `sites-available/dentalcare` | `sites-available/cuervo_negro` |
| Módulo WSGI | (el suyo) | `dentalcare.wsgi:application` | `cuervo_negro.wsgi:application` |

---

## Comandos de mantenimiento para Cuervo Negro

```bash
# Actualizar código
cd /home/cuervo_negro/app && git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart cuervo_negro      # solo reinicia este proyecto, no toca los otros

# Ver logs en tiempo real
sudo journalctl -u cuervo_negro -f

# Backup de la BD
sudo -u postgres pg_dump cuervo_negro_db > ~/backup_cuervo_negro_$(date +%Y%m%d).sql
```

---

## Problemas comunes

### `curl http://66.70.189.161:8081/` no responde (connection refused)
El puerto no está abierto o Nginx no escucha en él:
```bash
sudo ufw allow 8081/tcp
sudo ufw status
sudo nginx -t && sudo systemctl reload nginx
```

### Nginx devuelve 502 Bad Gateway
Gunicorn no está corriendo:
```bash
sudo systemctl status cuervo_negro
sudo systemctl restart cuervo_negro
sudo journalctl -u cuervo_negro -n 20
```

### Nginx devuelve 403 en /static/ o /media/
```bash
sudo chmod 710 /home/cuervo_negro
sudo chmod -R 755 /home/cuervo_negro/app/staticfiles
sudo chmod -R 755 /home/cuervo_negro/app/media
```

### Error `DisallowedHost` en los logs
La IP no está en `ALLOWED_HOSTS` del `.env`:
```bash
nano /home/cuervo_negro/.env
# ALLOWED_HOSTS=66.70.189.161
sudo systemctl restart cuervo_negro
```

### Error de zona horaria o localización
El `.env` debe incluir:
```ini
LANGUAGE_CODE=es-bo
TIME_ZONE=America/La_Paz
```
```bash
sudo systemctl restart cuervo_negro
```

### Los proyectos anteriores dejaron de funcionar
Verificar que sus bloques Nginx siguen habilitados y que `nginx -t` no reporta errores:
```bash
ls /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

*La regla de oro: cada proyecto es una isla — usuario, entorno, BD, socket y puerto propios.*
