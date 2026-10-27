from django.db import migrations, models


def copiar_staff_a_operario(apps, schema_editor):
    User = apps.get_model('users', 'User')
    User.objects.using(schema_editor.connection.alias).filter(is_staff=True).update(
        is_operario=True,
    )


def revertir_operarios_migrados(apps, schema_editor):
    User = apps.get_model('users', 'User')
    User.objects.using(schema_editor.connection.alias).update(is_operario=False)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_remove_user_vehiculo'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_operario',
            field=models.BooleanField(
                default=False,
                help_text='Designa si el usuario puede acceder al módulo de operario.',
                verbose_name='operario',
            ),
        ),
        migrations.RunPython(copiar_staff_a_operario, revertir_operarios_migrados),
    ]
