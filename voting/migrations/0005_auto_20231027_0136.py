# Generated by Django 3.1.1 on 2023-10-26 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_auto_20231026_2153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='admission_number',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='voter',
            name='admission_number',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
