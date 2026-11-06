from django.contrib import admin
from .models import ApiKey, Estacion, RolEstacion, Subestacion, UsuarioEstacion

admin.site.register(RolEstacion)
admin.site.register(Estacion)
admin.site.register(Subestacion)
admin.site.register(UsuarioEstacion)
admin.site.register(ApiKey)