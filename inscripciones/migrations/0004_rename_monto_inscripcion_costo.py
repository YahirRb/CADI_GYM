# Generated by Django 5.1.1 on 2024-10-02 03:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inscripciones', '0003_remove_inscripcion_gimnasia_artistica_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inscripcion',
            old_name='monto',
            new_name='costo',
        ),
    ]
