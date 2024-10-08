# Generated by Django 4.2.15 on 2024-08-13 19:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_matchmaking_point1_matchmaking_point2_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Doubles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_users', models.IntegerField(default=-1)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('ball_speed', models.IntegerField(default=2)),
                ('paddle_size', models.IntegerField(default=2)),
                ('match_point', models.IntegerField(default=10)),
                ('is_3d', models.BooleanField(default=False)),
                ('is_complete', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='matchmaking',
            name='user3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matchmaking_user3', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='matchmaking',
            name='user4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matchmaking_user4', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='DoublesUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('doubles', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.doubles')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='matchmaking',
            name='doubles',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.doubles'),
        ),
    ]
