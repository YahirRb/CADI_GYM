# Generated by Django 5.1.1 on 2024-10-03 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_customuser_num_control'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenUtilizado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=512, unique=True)),
                ('fecha_utilizacion', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
