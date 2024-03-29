from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
# from book.models import Book


class History(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userHistory')
    book = models.ForeignKey("book.Book", on_delete=models.CASCADE, related_name='bookHistory')
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_renewal = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.book.name)


class Notification(models.Model):
    TYPE_CHOICES = (
        ('BR', 'Borrow'),
        ('RT', 'Return'),
        ('EX', 'Extend'),
        ('TW', 'Time Warning'),
        ('GN', 'General'),
        ('AV', 'Available'),
    )
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='GN')
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    user = models.ForeignKey(get_user_model(), related_name='userNotification', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.TextField(null=True, blank=True, default=None)
    is_read = models.BooleanField(default=False)


class BookShelf(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userBookShelf')
    book = models.ManyToManyField("book.Book", related_name='bookBookShelf')


class Request(models.Model):
    TYPE_CHOICES = (
        ('BR', 'Borrow'),
        ('RT', 'Return'),
        ('EX', 'Extend'),
    )
    # id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey("book.Book", on_delete=models.CASCADE)
    text = models.TextField(default='')
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=None, null=True)
    metadata = models.JSONField(null=True, blank=True)


class AvailableNotification(models.Model):
    user = models.ManyToManyField(get_user_model(), related_name='availableNotifUser')
    book = models.ManyToManyField("book.Book", related_name='availableNotifBook')
