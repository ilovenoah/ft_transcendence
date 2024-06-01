from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .validators import validate_file_size

class CustomUser(AbstractUser):
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True,
        default='avatars/default.png'  # デフォルト画像のパスを指定
    )
    is_online = models.BooleanField(default=False) #オンラインステータス
    last_active = models.DateTimeField(default=timezone.now)  # 最後にアクティブだった時間

class Image(models.Model):
    image = models.ImageField(upload_to='avatars/', validators=[validate_file_size])
