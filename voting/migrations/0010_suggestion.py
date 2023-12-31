# Generated by Django 3.1.1 on 2023-10-29 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0009_electionmilboxreply_reply'),
    ]

    operations = [
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('implemented', models.BooleanField(default=False)),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestion_voter', to='voting.voter')),
            ],
        ),
    ]
