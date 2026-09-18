from django.contrib import admin
from .models import Estacion, RolEstacion, UsuarioEstacion, Lectura, TelemetriaDispositivo, ApiKey

admin.site.register(RolEstacion)
admin.site.register(Estacion)
admin.site.register(UsuarioEstacion)
admin.site.register(TelemetriaDispositivo)
admin.site.register(ApiKey)

@admin.register(Lectura)
class LecturaAdmin(admin.ModelAdmin):
    list_display = ('estacion', 'fecha_hora', 'out_temp', 'out_hum', 'rain')
    list_filter = ('estacion',)
    date_hierarchy = 'fecha_hora'