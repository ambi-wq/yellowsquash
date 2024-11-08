# Generated by Django 2.2.6 on 2022-05-01 11:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0008_auto_20220430_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='cover_image',
            field=models.CharField(max_length=4000),
        ),
        migrations.AlterField(
            model_name='grouppost',
            name='status_changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='group_post_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='GroupMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(upload_to='')),
                ('post', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='group_media_post_group', to='group.GroupPost')),
            ],
        ),
    ]
