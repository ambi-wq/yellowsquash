# Generated by Django 2.2.6 on 2022-04-05 20:00

import datetime
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProgramList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('rating', models.DecimalField(blank=True, decimal_places=1, max_digits=2)),
                ('intro_video_url', models.CharField(blank=True, max_length=200, verbose_name='program into video url')),
                ('image_url', models.CharField(blank=True, max_length=100)),
                ('html_description', models.TextField(blank=True)),
                ('offer_price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=20, null=True, verbose_name='program cost')),
                ('session_count', models.IntegerField(null=True, verbose_name='number of sessions')),
                ('duration_in_weeks', models.IntegerField(null=True, verbose_name='duration in weeks')),
                ('start_date', models.DateField(default=django.utils.timezone.now, verbose_name='start date')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10)),
                ('chat_group_key', models.CharField(blank=True, max_length=50, null=True, verbose_name="auto genrated group chat key(Don't Update Manually After Creation)")),
                ('is_favorite', models.BooleanField(default=False, verbose_name='is users favorite program')),
                ('is_subscribed', models.CharField(choices=[('active', 'ACTIVE'), ('inactive', 'INACTIVE'), ('payment_under_review', 'PAYMENT_UNDER_REVIEW')], default='inactive', max_length=100)),
                ('experties', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=20, null=True)),
                ('total_redemption_limit', models.IntegerField(blank=True, null=True)),
                ('is_unlimited_redemption', models.BooleanField(default=False)),
                ('additional_info', models.TextField()),
                ('valid_from_timestamp', models.DateTimeField()),
                ('valid_till_stamp', models.DateTimeField()),
                ('discount', models.CharField(blank=True, max_length=50, null=True)),
                ('discount_type', models.CharField(choices=[('Fixed', 'Fixed'), ('Percentage', 'Percentage')], max_length=20)),
                ('if_percentage_max_limit_per_tx', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Deactive', 'Deactive')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='DiscountStatistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_applied_timestamp', models.DateTimeField()),
                ('amount', models.FloatField()),
                ('discount_amount', models.FloatField()),
                ('amount_after_discount', models.FloatField()),
                ('discount_code', models.CharField(blank=True, max_length=20, null=True)),
                ('status', models.CharField(choices=[('Applied', 'Applied'), ('Rejected', 'Rejected')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
            ],
        ),
        migrations.CreateModel(
            name='FrequentlyAskedQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(verbose_name='question')),
                ('answer', models.TextField(verbose_name='answer')),
            ],
        ),
        migrations.CreateModel(
            name='Overview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, verbose_name='overview title')),
                ('header_image_link', models.CharField(blank=True, max_length=100, verbose_name='header image link')),
                ('description', models.TextField(blank=True, verbose_name='overview description')),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, null=True)),
                ('slug', models.CharField(blank=True, max_length=300, null=True)),
                ('rating', models.DecimalField(decimal_places=1, max_digits=2, null=True, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(0)])),
                ('intro_video_url', models.CharField(max_length=200, null=True, verbose_name='program intro video url')),
                ('image_url', models.CharField(blank=True, max_length=150, null=True)),
                ('thumbnail_image', models.FileField(blank=True, null=True, upload_to='', verbose_name='temporary field for getting image from admin panel (Ideal Size: 500px X 345px)')),
                ('html_description', models.TextField(null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=20, null=True, verbose_name='program cost')),
                ('session_count', models.IntegerField(null=True, verbose_name='number of sessions')),
                ('duration_in_weeks', models.IntegerField(null=True, verbose_name='duration in weeks')),
                ('start_date', models.DateField(default=django.utils.timezone.now, verbose_name='start date')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10)),
                ('chat_group_key', models.CharField(blank=True, max_length=50, null=True, verbose_name="auto genrated group chat key(Don't Update Manually After Creation)")),
            ],
        ),
        migrations.CreateModel(
            name='ProgramBatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='batch description')),
                ('start_time', models.TimeField(default='07:00', verbose_name='default batch session start timing')),
                ('end_time', models.TimeField(default='09:00', verbose_name='default batch session end timing')),
                ('batch_start_date', models.DateField(default=datetime.datetime.now, verbose_name='batch start date')),
                ('batch_end_date', models.DateField(null=True, verbose_name='batch end date')),
                ('scheduling_strategy', models.CharField(choices=[('daily', 'DAILY'), ('once', 'ONCE'), ('weekly', 'WEEKLY'), ('monthly', 'MONTHLY')], default='daily', max_length=10)),
                ('scheduled_days_of_week', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('Sunday', 'Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')], default='Monday', max_length=12, null=True), blank=True, help_text='\n        This is Only Applicable if scheduling_strategy is selected WEEKLY\n        ', null=True, size=None)),
                ('scheduled_day_of_month', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31)], default=1, help_text='\n        This is Only Applicable if <b>scheduling_strategy</b> is selected <b>MONTHLY</b> <br>\n        <b>Warning</b>: For dates like 29,30,31 if not available in any month then last day of month will be considered\n        ', null=True, verbose_name='day of month')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='session creation date')),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('batch_status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('cancelled', 'Cancelled')], default='open', max_length=10)),
                ('offer_price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('meet_link', models.CharField(blank=True, max_length=500, null=True, verbose_name='zoom meeting link')),
            ],
        ),
        migrations.CreateModel(
            name='ProgramBatchSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='session title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='session description')),
                ('sequence_num', models.IntegerField(verbose_name='order number of session')),
                ('duration', models.IntegerField(verbose_name='duration in minutes')),
                ('session_type', models.CharField(choices=[('permanent', 'Permanent'), ('temporary', 'Temporary')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='session creation date')),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('session_date', models.DateField(verbose_name='scheduled session date')),
                ('start_time', models.TimeField(verbose_name='session start time')),
                ('end_time', models.TimeField(verbose_name='session start time')),
                ('actual_start_datetime', models.DateTimeField(blank=True, null=True, verbose_name='actual start date time')),
            ],
        ),
        migrations.CreateModel(
            name='ProgramBatchSessionResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='resource title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='resource description')),
                ('doc_file', models.FileField(blank=True, null=True, upload_to='', verbose_name='temporary filed for getting file from admin panel')),
                ('doc_type', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('doc_url', models.CharField(blank=True, max_length=150, null=True, verbose_name='actual doc file url')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='session creation date')),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProgramBatchUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_date', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Subscription date')),
                ('status', models.CharField(choices=[('active', 'ACTIVE'), ('inactive', 'INACTIVE'), ('payment_under_review', 'PAYMENT_UNDER_REVIEW')], default='inactive', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ProgramCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ProgramSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='session title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='session description')),
                ('sequence_num', models.IntegerField(verbose_name='order number of session')),
                ('duration', models.IntegerField(verbose_name='duration in minutes')),
                ('session_type', models.CharField(choices=[('permanent', 'Permanent'), ('temporary', 'Temporary')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='session creation date')),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProgramSessionResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='resource title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='resource description')),
                ('doc_file', models.FileField(blank=True, null=True, upload_to='', verbose_name='temporary filed for getting file from admin panel')),
                ('doc_type', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('doc_url', models.CharField(blank=True, max_length=150, null=True, verbose_name='actual doc file url')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='session creation date')),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, verbose_name='curriculum title')),
                ('youtube_video_link', models.CharField(blank=True, max_length=150, verbose_name='review video link')),
                ('description', models.TextField(blank=True, verbose_name='review description')),
                ('rating', models.CharField(blank=True, max_length=10)),
                ('user_name', models.CharField(blank=True, max_length=100)),
                ('user_email', models.CharField(blank=True, max_length=100)),
                ('created_date', models.DateField(default=django.utils.timezone.now, null=True, verbose_name='Created date')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Videos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('youtube_video_link', models.CharField(blank=True, max_length=150, verbose_name='video link')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='program.Program')),
            ],
        ),
        migrations.CreateModel(
            name='UserPaymentDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('mobile', models.CharField(blank=True, max_length=100)),
                ('email_id', models.CharField(blank=True, max_length=100)),
                ('flat_or_house_no', models.CharField(blank=True, max_length=100)),
                ('stret_or_landmark', models.CharField(blank=True, max_length=100)),
                ('town_city_dist', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('pincode', models.CharField(blank=True, max_length=100)),
                ('gst_no', models.CharField(blank=True, max_length=100)),
                ('aadhar_no', models.CharField(blank=True, max_length=100)),
                ('pan_no', models.CharField(blank=True, max_length=100)),
                ('payment_type', models.CharField(blank=True, choices=[('bank', 'BANK'), ('upi', 'UPI'), ('credit card', 'CREDIT CARD'), ('netbanking', 'NETBANKING')], default='bank', max_length=100)),
                ('program_price', models.CharField(blank=True, max_length=10, null=True)),
                ('payment_screen_short', models.FileField(blank=True, null=True, upload_to='', verbose_name='payment screen short')),
                ('payment_screen_short_url', models.CharField(blank=True, max_length=1000)),
                ('created_at', models.DateField(auto_now=True, verbose_name='created date')),
                ('razorpay_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=100, null=True)),
                ('razorpay_signature', models.CharField(blank=True, max_length=100, null=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='program.ProgramBatch')),
            ],
        ),
    ]