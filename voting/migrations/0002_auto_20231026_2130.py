# Generated by Django 3.1.1 on 2023-10-26 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='voter',
            name='admission_number',
            field=models.CharField(default='hsp201-0035/2019', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='voter',
            name='year_of_study',
            field=models.CharField(default=3, max_length=100),
            preserve_default=False,
        ),
    ]
