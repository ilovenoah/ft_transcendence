from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .validators import validate_file_size
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    avatar = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        default='avatars/default.png'  # デフォルト画像のパスを指定
    )
    is_online = models.BooleanField(default=False) #オンラインステータス
    last_active = models.DateTimeField(default=timezone.now)  # 最後にアクティブだった時間
    display_name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)

    def send_friend_request(self, to_user):
        if self == to_user:
            raise ValidationError("You cannot send a friend request to yourself.")
        if FriendRequest.objects.filter(Q(from_user=self, to_user=to_user) | Q(from_user=to_user, to_user=self)).exists():
            raise ValidationError("You cannot send a friend request.")
        friend_request = FriendRequest(from_user=self, to_user=to_user)
        friend_request.save()
        return friend_request

class Image(models.Model):
    image = models.ImageField(upload_to='avatars/', validators=[validate_file_size])

class FriendRequest(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='friend_requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=[('P', 'Pending'), ('A', 'Accepted')], default='P')

    def accept_request(self):
        self.status = 'A'
        self.save()

class Tournament(models.Model):
    size = models.IntegerField(default=0)
    num_users = models.IntegerField(default=-1)
    timestamp = models.DateTimeField(auto_now=True)
    ball_speed = models.IntegerField(default=2)
    paddle_size = models.IntegerField(default=2)
    match_point = models.IntegerField(default=10)
    is_3d = models.BooleanField(default=False)

class TournamentUser(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)

class Doubles(models.Model):
    num_users = models.IntegerField(default=-1)
    timestamp = models.DateTimeField(auto_now=True)
    ball_speed = models.IntegerField(default=2)
    paddle_size = models.IntegerField(default=2)
    match_point = models.IntegerField(default=10)
    is_3d = models.BooleanField(default=False)

class DoublesUser(models.Model):
    doubles = models.ForeignKey(Doubles, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)

class Matchmaking(models.Model):
    user1 = models.ForeignKey(CustomUser, related_name='matchmaking_user1', on_delete=models.CASCADE, null=True, blank=True)
    user2 = models.ForeignKey(CustomUser, related_name='matchmaking_user2', on_delete=models.CASCADE, null=True, blank=True)
    user3 = models.ForeignKey(CustomUser, related_name='matchmaking_user3', on_delete=models.CASCADE, null=True, blank=True)
    user4 = models.ForeignKey(CustomUser, related_name='matchmaking_user4', on_delete=models.CASCADE, null=True, blank=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True, blank=True)  # トーナメントID
    doubles = models.ForeignKey(Doubles, on_delete=models.CASCADE, null=True, blank=True) #ダブルス
    timestamp = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    level = models.IntegerField(default=-1)
    ball_speed = models.IntegerField(default=2)
    paddle_size = models.IntegerField(default=2)
    match_point = models.IntegerField(default=10)
    is_3d = models.BooleanField(default=False)
    ai = models.IntegerField(default=2)
    is_single = models.BooleanField(default=False)
    point1 = models.IntegerField(default=0)
    point2 = models.IntegerField(default=0)
    winner = models.ForeignKey(CustomUser, related_name='winner', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f'Matchmaking ID {self.id} (Tournament: {self.tournament_id})'


