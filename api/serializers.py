from django.contrib.auth import get_user_model
from django.db.models import Avg, F
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from book.models import Book, Feedback
from users.models import BookUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model()
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'comment', 'rate', 'User_id', 'User_pic']

    def get_user_name(self, obj):
        return BookUser.objects.get(id=obj.User_id).username

    def get_user_pic(self, obj):
        return BookUser.objects.get(id=obj.User_id).phone_number

    User_id = SerializerMethodField(method_name='get_user_name')
    User_pic = SerializerMethodField(method_name='get_user_pic')


class BookPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'picture']


class MainPageSerializer(serializers.Serializer):
    @staticmethod
    def get_newest(self):
        three_months_ago = timezone.now() - timezone.timedelta(days=30 * 3)
        newest_filter = Book.objects.filter(created_at__gt=three_months_ago).order_by('-created_at')
        return BookPreviewSerializer(newest_filter[:10], many=True).data

    @staticmethod
    def get_most_popular(self):
        wanted_filter = Book.objects.filter(BookFeedback__rate__gte=4).order_by('-BookFeedback__rate')
        return BookPreviewSerializer(wanted_filter[:10], many=True).data

    @staticmethod
    def get_most_wanted(self):
        wanted_filter = Book.objects.filter(wanted_to_read__gt=10).order_by('-wanted_to_read')
        return BookPreviewSerializer(wanted_filter[:10], many=True).data

    newest_books = SerializerMethodField(method_name='get_newest')
    most_popular_books = SerializerMethodField(method_name='get_most_popular')
    most_wanted_books = SerializerMethodField(method_name='get_most_wanted')


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'description', 'volume_num']


class RetrieveBookPageSerializer(serializers.Serializer):

    @staticmethod
    def get_rate(self):
        rate = Feedback.objects.filter(Book_id=self).aggregate(Avg('rate'))
        return round(rate.get('rate__avg'), 1)

    @staticmethod
    def get_comments(self):
        comments = Feedback.objects.filter(Book_id=self)
        # .order_by('-created_at')
        return CommentSerializer(comments, many=True).data

    book = BookRetrieveSerializer(source='*')
    rate = SerializerMethodField(method_name='get_rate')
    comments = SerializerMethodField(method_name='get_comments')
