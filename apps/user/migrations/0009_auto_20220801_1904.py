# Generated by Django 2.2.6 on 2022-08-01 19:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20220730_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usereducationdetail',
            name='completion_year',
            field=models.CharField(choices=[(1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022)], default=2022, max_length=10, verbose_name='completion year'),
        ),
        migrations.AlterField(
            model_name='usereducationdetail',
            name='course_name',
            field=models.CharField(choices=[('High School', 'High School'), ('Pre University (XII)', 'Pre University (XII)'), ('Diploma', 'Diploma'), ("3 Year-Bachelor's Degree", "3 Year-Bachelor's Degree"), ("4 Year-Bachelor's Degree", "4 Year-Bachelor's Degree"), ("5 Year-Bachelor's Degree", "5 Year-Bachelor's Degree"), ("Master's Degree", "Master's Degree"), ('Doctoral Degree', 'Doctoral Degree'), ('MBBS', 'MBBS'), ('Certification', 'Certification')], max_length=100, verbose_name='user course name'),
        ),
        migrations.CreateModel(
            name='ExpertTeamMember',
            fields=[
                ('team_member_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('role', models.CharField(blank=True, max_length=50, null=True)),
                ('phone', models.CharField(blank=True, help_text='Phone number of user', max_length=15, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]