# Generated by Django 2.2.6 on 2022-11-08 17:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('queries', '0004_auto_20221028_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='querycomment',
            name='liked_user',
            field=models.ManyToManyField(blank=True, null=True, related_name='liked_user_comment', to=settings.AUTH_USER_MODEL),
        ),
    ]