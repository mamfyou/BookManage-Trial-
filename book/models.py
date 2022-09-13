from django.contrib.auth import get_user_model
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='books')
    page_count = models.PositiveIntegerField()
    description = models.JSONField()
    volume_num = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    publish_date = models.DateField()
    category = models.ManyToManyField('BookCategory', related_name='bookCategory')

    def __str__(self):
        return self.name


class BookCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('BookCategory', on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Feedback(models.Model):
    RATE_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    User = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='userFeedback')
    rate = models.CharField(choices=RATE_CHOICES, max_length=1)
    comment = models.TextField(max_length=500)
    Book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='BookFeedback')
    is_read = models.BooleanField(default=True)

    def __str__(self):
        return self.id


