# Generated by Django 3.1.1 on 2023-10-26 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0002_auto_20231026_2130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voter',
            name='otp',
        ),
        migrations.RemoveField(
            model_name='voter',
            name='otp_sent',
        ),
        migrations.RemoveField(
            model_name='voter',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='voter',
            name='verified',
        ),
        migrations.AddField(
            model_name='candidate',
            name='admission_number',
            field=models.CharField(default='testing -admission', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='candidate',
            name='year_of_study',
            field=models.CharField(default=3, max_length=100),
            preserve_default=False,
        ),
    ]
