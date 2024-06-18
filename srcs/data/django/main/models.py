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
    display_name = models.CharField(max_length=255, unique=True)
    is_first = models.BooleanField(default=True) #最初のログイン
    email = models.EmailField(unique=True)

    # def save(self, *args, **kwargs):
    #     if not self.display_name:  # display_nameが設定されていない場合
    #         self.display_name = self.username  # usernameをdisplay_nameとして設定
    #     super(CustomUser, self).save(*args, **kwargs)

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
    status = models.CharField(max_length=1, choices=[('P', 'Pending'), ('A', 'Accepted'), ('D', 'Declined')], default='P')

    def accept_request(self):
        self.status = 'A'
        self.save()

    def decline_request(self):
        self.status = 'D'
        self.save()

class Tournament(models.Model):
    size = models.IntegerField(default=4)
    count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

class TournamentUser(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)

class Matchmaking(models.Model):
    user1 = models.ForeignKey(CustomUser, related_name='matchmaking_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(CustomUser, related_name='matchmaking_user2', on_delete=models.CASCADE, null=True, blank=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True, blank=True)  # トーナメントID
    timestamp = models.DateTimeField(auto_now=True)



