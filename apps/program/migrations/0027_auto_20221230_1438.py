# Generated by Django 2.2.6 on 2022-12-30 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0026_auto_20221230_1342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reviewfiles',
            name='program',
        ),
        migrations.RemoveField(
            model_name='reviewfiles',
            name='user',
        ),
        migrations.AddField(
            model_name='review',
            name='files',
            field=models.ManyToManyField(blank=True, null=True, related_name='review_files', to='program.ReviewFiles'),
        ),
    ]