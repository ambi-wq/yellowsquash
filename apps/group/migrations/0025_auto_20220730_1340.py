# Generated by Django 2.2.6 on 2022-07-30 13:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0024_auto_20220730_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 30, 13, 40, 47, 938835)),
        ),
    ]
