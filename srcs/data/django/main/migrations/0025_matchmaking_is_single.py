# Generated by Django 4.2.14 on 2024-08-10 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_matchmaking_ai'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchmaking',
            name='is_single',
            field=models.BooleanField(default=False),
        ),
    ]
