from django.db import migrations


def seed_roles(apps, schema_editor):
    RolSistema = apps.get_model('usuarios', 'RolSistema')
    manager = RolSistema.objects.using(schema_editor.connection.alias)
    for role_id, name in ((1, 'admin'), (2, 'usuario')):
        manager.update_or_create(id=role_id, defaults={'nombre': name})

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT setval(pg_get_serial_sequence('roles_sistema', 'id'), "
            "GREATEST((SELECT COALESCE(MAX(id), 1) FROM roles_sistema), 1), true)"
        )


def unseed_roles(apps, schema_editor):
    RolSistema = apps.get_model('usuarios', 'RolSistema')
    RolSistema.objects.using(schema_editor.connection.alias).filter(
        id__in=[1, 2], nombre__in=['admin', 'usuario']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]
