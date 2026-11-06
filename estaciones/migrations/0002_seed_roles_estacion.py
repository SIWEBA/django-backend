from django.db import migrations


def seed_roles(apps, schema_editor):
    RolEstacion = apps.get_model('estaciones', 'RolEstacion')
    manager = RolEstacion.objects.using(schema_editor.connection.alias)
    roles = (
        (1, 'propietario'),
        (2, 'administrador'),
        (3, 'visor'),
    )
    for role_id, name in roles:
        manager.update_or_create(id=role_id, defaults={'nombre': name})

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT setval(pg_get_serial_sequence('roles_estacion', 'id'), "
            "GREATEST((SELECT COALESCE(MAX(id), 1) FROM roles_estacion), 1), true)"
        )


def unseed_roles(apps, schema_editor):
    RolEstacion = apps.get_model('estaciones', 'RolEstacion')
    RolEstacion.objects.using(schema_editor.connection.alias).filter(
        id__in=[1, 2, 3],
        nombre__in=['propietario', 'administrador', 'visor'],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('estaciones', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]
