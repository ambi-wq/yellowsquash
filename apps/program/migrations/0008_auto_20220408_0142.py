# Generated by Django 2.2.6 on 2022-04-08 01:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0007_auto_20220408_0136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actiontaskuserprogram',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_action', to='program.ProgramTask'),
        ),
    ]