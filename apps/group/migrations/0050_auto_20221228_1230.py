# Generated by Django 2.2.6 on 2022-12-28 12:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0049_auto_20221226_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 28, 12, 30, 50, 775335)),
        ),
    ]
