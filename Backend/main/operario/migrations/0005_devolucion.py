from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operario', '0004_alter_comercio_nombre'),
        ('repartidor', '0012_repartidor_disponible_desde'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Devolucion',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                (
                    'pedido',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='devolucion_confirmada',
                        to='repartidor.pedido',
                    ),
                ),
                (
                    'usuario',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='devoluciones_confirmadas',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'Devolución confirmada',
                'verbose_name_plural': 'Devoluciones confirmadas',
                'ordering': ['fecha', 'pk'],
            },
        ),
    ]
