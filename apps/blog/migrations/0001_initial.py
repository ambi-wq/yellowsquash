# Generated by Django 2.2.6 on 2022-04-05 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, null=True, unique=True)),
                ('summary', models.TextField(null=True)),
                ('feature_image_url', models.CharField(max_length=500, null=True, verbose_name='Actual Feature Image Url')),
                ('banner_image_url', models.CharField(max_length=500, null=True, verbose_name='Actual Banner Image Url')),
                ('article_body', models.TextField()),
                ('slug', models.CharField(max_length=100, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('draft', 'DRAFT'), ('requested', 'REQUESTED'), ('approved', 'APPROVED'), ('rejected', 'REJECTED'), ('published', 'PUBLISHED')], default='draft', max_length=20)),
                ('rejection_message', models.CharField(blank=True, max_length=200, null=True, verbose_name='reason for article rejection')),
            ],
        ),
        migrations.CreateModel(
            name='BlogComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BlogLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BlogShare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('where', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BlogStates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_view', models.BooleanField(default=False, verbose_name='blog view or not')),
                ('viewed_time', models.DateTimeField(auto_now=True)),
                ('is_like', models.BooleanField(default=False, verbose_name='blog liked or not')),
                ('liked_time', models.DateTimeField(auto_now=True, verbose_name='liked time')),
                ('is_shared', models.BooleanField(default=False, verbose_name='shared or not')),
                ('shared_time', models.DateTimeField(auto_now=True, verbose_name='sahred time')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'ACTIVE'), ('inactive', 'INACTIVE')], default='active', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='BlogView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Blog')),
            ],
        ),
    ]