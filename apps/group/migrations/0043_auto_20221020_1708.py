# Generated by Django 2.2.6 on 2022-10-20 17:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0042_auto_20221020_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 20, 17, 8, 53, 42148)),
        ),
    ]