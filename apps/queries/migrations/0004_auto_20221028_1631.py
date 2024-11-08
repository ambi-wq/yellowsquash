# Generated by Django 2.2.6 on 2022-10-28 16:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0003_auto_20221026_1210'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='query',
            name='attachment',
        ),
        migrations.CreateModel(
            name='QueryAttachments',
            fields=[
                ('attachment_id', models.AutoField(primary_key=True, serialize=False)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='queries')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('query', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='queries.Query')),
            ],
        ),
    ]
