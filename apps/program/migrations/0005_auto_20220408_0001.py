# Generated by Django 2.2.6 on 2022-04-08 00:01

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('program', '0004_auto_20220407_2359'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='actiontaskuserprogram',
            unique_together={('user', 'task')},
        ),
        migrations.RemoveField(
            model_name='actiontaskuserprogram',
            name='program',
        ),
    ]