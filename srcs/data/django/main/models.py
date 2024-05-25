from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True,
        default='avatars/default.png'  # デフォルト画像のパスを指定
    )
    is_online = models.BooleanField(default=False) #オンラインステータス
    last_active = models.DateTimeField(default=timezone.now)  # 最後にアクティブだった時間

    def save(self, *args, **kwargs):
        if not self.nickname:  # nicknameが空の場合
            self.nickname = self.username  # usernameをnicknameに設定
        super().save(*args, **kwargs)

# Create your models here.
