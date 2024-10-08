# Generated by Django 5.1.1 on 2024-10-01 19:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inscripciones', '0001_initial'),
        ('miembros', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pagos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(default='pendiente', max_length=20)),
                ('pago_realizado', models.BooleanField(default=False)),
                ('proximo_pago', models.DateField()),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('inscripcion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscripciones.inscripcion')),
                ('miembro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='miembros.miembro')),
            ],
        ),
    ]
