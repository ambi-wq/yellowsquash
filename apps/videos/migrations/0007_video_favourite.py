# Generated by Django 2.2.6 on 2022-11-29 13:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('videos', '0006_auto_20221011_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='favourite',
            field=models.ManyToManyField(blank=True, null=True, related_name='favourite_video', to=settings.AUTH_USER_MODEL),
        ),
    ]