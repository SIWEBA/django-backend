from django.db import models, transaction
from django.db.models import Q
from django.db.models.functions import Now

from usuarios.models import Usuario


class RolEstacion(models.Model):
    id = models.SmallAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'roles_estacion'
        verbose_name = 'Rol de Estación'
        verbose_name_plural = 'Roles de Estación'

    def __str__(self):
        return self.nombre


class Estacion(models.Model):
    ESTADO_ACTIVA = 'activa'
    ESTADO_INACTIVA = 'inactiva'
    ESTADO_MANTENIMIENTO = 'mantenimiento'
    ESTADOS = [
        (ESTADO_ACTIVA, 'Activa'),
        (ESTADO_INACTIVA, 'Inactiva'),
        (ESTADO_MANTENIMIENTO, 'Mantenimiento'),
    ]

    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_ACTIVA,
        db_default=ESTADO_ACTIVA,
    )
    ultima_conexion = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(db_default=Now(), editable=False)

    class Meta:
        db_table = 'estaciones'
        constraints = [
            models.CheckConstraint(
                condition=Q(estado__in=['activa', 'inactiva', 'mantenimiento']),
                name='ck_estaciones_estado',
            ),
        ]
        verbose_name = 'Estación'
        verbose_name_plural = 'Estaciones'

    def save(self, *args, **kwargs):
        create_default_substation = self._state.adding
        with transaction.atomic():
            super().save(*args, **kwargs)
            if create_default_substation:
                Subestacion.objects.create(
                    estacion=self,
                    nombre='Consola principal',
                )

    def __str__(self):
        return self.nombre


class Subestacion(models.Model):
    id = models.AutoField(primary_key=True)
    estacion = models.ForeignKey(
        Estacion, on_delete=models.PROTECT, related_name='subestaciones'
    )
    nombre = models.CharField(max_length=100)
    activa = models.BooleanField(default=True, db_default=True)
    fecha_creacion = models.DateTimeField(db_default=Now(), editable=False)

    class Meta:
        db_table = 'subestaciones'
        constraints = [
            models.UniqueConstraint(
                fields=['estacion', 'nombre'], name='uq_subestacion_estacion_nombre'
            ),
        ]
        indexes = [
            models.Index(fields=['estacion'], name='idx_subestacion_estacion'),
        ]
        verbose_name = 'Subestación'
        verbose_name_plural = 'Subestaciones'

    def __str__(self):
        return f'{self.estacion} - {self.nombre}'


class UsuarioEstacion(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]

    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name='estaciones_asignadas'
    )
    estacion = models.ForeignKey(
        Estacion, on_delete=models.PROTECT, related_name='usuarios_asignados'
    )
    rol_estacion = models.ForeignKey(
        RolEstacion, on_delete=models.PROTECT, related_name='asignaciones'
    )
    estado = models.CharField(
        max_length=20, choices=ESTADOS, default='activo', db_default='activo'
    )
    fecha_asignacion = models.DateTimeField(db_default=Now(), editable=False)

    class Meta:
        db_table = 'usuarios_estaciones'
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'estacion'], name='uq_usuario_estacion'
            ),
            models.CheckConstraint(
                condition=Q(estado__in=['activo', 'inactivo', 'suspendido']),
                name='ck_usuarios_estaciones_estado',
            ),
            models.UniqueConstraint(
                fields=['estacion'],
                condition=Q(rol_estacion=1),
                name='uq_ue_un_propietario',
            ),
        ]
        indexes = [
            models.Index(fields=['estacion'], name='idx_ue_estacion'),
            models.Index(fields=['rol_estacion'], name='idx_ue_rol'),
        ]
        verbose_name = 'Usuario-Estación'
        verbose_name_plural = 'Usuarios-Estaciones'

    def __str__(self):
        return f'{self.usuario} → {self.estacion} ({self.rol_estacion})'


