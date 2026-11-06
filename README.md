# SIWEBA — Backend Django

## Nombre del proyecto
Diseño e implementación de un sistema web para el monitoreo de estaciones meteorológicas basadas en Arduino.

## Breve descripción
La solución consiste en el desarrollo de una plataforma web que permite integrar estaciones meteorológicas de usuarios e instituciones en una red colaborativa. En esta plataforma, los datos generados (temperatura, humedad, presión atmosférica, etc.) pueden ser compartidos y consultados de manera accesible y en tiempo real. El sistema se compone de dos subsistemas interconectados: una estación meteorológica de hardware basada en Arduino y una plataforma web de software desarrollada en Django para almacenar, validar y visualizar los datos.

## Objetivo general
Crear una estación meteorológica funcional con Arduino y una plataforma web para almacenar y consultar libremente los datos que esta recolecta

## Mentor
Dr. Juan José López Cisneros.

## Project Leader
Primitivo Oyoque Vargas

## Integrantes del equipo
- Casandra Jazmín Rodríguez Flores 
- Primitivo Oyoque Vargas

## Estado actual
En desarrollo de una primera versión funcional que corresponderá a un prototipo mínimo viable, el cual estará enfocado en la recolección, almacenamiento, visualización y consulta de datos meteorológicos.

## Estructura del repositorio
```txt
django-backend/      # API y lógica del servidor desarrolladas con Django
    ├── config/          # Configuración general, rutas y despliegue de Django
    ├── estaciones/      # Aplicación para gestionar estaciones meteorológicas
    ├── usuarios/        # Aplicación para gestionar usuarios
    └── docs/            # Documentación técnica del backend
```

## Versión o Sprint actual
Sprint II


## Instrucciones para consultar o reproducir el proyecto
Para comenzar, esto solo es el Backend del proyecto. 
El resto del proyecto se encuntra en la organización principal del repositorio. (https://github.com/orgs/SIWEBA/repositories)

### Ejecución del backend

Clonar el repositorio:
```bash
git clone https://github.com/SIWEBA/django-backend
```

Acceder al directorio del proyecto:
```bash
cd django-backend
```
Instalar las dependencias del proyecto:
```bash
python3 -m pip install -r requirements.txt
```

Configurar la conexión PostgreSQL en `.env` con `DATABASE_URL` o con las variables
`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT`. En el proveedor alojado,
configurar también `DB_SSLMODE=require`.

Crear el esquema y los objetos de TimescaleDB:
```bash
python3 manage.py migrate
```

La base debe tener TimescaleDB habilitado; si `migrate` falla, consulta
`docs/tecnica/instalar-timescaledb.md` (instalación y solución de errores).
Las migraciones crean las tablas, las
hypertables, las políticas y los agregados; no es necesario importar `atlas.sql`.

Ejecutar el servidor de desarrollo de Django:
```bash
python3 manage.py runserver
```

### Visualización de la documentación

```bash
python3 -m pip install -r requirements-docs.txt
```
Luego, puedes iniciar el servidor de documentación con:

```bash
mkdocs serve   # http://127.0.0.1:8000
```