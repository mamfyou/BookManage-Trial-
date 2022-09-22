from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from book.models import Book


class History(models.Model):
    User = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userHistory')
    Book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookHistory')
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_renewal = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.Book.name


class Notification(models.Model):
    PRIORITY_CHOICES = (
        ('U', 'Urgent'),
        ('I', 'Important'),
        ('N', 'Normal'),
        ('L', 'Low'),
    )

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    # user_group =
    user_group = models.ManyToManyField(get_user_model(), related_name='userNotification')
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=1)


class BookShelf(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    User = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userBookShelf')
    Book = models.ManyToManyField(Book, related_name='bookBookShelf')


class Request(models.Model):
    object_id = models.PositiveIntegerField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_obj = GenericForeignKey()
    created = models.DateTimeField(auto_now_add=True)
