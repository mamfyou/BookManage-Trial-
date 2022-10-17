from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from panel_toolbox.models import AvailableNotification, Notification


class Book(models.Model):
    name = models.CharField(max_length=100)
    picture = models.URLField()
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='owner')
    publisher = models.CharField(max_length=100)
    publish_date = models.DateField()
    author = models.CharField(max_length=100)
    translator = models.CharField(max_length=100, null=True, blank=True)
    page_count = models.PositiveIntegerField()
    volume_num = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField('BookCategory', related_name='bookCategory')
    wanted_to_read = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class BookCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('BookCategory', on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Rate(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userRate')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookRate')
    rate = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='userComment')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookComment')
    comment_text = models.TextField(max_length=500, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.user) + ": " + str(self.book)


@receiver(post_save, sender=Book)
def available_signal(sender, instance, updated, **kwargs):
    if updated:
        if instance.count > 0:
            # send notification
            if AvailableNotification.objects.filter(book=instance).exists():
                notifications = AvailableNotification.objects.filter(book=instance)
                for i in notifications:
                    Notification.objects.create(
                        user=i.user,
                        book=i.book,
                        type='AV',
                        message='The book you wanted to read is available now.',
                    )
