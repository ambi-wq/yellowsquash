# Generated by Django 2.2.6 on 2022-12-31 12:28

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('program', '0028_auto_20221230_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='like',
            field=models.ManyToManyField(blank=True, null=True, related_name='review_like', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='review',
            name='status',
            field=models.CharField(choices=[('approved', 'APPROVED'), ('under_review', 'UNDER_REVIEW')], default='under_review', max_length=100),
        ),
    ]
