from django.db import models
from django.contrib.auth.hashers import identify_hasher
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.functions import Lower, Now

class RolSistema(models.Model):
    id = models.SmallAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'roles_sistema'
        verbose_name = 'Rol de Sistema'
        verbose_name_plural = 'Roles de Sistema'

    def __str__(self):
        return self.nombre

class Usuario(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    rol_sistema = models.ForeignKey(RolSistema, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=254)
    activo = models.BooleanField(default=True, db_default=True)
    fecha_registro = models.DateTimeField(db_default=Now(), editable=False)
    password = models.CharField(max_length=255, db_column='contrasena')
    last_login = None
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']
    objects = BaseUserManager()

    class Meta:
        db_table = 'usuarios'
        constraints = [
            models.UniqueConstraint(
                Lower('correo'), name='uq_usuarios_correo_ci'
            ),
        ]
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    @property
    def is_active(self):
        return self.activo

    def __str__(self):
        return f"{self.nombre} ({self.correo})"

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('!'):
            try:
                identify_hasher(self.password)
            except ValueError:
                self.set_password(self.password)
        super().save(*args, **kwargs)