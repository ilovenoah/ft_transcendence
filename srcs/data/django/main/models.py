from django.db import models
from .validators import validate_file_size

class Image(models.Model):
    image = models.ImageField(upload_to='images/', validators=[validate_file_size])
