# Generated by Django 5.1.3 on 2024-11-26 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_userprofile_location_userprofile_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=30),
        ),
    ]
