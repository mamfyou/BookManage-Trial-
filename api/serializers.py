from django.contrib.auth import get_user_model
from django.db.models import Avg, F
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.generics import ListCreateAPIView

from book.models import Book, Feedback
from users.models import BookUser
from panel_toolbox.models import History


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
        is_newest = Book.objects.filter(created_at__gt=three_months_ago, count__gt=0).order_by('-created_at')
        return BookPreviewSerializer(is_newest[:10], many=True).data

    @staticmethod
    def get_most_popular(self):
        wanted_filter = Book.objects.filter(BookFeedback__rate__gte=4, count__gt=0).order_by('-BookFeedback__rate')
        return BookPreviewSerializer(wanted_filter[:10], many=True).data

    @staticmethod
    def get_most_wanted(self):
        wanted_filter = Book.objects.filter(wanted_to_read__gt=10, count__gt=0).order_by('-wanted_to_read')
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
        fields = ['id', 'name', 'description', 'volume_num', 'count']


class RetrieveExistingBookSerializer(serializers.Serializer):

    @staticmethod
    def get_rate(self):
        rate = Feedback.objects.filter(Book_id=self).aggregate(Avg('rate'))
        if rate['rate__avg'] is not None:
            return round(rate.get('rate__avg'), 1)
        return None

    @staticmethod
    def get_comments(self):
        comments = Feedback.objects.filter(Book_id=self)
        # .order_by('-created_at')
        return CommentSerializer(comments, many=True).data

    @staticmethod
    def get_available(self):
        return Book.objects.get(id=self.id).count > 0

    book = BookRetrieveSerializer(source='*')
    rate = SerializerMethodField(method_name='get_rate')
    comments = SerializerMethodField(method_name='get_comments')
    is_available = serializers.SerializerMethodField(method_name='get_available')


class RetrieveLendedBookSerializer(serializers.Serializer):

    @staticmethod
    def get_rate(self):
        rate = Feedback.objects.filter(Book_id=self).aggregate(Avg('rate'))
        if rate['rate__avg'] is not None:
            return round(rate.get('rate__avg'), 1)
        return None

    @staticmethod
    def get_comments(self):
        comments = Feedback.objects.filter(Book_id=self)
        # .order_by('-created_at')
        return CommentSerializer(comments, many=True).data

    @staticmethod
    def get_deadline(self):
        history = History.objects.get(Book_id=self, is_active=True)
        deadline_days = history.end_date - timezone.now()
        return deadline_days.days

    book = BookRetrieveSerializer(source='*')
    rate = SerializerMethodField(method_name='get_rate')
    comments = SerializerMethodField(method_name='get_comments')
    deadline = SerializerMethodField(method_name='get_deadline')


class BookRetrieveBorrowedPageSerializer(serializers.Serializer):

    @staticmethod
    def get_rate(self):
        rate = Feedback.objects.filter(Book_id=self).aggregate(Avg('rate'))
        return round(rate.get('rate__avg'), 1)

    @staticmethod
    def get_comments(self):
        comments = Feedback.objects.filter(Book_id=self)
        # .order_by('-created_at')
        return CommentSerializer(comments, many=True).data

    def get_deadline_day_number(self):
        row_history = History.objects.get(Book_id=self, User_id=self.context['request'].user.id)
        return (row_history.end_date - timezone.now()).days

    book = BookRetrieveSerializer(source='*')
    rate = SerializerMethodField(method_name='get_rate')
    comments = SerializerMethodField(method_name='get_comments')
    deadline_day_number = SerializerMethodField(method_name='get_deadline_day_number')


class BorrowBookSerializer(serializers.Serializer):

    def get_book_name(self, value):
        book_id = self.context['request'].data['book_id']
        return value.get(id=book_id).name

    def get_book_id(self, value):
        book_id = self.context['request'].data['book_id']
        return value.get(id=book_id).id

    def get_book_pic(self, value):
        book_id = self.context['request'].data['book_id']
        return value.get(id=book_id).picture

    def get_rate(self):
        rate = Feedback.objects.filter(Book_id=self).aggregate(Avg('rate'))
        return round(rate.get('rate__avg'), 1)

    end_date = serializers.DateTimeField()


class ExtendBookSerializer(serializers.Serializer):
    new_end_date = serializers.DateTimeField()

    def update(self, instance, validated_data):
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.save()
        return instance


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['rate', 'comment', 'is_read']


class HistoryBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['start_date', 'end_date', 'is_active']


class ReturnBookSerializer(serializers.Serializer):

    def get_book_name(self, instance):
        return Book.objects.get(id=instance.id).name

    # def get_book_pic(self, instance):
    #     return Book.objects.get(id=instance.id).picture

    def get_book_id(self, instance):
        return Book.objects.get(id=instance.id).id

    feedback = FeedbackSerializer(source='*')
    book_name = SerializerMethodField(method_name='get_book_name')
    # book_pic = SerializerMethodField(method_name='get_book_pic')
    book_id = SerializerMethodField(method_name='get_book_id')
