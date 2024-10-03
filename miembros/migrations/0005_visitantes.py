# Generated by Django 5.1.1 on 2024-10-02 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miembros', '0004_miembro_foto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visitantes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellidos', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254)),
                ('celular', models.CharField(blank=True, max_length=15, null=True)),
            ],
        ),
    ]
