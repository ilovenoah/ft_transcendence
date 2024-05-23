from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)


# Create your models here.