class Lectura(models.Model):
    pk = models.CompositePrimaryKey('estacion', 'fecha_hora')
    estacion = models.ForeignKey(
        Estacion, on_delete=models.PROTECT, related_name='lecturas'
    )
    fecha_hora = models.DateTimeField()
    out_temp = models.FloatField(blank=True, null=True, db_column='temp_ext')
    hi_temp = models.FloatField(blank=True, null=True, db_column='temp_max')
    low_temp = models.FloatField(blank=True, null=True, db_column='temp_min')
    out_hum = models.FloatField(blank=True, null=True, db_column='hum_ext')
    wind_speed = models.FloatField(blank=True, null=True, db_column='vel_viento')
    wind_dir = models.SmallIntegerField(blank=True, null=True, db_column='dir_viento')
    wind_run = models.FloatField(blank=True, null=True, db_column='recorrido_viento')
    hi_speed = models.FloatField(blank=True, null=True, db_column='vel_max_viento')
    hi_dir = models.SmallIntegerField(blank=True, null=True, db_column='dir_vel_max')
    rain = models.FloatField(blank=True, null=True, db_column='lluvia')
    rain_rate = models.FloatField(blank=True, null=True, db_column='tasa_lluvia')
    solar_rad = models.FloatField(blank=True, null=True, db_column='rad_solar')
    solar_energy = models.FloatField(blank=True, null=True, db_column='energia_solar')
    hi_solar_rad = models.FloatField(blank=True, null=True, db_column='rad_solar_max')
    uv_index = models.FloatField(blank=True, null=True, db_column='indice_uv')
    uv_dose = models.FloatField(blank=True, null=True, db_column='dosis_uv')
    hi_uv = models.FloatField(blank=True, null=True, db_column='uv_max')
    bar = models.FloatField(blank=True, null=True, db_column='presion_bar')
    dew_pt = models.FloatField(blank=True, null=True, db_column='punto_rocio')
    wind_chill = models.FloatField(blank=True, null=True, db_column='sensacion_termica')
    heat_index = models.FloatField(blank=True, null=True, db_column='indice_calor')
    thw_index = models.FloatField(blank=True, null=True, db_column='indice_thw')
    thsw_index = models.FloatField(blank=True, null=True, db_column='indice_thsw')
    et = models.FloatField(blank=True, null=True, db_column='evapotranspiracion')
    in_temp = models.FloatField(blank=True, null=True, db_column='temp_int')
    in_hum = models.FloatField(blank=True, null=True, db_column='hum_int')
    iss_recept = models.FloatField(blank=True, null=True, db_column='recepcion_iss')
    arc_int = models.SmallIntegerField(blank=True, null=True, db_column='int_archivo')

    class Meta:
        db_table = 'lecturas'
        ordering = ['-fecha_hora']
        verbose_name = 'Lectura'
        verbose_name_plural = 'Lecturas'

    def __str__(self):
        return f'{self.estacion} - {self.fecha_hora}'


class TelemetriaDispositivo(models.Model):
    pk = models.CompositePrimaryKey('subestacion', 'fecha_hora')
    subestacion = models.ForeignKey(
        Subestacion, on_delete=models.PROTECT, related_name='telemetrias'
    )
    fecha_hora = models.DateTimeField()
    bateria_porcentaje = models.FloatField(blank=True, null=True)
    bateria_voltaje = models.FloatField(blank=True, null=True)
    panel_solar_voltaje = models.FloatField(blank=True, null=True)
    senal_rssi = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'telemetria_dispositivo'
        ordering = ['-fecha_hora']
        verbose_name = 'Telemetría de Dispositivo'
        verbose_name_plural = 'Telemetrías de Dispositivos'

    @property
    def estacion(self):
        return self.subestacion.estacion

    def __str__(self):
        return f'{self.subestacion} - {self.fecha_hora}'


class ApiKey(models.Model):
    id = models.AutoField(primary_key=True)
    subestacion = models.ForeignKey(
        Subestacion, on_delete=models.PROTECT, related_name='api_keys'
    )
    creado_por_usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name='api_keys_creadas'
    )
    llave_hash = models.CharField(max_length=255, db_column='api_key')
    prefijo_visible = models.CharField(max_length=12)
    activa = models.BooleanField(default=True, db_default=True)
    fecha_creacion = models.DateTimeField(db_default=Now(), editable=False)
    fecha_ultimo_uso = models.DateTimeField(blank=True, null=True)
    fecha_expiracion = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'api_keys'
        indexes = [
            models.Index(fields=['subestacion'], name='idx_api_keys_subestacion'),
            models.Index(fields=['creado_por_usuario'], name='idx_api_keys_usuario'),
            models.Index(fields=['prefijo_visible'], name='idx_api_keys_prefijo'),
        ]
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def __str__(self):
        return f'{self.prefijo_visible}... → {self.subestacion}'
