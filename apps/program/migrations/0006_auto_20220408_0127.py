# Generated by Django 2.2.6 on 2022-04-08 01:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('program', '0005_auto_20220408_0001'),
    ]

    operations = [
        migrations.AddField(
            model_name='actiontaskuserprogram',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='action_program_id', to='program.Program'),
        ),
        migrations.AlterUniqueTogether(
            name='actiontaskuserprogram',
            unique_together={('user', 'program', 'task')},
        ),
    ]
