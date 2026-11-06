# Cómo se actualiza

## Actualizar el código

```bash
git pull
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 manage.py migrate
```

Reinicia el servidor después de actualizar.

## Cambiar un modelo

1. Edita `estaciones/models.py` (o `usuarios/models.py`).
2. Genera la migración: `python3 manage.py makemigrations`
3. Aplícala: `python3 manage.py migrate`
4. Si cambia el esquema, registra el cambio en una migración. Los objetos que Django
   no puede representar (por ejemplo, hypertables y agregados continuos) deben crearse
   en una migración con `RunSQL`.

No importes `atlas.sql` manualmente: en una base Atlas vacía, `python3 manage.py migrate`
crea el esquema y los objetos de TimescaleDB.

## Conceptos básicos

Un endpoint de la API se construye con cuatro piezas. Cada una tiene un archivo y una tarea:

| Pieza | Archivo | Qué es |
|-------|---------|--------|
| **Modelo** | `models.py` | Clase de Python que representa una tabla de la base de datos. Cada atributo es una columna. Con él se consulta y guarda (`Estacion.objects.all()`). |
| **Serializer** | `serializers.py` | "Traductor" entre el modelo y JSON. Al responder convierte un objeto en JSON. Al recibir datos valida el JSON y lo convierte en un objeto. Define qué campos se exponen. |
| **ViewSet** | `views.py` | Clase que agrupa la lógica del recurso: listar, ver uno, crear, editar y borrar. `ModelViewSet` trae las cinco operaciones ya hechas. Se indica qué datos usa (`queryset`) y con qué serializer. |
| **Router / URL** | `urls.py` | Conecta una ruta (`/api/v1/estaciones/`) con un ViewSet. El router genera solas las rutas de lista y detalle. |

Flujo de una petición:

```text
GET /api/v1/subestaciones/  →  urls.py (router)  →  ViewSet  →  Modelo (consulta la BD)
                                                      ↓
                                      Serializer (objeto → JSON)  →  respuesta
```

Un `ModelViewSet` con el router genera estas rutas y métodos HTTP:

| Método y ruta | Acción |
|---------------|--------|
| `GET /ruta/` | Listar |
| `POST /ruta/` | Crear |
| `GET /ruta/{id}/` | Ver uno |
| `PUT` / `PATCH /ruta/{id}/` | Editar (completo / parcial) |
| `DELETE /ruta/{id}/` | Borrar |

## Añadir un endpoint

Ejemplo: exponer un recurso nuevo `Sensor` en `/api/v1/sensores/`.

**1. Modelo** (`estaciones/models.py`)

```python
class Sensor(models.Model):
    id = models.AutoField(primary_key=True)
    estacion = models.ForeignKey(
        Estacion, on_delete=models.PROTECT, related_name='sensores'
    )
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True, db_default=True)

    class Meta:
        db_table = 'sensores'

    def __str__(self):
        return self.nombre
```

**2. Migración** (crea la tabla en la base)

```bash
python3 manage.py makemigrations estaciones
python3 manage.py migrate
```

**3. Serializer** (`estaciones/serializers.py`). Importa `Sensor` junto a los demás modelos.

```python
class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'   # o una lista: ('id', 'nombre', 'activo')
```

**4. ViewSet** (`estaciones/views.py`). Importa `Sensor` y `SensorSerializer`.

```python
class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.select_related('estacion')
    serializer_class = SensorSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        estacion_id = self.request.query_params.get('estacion')   # /sensores/?estacion=1
        if estacion_id:
            qs = qs.filter(estacion_id=estacion_id)
        return qs
```

**5. Ruta** (`estaciones/urls.py`). Importa `SensorViewSet`.

```python
router.register('sensores', SensorViewSet)
```

**6. Probar**

```bash
python3 manage.py check
python3 manage.py runserver
```

Después abre `http://127.0.0.1:8000/api/v1/sensores/`. Si no necesitas todas las operaciones,
usa `ReadOnlyModelViewSet` (solo lectura) en lugar de `ModelViewSet`.

**Nota:** Los modelos con clave primaria compuesta (`Lectura`, `TelemetriaDispositivo`) necesitan
un `get_object` propio, como se ve en `LecturaViewSet`. Para tablas con `id` normal no hace falta.

## Actualizar dependencias

```bash
python3 -m pip install -U <paquete>
python3 -m pip freeze | grep -i <paquete>   # copia la versión a requirements.txt
```

## Actualizar la documentación

Edita los archivos de `docs/` y registra las páginas nuevas en `nav` de `mkdocs.yml`.

```bash
NO_MKDOCS_2_WARNING=true mkdocs serve   # vista previa en http://127.0.0.1:8000
NO_MKDOCS_2_WARNING=true mkdocs build   # genera site/ (ignorado por git)
```
