# Generated by Django 2.2.6 on 2022-11-29 13:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0047_auto_20221128_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 29, 13, 17, 19, 208614)),
        ),
    ]
