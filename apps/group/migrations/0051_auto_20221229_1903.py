# Generated by Django 2.2.6 on 2022-12-29 19:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0050_auto_20221228_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 29, 19, 3, 35, 864525)),
        ),
    ]
