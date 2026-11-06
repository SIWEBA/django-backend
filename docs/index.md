# SIWEBA Backend

API REST (Django + DRF) para la gestión de estaciones meteorológicas.

## Entorno local

```bash
python3 -m venv venv
source venv/bin/activate

python3 -m pip install -r requirements.txt

cp .env.example .env   # o crea .env con tus variables

python3 manage.py migrate
python3 manage.py runserver
```

## Documentación

Para poder visualizar la documentación del proyecto, primero instala las dependencias necesarias con:

```bash
python3 -m pip install -r requirements-docs.txt
```
Luego, puedes iniciar el servidor de documentación con:

```bash
mkdocs serve   # http://127.0.0.1:8000
```


