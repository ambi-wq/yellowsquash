# Generated by Django 2.2.6 on 2022-04-19 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0022_programbatch_additional_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='speciality',
            field=models.CharField(max_length=200, null=True),
        ),
    ]