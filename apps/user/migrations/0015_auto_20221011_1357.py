# Generated by Django 2.2.6 on 2022-10-11 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_auto_20220915_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usereducationdetail',
            name='completion_year',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='completion year'),
        ),
        migrations.AlterField(
            model_name='usereducationdetail',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
