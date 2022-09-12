from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

phone_validate = RegexValidator(regex=r'^\0\d{0,9}$',
                                message="Phone number must be entered in the format: '09123456789'")


# Create your models here.
class BookUser(AbstractUser):
    phone_number = models.CharField(validators=phone_validate, max_length=11)
    telegram_id = models.CharField(max_length=35)
