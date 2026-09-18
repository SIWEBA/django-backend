from django.db import models
from usuarios.models import Usuario


class RolEstacion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'Roles_Estacion'
        verbose_name = 'Rol de Estación'
        verbose_name_plural = 'Roles de Estación'

    def __str__(self):
        return self.nombre


class Estacion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=50)
    ultima_conexion = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Estaciones'
        verbose_name = 'Estación'
        verbose_name_plural = 'Estaciones'

    def __str__(self):
        return self.nombre


class UsuarioEstacion(models.Model):
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
    estado = models.CharField(max_length=20, default='activo')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Usuarios_Estaciones'
        verbose_name = 'Usuario-Estación'
        verbose_name_plural = 'Usuarios-Estaciones'

    def __str__(self):
        return f"{self.usuario} → {self.estacion} ({self.rol_estacion})"


class Lectura(models.Model):
    id = models.BigAutoField(primary_key=True)
    estacion = models.ForeignKey(
        Estacion, on_delete=models.PROTECT, related_name='lecturas'
    )
    fecha_hora = models.DateTimeField()
    out_temp = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hi_temp = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    low_temp = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    out_hum = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    wind_dir = models.SmallIntegerField(blank=True, null=True)
    wind_run = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hi_speed = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hi_dir = models.SmallIntegerField(blank=True, null=True)
    rain = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    rain_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    solar_rad = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    solar_energy = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    hi_solar_rad = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    uv_index = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    uv_dose = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hi_uv = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    bar = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    dew_pt = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    wind_chill = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    heat_index = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    thw_index = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    thsw_index = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    et = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    in_temp = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    in_hum = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    iss_recept = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    arc_int = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'Lecturas'
        constraints = [
            models.UniqueConstraint(
                fields=['estacion', 'fecha_hora'], name='idx_estacion_fecha'
            )
        ]
        indexes = [
            models.Index(fields=['estacion', 'fecha_hora']),
        ]
        ordering = ['-fecha_hora']
        verbose_name = 'Lectura'
        verbose_name_plural = 'Lecturas'

    def __str__(self):
        return f"{self.estacion} - {self.fecha_hora}"


class TelemetriaDispositivo(models.Model):
    id = models.BigAutoField(primary_key=True)
    estacion = models.ForeignKey(
        Estacion, on_delete=models.PROTECT, related_name='telemetrias'
    )
    fecha_hora = models.DateTimeField()
    bateria_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    bateria_voltaje = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    panel_solar_voltaje = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    senal_rssi = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'Telemetria_Dispositivo'
        ordering = ['-fecha_hora']
        verbose_name = 'Telemetría de Dispositivo'
        verbose_name_plural = 'Telemetrías de Dispositivos'

    def __str__(self):
        return f"{self.estacion} - {self.fecha_hora}"


class ApiKey(models.Model):
    id = models.AutoField(primary_key=True)
    estacion = models.OneToOneField(
        Estacion, on_delete=models.PROTECT, related_name='api_key'
    )
    creado_por_usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name='api_keys_creadas'
    )
    llave_hash = models.CharField(max_length=255)
    prefijo_visible = models.CharField(max_length=12)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultimo_uso = models.DateTimeField(blank=True, null=True)
    fecha_expiracion = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'Api_Keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def __str__(self):
        return f"{self.prefijo_visible}... → {self.estacion}"