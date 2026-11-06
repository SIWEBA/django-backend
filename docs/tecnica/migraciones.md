# Migraciones

Las migraciones de Django crean todo el esquema Atlas (tablas, hypertables de TimescaleDB,
`upsert_lecturas`, agregados continuos y políticas). No hace falta importar `atlas.sql`.

## Requisitos

1. PostgreSQL con TimescaleDB instalado: ver [Instalar TimescaleDB](instalar-timescaledb.md).
2. La extensión creada en la base (como `postgres`):
   `sudo -u postgres psql -d atlas -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"`
3. Credenciales en `.env` (`DATABASE_URL` o `DB_*`).

## Aplicar las migraciones

```bash
source venv/bin/activate
python3 manage.py migrate
```

## Ver el estado

```bash
python3 manage.py showmigrations              # [X] aplicada, [ ] pendiente
python3 manage.py showmigrations estaciones usuarios
python3 manage.py makemigrations --check      # falla si los modelos tienen cambios sin migrar
```

Orden de las migraciones propias:

| App | Migración | Qué hace |
|-----|-----------|----------|
| usuarios | `0001_initial` | Tablas de usuarios y roles de sistema |
| usuarios | `0002_seed_roles_sistema` | Inserta los roles de sistema |
| usuarios | `0003_...` | Valores por defecto en base de datos |
| estaciones | `0001_initial` | Estaciones, subestaciones, lecturas, telemetría, API keys |
| estaciones | `0002_seed_roles_estacion` | Inserta los roles de estación |
| estaciones | `0003_timescaledb` | Hypertables, `upsert_lecturas`, compresión, agregados y políticas |
| estaciones | `0004_...` | Valores por defecto en base de datos |

## Verificar el resultado

```bash
psql -h localhost -U TU_USUARIO -d atlas
```

```sql
SELECT hypertable_name FROM timescaledb_information.hypertables;       -- lecturas, telemetria_dispositivo
SELECT view_name FROM timescaledb_information.continuous_aggregates;   -- lecturas_hora, lecturas_dia
SELECT upsert_lecturas('[]'::jsonb);                                   -- debe ejecutar sin error
```

## Errores frecuentes

| Error | Causa y solución |
|-------|------------------|
| `no existe la relación «roles_sistema»` | La base tiene registrada la `0001_initial` **antigua**. Ver [Reiniciar la base](#reiniciar-la-base-de-desarrollo). |
| `extension "timescaledb" is not available` | TimescaleDB no está instalado: ver la guía de instalación. |
| `must be superuser` al crear la extensión | Créala como `postgres` (ver requisitos). |
| `password authentication failed` | Revisa `DB_USER` / `DB_PASSWORD` en `.env`. |

## Reiniciar la base de desarrollo

Úsalo cuando la base tiene el esquema o el historial de migraciones antiguos y **no hay datos
que conservar**. `DROP DATABASE` borra todo y no debe haber otras conexiones abiertas.

```bash
sudo -u postgres psql <<'SQL'
DROP DATABASE atlas;
CREATE DATABASE atlas OWNER TU_USUARIO;
SQL
sudo -u postgres psql -d atlas -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
python3 manage.py migrate
```

!!! warning
    Nunca lo ejecutes en producción. Allí crea una migración nueva en vez de editar las existentes.
