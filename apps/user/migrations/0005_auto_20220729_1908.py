# Generated by Django 2.2.6 on 2022-07-29 19:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_languages_location_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='timezone',
            field=models.ManyToManyField(blank=True, null=True, related_name='timezone', to='user.TimeZone'),
        ),
        migrations.RemoveField(
            model_name='user',
            name='language',
        ),
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.ManyToManyField(blank=True, null=True, related_name='languages', to='user.Languages'),
        ),
        migrations.AlterField(
            model_name='user',
            name='location',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location', to='user.Location'),
        ),
    ]