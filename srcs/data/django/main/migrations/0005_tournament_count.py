# Generated by Django 4.2.13 on 2024-06-14 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_tournament_timestamp1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]
