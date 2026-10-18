from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repartidor', '0004_repartidor'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='fecha_hora_asignacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_hora_aceptacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
