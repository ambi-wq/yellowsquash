# Generated by Django 2.2.6 on 2022-12-31 12:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0054_auto_20221230_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 31, 12, 28, 22, 214160)),
        ),
    ]
