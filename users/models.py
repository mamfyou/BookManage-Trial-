from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class BookUser(AbstractUser):
    picture = models.ImageField(upload_to='profile', blank=True, null=True)
    phone_number = models.CharField(max_length=11)
    telegram_id = models.CharField(max_length=35, unique=True)

