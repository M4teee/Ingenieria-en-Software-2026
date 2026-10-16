# Generated for the Repartidor profile after the Pedido initial schema.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repartidor', '0003_alter_historialestado_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Repartidor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pin', models.CharField(max_length=4, unique=True)),
                ('disponible', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='repartidor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Repartidor',
                'verbose_name_plural': 'Repartidores',
            },
        ),
    ]
