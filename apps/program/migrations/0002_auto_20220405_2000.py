# Generated by Django 2.2.6 on 2022-04-05 20:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user', '0001_initial'),
        ('program', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpaymentdetail',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='review',
            name='program',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='program.Program'),
        ),
        migrations.AddField(
            model_name='review',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='programsessionresource',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='programs', to='program.Program'),
        ),
        migrations.AddField(
            model_name='programsessionresource',
            name='programBatch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='programs_sessions_batch', to='program.ProgramBatch'),
        ),
        migrations.AddField(
            model_name='programsessionresource',
            name='programSession',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='programs_sessions_resources', to='program.ProgramSession'),
        ),
        migrations.AddField(
            model_name='programsession',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='programs_sessions', to='program.Program'),
        ),
        migrations.AddField(
            model_name='programcategory',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_category', to='user.Category'),
        ),
        migrations.AddField(
            model_name='programcategory',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='programs_for_category', to='program.Program'),
        ),
        migrations.AddField(
            model_name='programbatchuser',
            name='programBatch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='program.ProgramBatch'),
        ),
        migrations.AddField(
            model_name='programbatchuser',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='programbatchsessionresource',
            name='programBatchSession',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='programs_batch_session_resources', to='program.ProgramBatchSession'),
        ),
        migrations.AddField(
            model_name='programbatchsession',
            name='programBatch',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='programs_batch_sessions', to='program.ProgramBatch'),
        ),
        migrations.AddField(
            model_name='programbatch',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='programs_batches', to='program.Program'),
        ),
        migrations.AddField(
            model_name='program',
            name='auther',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auther_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='program',
            name='category',
            field=models.ManyToManyField(related_name='program_categories', through='program.ProgramCategory', to='user.Category'),
        ),
        migrations.AddField(
            model_name='program',
            name='expert',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expert_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='overview',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='program.Program'),
        ),
        migrations.AddField(
            model_name='frequentlyaskedquestion',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='program.Program'),
        ),
        migrations.AddField(
            model_name='favoriteprogram',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favorite_program_id', to='program.Program'),
        ),
        migrations.AddField(
            model_name='favoriteprogram',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_who_liked_program_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='discountstatistics',
            name='discount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='program.Discount'),
        ),
        migrations.AddField(
            model_name='discountstatistics',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='program.Program'),
        ),
        migrations.AddField(
            model_name='discountstatistics',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='program_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='discount',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.Category'),
        ),
        migrations.AddField(
            model_name='discount',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='program.Program'),
        ),
        migrations.AlterUniqueTogether(
            name='programsession',
            unique_together={('program', 'sequence_num')},
        ),
        migrations.AlterUniqueTogether(
            name='programcategory',
            unique_together={('program', 'category')},
        ),
        migrations.AlterUniqueTogether(
            name='programbatchuser',
            unique_together={('programBatch', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='programbatchsession',
            unique_together={('programBatch', 'sequence_num')},
        ),
        migrations.AlterUniqueTogether(
            name='favoriteprogram',
            unique_together={('user', 'program')},
        ),
    ]