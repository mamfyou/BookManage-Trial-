from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


# Create your models here.
class BookUser(AbstractUser):
    # phone_validate = RegexValidator(regex='0.d{10}$',
    #                                 message="Phone number must be entered in the format: '09123456789'")
    phone_number = models.CharField(max_length=11, blank=True)
    telegram_id = models.CharField(max_length=35)
