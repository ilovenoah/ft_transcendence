# Generated by Django 4.2.13 on 2024-06-20 06:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_remove_customuser_is_first_matchmaking_parent_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='matchmaking',
            name='parent_id',
        ),
        migrations.AddField(
            model_name='matchmaking',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='main.matchmaking'),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='count',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='size',
            field=models.IntegerField(default=0),
        ),
    ]
