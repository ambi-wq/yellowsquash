# Generated by Django 2.2.6 on 2022-10-26 12:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0043_auto_20221020_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 26, 12, 10, 17, 35262)),
        ),
    ]