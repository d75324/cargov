# Generated by Django 4.2.21 on 2025-07-16 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cargo', '0010_trucktrip_initial_mileage_alter_truck_mileage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='truck',
            name='mileage',
            field=models.PositiveIntegerField(verbose_name='Kilometraje'),
        ),
    ]
