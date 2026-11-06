# Instalar TimescaleDB

El proyecto usa PostgreSQL con la extensión TimescaleDB. TimescaleDB es un paquete del
sistema (no se instala con `pip`) y debe instalarse en el servidor PostgreSQL **antes** de
ejecutar `python3 manage.py migrate`.

Esta guía es para Debian/Ubuntu con PostgreSQL 15. Si usas otra versión, cambia el `15` por
la tuya (`psql --version` te la muestra).

## Antes de empezar: ¿ya tienes TimescaleDB?

Ejecuta:

```bash
sudo -u postgres psql -c "SELECT name, default_version, installed_version FROM pg_available_extensions WHERE name = 'timescaledb';"
```

- **0 filas**: no está instalado. Sigue la guía desde el paso 1.
- **1 fila con `installed_version` vacío**: está instalado en el servidor, pero falta crearlo
  en tu base de datos. Ve al paso 5.
- **1 fila con `installed_version` con número**: ya lo tienes listo en la base `postgres`.
  Para tu base del proyecto, comprueba con el paso 5.

También puedes ver si el paquete está instalado en el sistema:

```bash
dpkg -l | grep timescaledb
```

## 1. Instalar PostgreSQL

Revisa si ya tienes el servidor:

```bash
pg_lsclusters
```

Si aparece una línea con `15 main 5432 online`, ya lo tienes y puedes pasar al paso 2.
Si no aparece nada, instálalo:

```bash
sudo apt update
sudo apt install -y postgresql-15
```

## 2. Instalar TimescaleDB

Agrega el repositorio de Timescale:

```bash
sudo apt install -y gnupg lsb-release wget

wget -qO- https://packagecloud.io/timescale/timescaledb/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/timescaledb.gpg

echo "deb [signed-by=/usr/share/keyrings/timescaledb.gpg] https://packagecloud.io/timescale/timescaledb/debian/ $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/timescaledb.list
```

En Ubuntu cambia `debian` por `ubuntu` en la URL.

Instala el paquete:

```bash
sudo apt update
sudo apt install -y timescaledb-2-postgresql-15 timescaledb-tools
```

## 3. Activar TimescaleDB y reiniciar

```bash
sudo timescaledb-tune --quiet --yes --pg-config=/usr/lib/postgresql/15/bin/pg_config
sudo systemctl restart postgresql
```

Comprueba que la biblioteca quedó cargada (debe incluir `timescaledb`):

```bash
sudo -u postgres psql -c "SHOW shared_preload_libraries;"
```

## 4. Crear el usuario y la base de datos

Reemplaza `TU_USUARIO` y `TU_CONTRASEÑA` por los que quieras usar (son los mismos que
pondrás en el `.env`):

```bash
sudo -u postgres psql <<'SQL'
CREATE USER TU_USUARIO WITH PASSWORD 'TU_CONTRASEÑA';
CREATE DATABASE atlas OWNER TU_USUARIO;
SQL
```

Si el usuario o la base ya existen, mostrará `already exists`; no pasa nada.

## 5. Crear la extensión

```bash
sudo -u postgres psql -d atlas -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
```

Comprueba que quedó instalada:

```bash
sudo -u postgres psql -d atlas -c "\dx timescaledb"
```

Debe aparecer una fila con `timescaledb` y su versión.

## 6. Ejecutar las migraciones

Revisa que el `.env` tenga los datos de la base (`DB_NAME`, `DB_USER`, `DB_PASSWORD`,
`DB_HOST`, `DB_PORT`) y ejecuta:

```bash
python3 manage.py migrate
```

---

## Errores frecuentes

| Error | Solución |
|-------|----------|
| `404 Not Found` al usar `apt install` | Ejecuta `sudo apt update` y repite el comando. |
| `extension "timescaledb" is not available` | Falta el paso 2, o instalaste el paquete de otra versión de PostgreSQL. Revisa la versión con `pg_lsclusters`. |
| `must be superuser` / `permission denied to create extension` | Crea la extensión como `postgres` (paso 5). |
| `must be loaded via shared_preload_libraries` | Repite el paso 3 y reinicia PostgreSQL. |
| `connection refused` | Revisa el puerto con `pg_lsclusters` y ponlo en `DB_PORT` del `.env`. |
| `password authentication failed` | La contraseña del `.env` no coincide con la del usuario creado en el paso 4. |
| `relation "lecturas" already a hypertable` | Una migración anterior falló a medias. Corrige la causa y vuelve a ejecutar `python3 manage.py migrate`. |
| `no existe la relación «roles_sistema»` (en `usuarios.0002_seed_roles_sistema`) | La base ya tenía registrada la `0001_initial` **antigua** (tablas como `Roles_Sistema`, `Usuarios`…). Reinicia la base como se indica abajo. |

## Reiniciar una base con el esquema antiguo (solo si está vacía)

Si `django_migrations` ya tiene `usuarios.0001_initial` y `estaciones.0001_initial` de la
versión anterior, Django las da por aplicadas y nunca crea las tablas nuevas. Comprueba que
no hay datos que conservar y recrea la base:

```bash
sudo -u postgres psql <<'SQL'
DROP DATABASE atlas;
CREATE DATABASE atlas OWNER TU_USUARIO;
SQL
sudo -u postgres psql -d atlas -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
python3 manage.py migrate
```

!!! warning
    `DROP DATABASE` borra todo el contenido de la base. Úsalo solo en desarrollo o con la
    base vacía.