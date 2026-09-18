from django.db import models
from django.contrib.auth.hashers import make_password

class RolSistema(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'Roles_Sistema'
        verbose_name = 'Rol de Sistema'
        verbose_name_plural = 'Roles de Sistema'

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    rol_sistema = models.ForeignKey(
        RolSistema, on_delete=models.PROTECT, related_name='usuarios'
    )
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} ({self.correo})"

    def save(self, *args, **kwargs):
        if self.contrasena and not self.contrasena.startswith('pbkdf2_sha256$'):
            self.contrasena = make_password(self.contrasena)
            
        super().save(*args, **kwargs)