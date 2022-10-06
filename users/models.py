from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class BookUser(AbstractUser):
    # phone_validate = RegexValidator(regex='^09[1-9]{2}\d{7}$',
    #                                 message="Phone number must be entered in the format: '09123456789'")
    picture = models.ImageField(upload_to='profile', blank=True, null=True)
    phone_number = models.CharField(max_length=11, blank=True)
    telegram_id = models.CharField(max_length=35)
