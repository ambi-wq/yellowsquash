# Generated by Django 2.2.6 on 2022-07-30 11:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0023_auto_20220729_1908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 30, 11, 0, 43, 161553)),
        ),
    ]