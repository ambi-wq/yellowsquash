# Generated by Django 2.2.6 on 2022-06-04 14:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0018_auto_20220524_2227'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 4, 14, 34, 49, 62738)),
        ),
    ]
