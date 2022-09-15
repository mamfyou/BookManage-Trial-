from django.contrib.auth import get_user_model
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    picture = models.ImageField(upload_to='books')
    page_count = models.PositiveIntegerField()
    description = models.JSONField()
    volume_num = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    publish_date = models.DateField()
    category = models.ManyToManyField('BookCategory', related_name='bookCategory')
    wanted_to_read = models.PositiveIntegerField(default=0)
    # owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='books')

    def __str__(self):
        return self.name


class BookCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('BookCategory', on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Feedback(models.Model):
    User = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userFeedback')
    rate = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    comment = models.TextField(max_length=500, null=True)
    Book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='BookFeedback')
    is_read = models.BooleanField(default=True)

    def __str__(self):
        return self.id


