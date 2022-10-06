from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from book.models import Book


class History(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userHistory')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookHistory')
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_renewal = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.book.name) + " - " + str(self.user.name)


class Notification(models.Model):
    PRIORITY_CHOICES = (
        ('U', 'Urgent'),
        ('I', 'Important'),
        ('N', 'Normal'),
        ('L', 'Low'),
    )

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    user = models.ManyToManyField(get_user_model(), related_name='userNotification')
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=1)
    is_read = models.BooleanField(default=False)


class BookShelf(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userBookShelf')
    book = models.ManyToManyField(Book, related_name='bookBookShelf')


class Request(models.Model):
    TYPE_CHOICES = (
        ('BR', 'Borrow'),
        ('RT', 'Return'),
        ('EX', 'Extend'),
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.TextField()
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
