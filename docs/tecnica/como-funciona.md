# Cómo funciona

## Estructura

```
config/       Configuración de Django (settings, urls)
estaciones/   Modelos, serializers y vistas de la API
usuarios/     App de usuarios
docs/         Esta documentación (MkDocs)
atlas.sql     Esquema de referencia de PostgreSQL/TimescaleDB
```

## Flujo de una petición

```
Cliente → config/urls.py → estaciones/urls.py (router) → ViewSet → Serializer → Modelo → PostgreSQL/TimescaleDB
```

Todas las rutas cuelgan de `/api/v1/`.

## Endpoints

| Ruta | Descripción |
|------|-------------|
| `/api/v1/estaciones/` | CRUD de estaciones |
| `/api/v1/subestaciones/` | CRUD de los dispositivos físicos de una estación |
| `/api/v1/lecturas/` | Lecturas meteorológicas. Filtro: `?estacion=<id>` |
| `/api/v1/telemetria/` | Batería, panel solar y señal de una subestación |
| `/admin/` | Panel de administración de Django |

Cada ruta es un `ModelViewSet` de DRF: `GET` (lista y detalle), `POST`, `PUT/PATCH` y `DELETE`.
Las rutas de detalle de lecturas y telemetría identifican una fila por su clave compuesta:
`<estacion_id>,<fecha_hora ISO-8601>` y `<subestacion_id>,<fecha_hora ISO-8601>`, respectivamente.

## Modelos principales

- **Estacion**: nombre, ubicación, coordenadas, estado, última conexión.
- **Subestacion**: dispositivo físico de una estación. Se crea una subestación principal al crear una estación desde Django.
- **Lectura**: temperatura, humedad, viento, lluvia, radiación solar, UV, presión, etc.
- **TelemetriaDispositivo**: estado de batería, panel solar y señal.
- **ApiKey**: llave por subestación (se guarda solo el hash y un prefijo visible).
- **UsuarioEstacion / RolEstacion**: asignación de usuarios a estaciones con un rol.

## Configuración

La conexión a PostgreSQL se lee de `.env`. Se puede usar una URL de proveedor:

```env
DATABASE_URL=postgresql://usuario:contraseña@host:5432/base
DB_SSLMODE=require
```

O definir las variables por separado:

| Variable | Uso |
|----------|-----|
| `DATABASE_URL` | URL PostgreSQL del proveedor (opcional si se usan variables `DB_*`) |
| `DB_NAME` | Nombre de la base de datos |
| `DB_USER` | Usuario |
| `DB_PASSWORD` | Contraseña |
| `DB_HOST` | Servidor |
| `DB_PORT` | Puerto |
| `DB_SSLMODE` | Modo SSL de PostgreSQL; usar `require` en el proveedor alojado |

Las tablas y catálogos se crean con las migraciones de Django; no importes `atlas.sql`.
La migración de TimescaleDB crea la extensión, hypertables, políticas de compresión y
agregados continuos. El servidor debe tener TimescaleDB disponible y permitir
`CREATE EXTENSION`; si no, `migrate` falla explícitamente en esa migración.
