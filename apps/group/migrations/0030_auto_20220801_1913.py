# Generated by Django 2.2.6 on 2022-08-01 19:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0029_auto_20220801_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 1, 19, 12, 59, 182919)),
        ),
    ]