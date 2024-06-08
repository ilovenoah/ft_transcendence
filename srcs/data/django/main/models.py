from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .validators import validate_file_size

class CustomUser(AbstractUser):
    avatar = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        default='avatars/default.png'  # デフォルト画像のパスを指定
    )
    is_online = models.BooleanField(default=False) #オンラインステータス
    last_active = models.DateTimeField(default=timezone.now)  # 最後にアクティブだった時間

    def send_friend_request(self, to_user):
        if self == to_user:
            raise ValidationError("You cannot send a friend request to yourself.")
        if FriendRequest.objects.filter(from_user=self, to_user=to_user, status='P').exists():
            raise ValidationError("There is already a pending friend request to this user.")
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