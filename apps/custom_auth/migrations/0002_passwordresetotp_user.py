# Generated by Django 2.2.6 on 2022-04-05 20:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('custom_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='passwordresetotp',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_who_wants_to_reset_password', to=settings.AUTH_USER_MODEL),
        ),
    ]
