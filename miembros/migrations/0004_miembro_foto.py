# Generated by Django 5.1.1 on 2024-10-02 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miembros', '0003_alter_miembro_num_control'),
    ]

    operations = [
        migrations.AddField(
            model_name='miembro',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
