# Generated by Django 2.2.6 on 2022-07-30 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20220730_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location', to='user.Location'),
        ),
        migrations.AlterField(
            model_name='user',
            name='timezone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='timezone', to='user.TimeZone'),
        ),
    ]