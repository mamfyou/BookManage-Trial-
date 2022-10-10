from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, F
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from book.models import Book, Comment, Rate, BookCategory
from users.models import BookUser
from panel_toolbox.models import History, Notification, Request


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'password', 'confirm_password', 'email',
                  'first_name', 'last_name', 'telegram_id', 'phone_number']
        write_only_fields = ['confirm_password']

    confirm_password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = super().create(validated_data)
        user_password = user.password
        user.set_password(user_password)
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        user_password = user.password
        user.set_password(user_password)
        user.save()
        return user

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError('Passwords didn\'t match')
        return attrs


class UpdateDestroyCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'comment_text']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'comment_text', 'user_id', 'user_pic', 'like_count', 'dislike_count']

    def get_user_name(self, obj):
        return BookUser.objects.get(id=obj.user_id).username

    def get_user_pic(self, obj):
        return BookUser.objects.get(id=obj.user_id).phone_number

    user_id = SerializerMethodField(method_name='get_user_name')
    user_pic = SerializerMethodField(method_name='get_user_pic')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = '__all__'


class BookPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'picture']


class MainPageSerializer(serializers.Serializer):
    @staticmethod
    def get_newest(self):
        three_months_ago = timezone.now() - timezone.timedelta(days=30 * 3)
        is_newest = Book.objects.filter(count__gt=0).order_by('-created_at')
        return BookPreviewSerializer(is_newest[:10], many=True).data

    @staticmethod
    def get_most_popular(self):
        wanted_filter = Book.objects.filter(count__gt=0).order_by('-bookRate')
        return BookPreviewSerializer(wanted_filter[:10], many=True).data

    @staticmethod
    def get_most_wanted(self):
        wanted_filter = Book.objects.filter(count__gt=0).order_by('-wanted_to_read')
        return BookPreviewSerializer(wanted_filter[:10], many=True).data

    newest_books = SerializerMethodField(method_name='get_newest')
    most_popular_books = SerializerMethodField(method_name='get_most_popular')
    most_wanted_books = SerializerMethodField(method_name='get_most_wanted')


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class CommentIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id']


class BookRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        exclude = ['count', 'created_at']

    @staticmethod
    def get_category(self):
        category = []
        x = Book.objects.get(id=self.id).category.all()
        print(x)
        for i in x:
            category.append(i)
        print(category)
        category_set = [[], [], [], []]
        print(len(category))
        for i in range(0, len(category)):
            if category[i].parent is not None:
                category_set[i] += [category[i].id]
                while category[i].parent is not None:
                    category_set[i] += [category[i].parent.id]
                    category[i] = category[i].parent
            else:
                category_set[i] += [category[i].id]

        final_set = []
        for i in category_set:
            if len(i) is not 0:
                final_set += [[*set(i)]]
        return final_set

    category = SerializerMethodField(method_name='get_category')


class RetrieveExistingBookSerializer(serializers.Serializer):

    @staticmethod
    def get_rate(self):
        rate = Rate.objects.filter(book_id=self).aggregate(Avg('rate'))
        if rate['rate__avg'] is not None:
            return round(rate.get('rate__avg'), 1)
        return None

    @staticmethod
    def get_comments(self):
        comments = Comment.objects.filter(book_id=self)
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
        rate = Rate.objects.filter(book_id=self).aggregate(Avg('rate'))
        if rate['rate__avg'] is not None:
            return round(rate.get('rate__avg'), 1)
        return None

    @staticmethod
    def get_comments(self):
        comments = Comment.objects.filter(book_id=self)
        # .order_by('-created_at')
        return CommentSerializer(comments, many=True).data

    @staticmethod
    def get_deadline(self):
        history = History.objects.get(book_id=self, is_active=True)
        deadline_days = history.end_date - timezone.now()
        return deadline_days.days

    book = BookRetrieveSerializer(source='*')
    rate = SerializerMethodField(method_name='get_rate')
    comments = SerializerMethodField(method_name='get_comments')
    deadline = SerializerMethodField(method_name='get_deadline')


class BookRetrieveBorrowedPageSerializer(serializers.Serializer):

    @staticmethod
    def get_rate(self):
        rate = Rate.objects.filter(book_id=self).aggregate(Avg('rate'))
        return round(rate.get('rate__avg'), 1)

    @staticmethod
    def get_comments(self):
        comments = Comment.objects.filter(book_id=self)
        # .order_by('-created_at')
        return CommentSerializer(comments, many=True).data

    def get_deadline_day_number(self):
        row_history = History.objects.get(book_id=self, user_id=self.context['request'].user.id)
        return (row_history.end_date - timezone.now()).days

    book = BookRetrieveSerializer(source='*')
    rate = SerializerMethodField(method_name='get_rate')
    comments = SerializerMethodField(method_name='get_comments')
    deadline_day_number = SerializerMethodField(method_name='get_deadline_day_number')


class BorrowBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'picture', 'name']
        read_only_fields = ['id', 'picture', 'name']


class BorrowBookDetailSerializer(serializers.Serializer):
    def get_rate(self, instance):
        book = Book.objects.get(id=self.context['view'].kwargs['pk'])
        rate = Rate.objects.filter(book_id=book.id).aggregate(Avg('rate'))
        avg = None
        if rate.get('rate__avg') is None:
            avg = 3
        else:
            avg = round(rate.get('rate__avg', 3), 1)
        return avg

    book = BorrowBookSerializer(source='*', read_only=True)
    rate = SerializerMethodField(method_name='get_rate', read_only=True)
    End_date = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        book = Book.objects.get(id=self.context['view'].kwargs['pk'])
        History.objects.create(user_id=user.id,
                               book_id=self.context['view'].kwargs['pk'],
                               is_active=True,
                               start_date=timezone.now(),
                               end_date=datetime.now() + timedelta(days=int(validated_data.get('End_date'))))
        Request.objects.create(user_id=user.id,
                               type='BR',
                               text=f'User {user.username} wants to borrow book {book.name}.'
                                    f'The number of available copies after borrowing this will be {book.count}!')
        return validated_data

    def validate(self, attr):
        book = Book.objects.get(id=self.context['view'].kwargs['pk'])
        if attr.get('End_date') not in [14, 30]:
            raise serializers.ValidationError('Invalid end date')
        already_borrowed = \
            History.objects.filter(user_id=self.context['request'].user.id,
                                   book_id=self.context['view'].kwargs['pk'],
                                   is_active=True).exists()
        if already_borrowed:
            raise ValidationError('You already borrowed this book')
        if not self.context['request'].user.is_superuser and \
                History.objects.filter(user_id=self.context['request'].user.id, is_active=True).count() is 2:
            raise ValidationError('You can not borrow more than 2 books')
        if book.count < 1:
            raise ValidationError("We don't have the book")
        return attr


class ExtendBookSerializer(serializers.Serializer):
    end_date = serializers.IntegerField(write_only=True)
    book = BorrowBookDetailSerializer(read_only=True)

    def update(self, instance, validated_data):
        instance.end_date += timedelta(days=validated_data.get('end_date'))
        instance.is_renewal = True
        instance.save()
        return instance

    def validate(self, attr):
        already_extended = \
            History.objects.filter(user_id=self.context['request'].user.id,
                                   book_id=self.context['view'].kwargs['pk'],
                                   is_active=True, is_renewal=True).exists()
        is_borrowed = \
            History.objects.filter(user_id=self.context['request'].user.id,
                                   book_id=self.context['view'].kwargs['pk'],
                                   is_active=True).exists()
        if not is_borrowed:
            raise ValidationError('You have not borrowed this book')
        if attr.get('end_date') not in [3, 5, 7]:
            raise serializers.ValidationError('Invalid renewal date')
        if already_extended:
            raise serializers.ValidationError('You already extended this book')
        return attr


class CommentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_text']


class HistoryBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['start_date', 'end_date', 'is_active']


class RateFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['rate']


class ReturnBookSerializer(serializers.Serializer):
    rate = RateFeedbackSerializer(source='*')
    comment = CommentFeedbackSerializer(source='*')
    book = BookRetrieveSerializer(data={'book': {'id': 'id', 'picture': 'picture', 'name': 'name'}},
                                  read_only=True)
    is_not_read = serializers.BooleanField(write_only=True)

    def create(self, validated_data):
        book_id = self.context.get('view').kwargs.get('pk')
        user_id = self.context['request'].user.id
        if History.objects.filter(book_id=book_id,
                                  user_id=user_id,
                                  is_active=True).exists():
            if not Comment.objects.filter(book_id=book_id, user_id=user_id).exists():
                History.objects.filter(book_id=book_id,
                                       user_id=user_id,
                                       is_active=True).update(is_active=False)
                Comment.objects.create(book_id=book_id,
                                       user_id=user_id,
                                       comment_text=validated_data.get('comment_text'))
                Rate.objects.create(book_id=book_id,
                                    user_id=user_id,
                                    rate=validated_data.get('rate'))
                return validated_data
            if Comment.objects.filter(book_id=book_id, user_id=user_id).exists():
                Comment.objects.filter(book_id=book_id, user_id=user_id)[:0].update(
                    comment_text=validated_data.get('comment_text'))
                Rate.objects.filter(book_id=book_id, user_id=user_id)[:0].update(
                    rate=validated_data.get('rate'))
                return validated_data
        return ValidationError('You did not borrow this book')

    def validate(self, attr):
        if attr.get('is_not_read', False) is False and (
                (attr.get('comment_text', None) is None) or (attr.get('rate', None) is None)):
            raise serializers.ValidationError('rate and comment required')
        elif attr.get('is_not_read', True) and (
                (attr.get('comment_text', None) is not None) and (attr.get('rate', None) is not None)):
            raise serializers.ValidationError('You haven\'t read the book')
        if attr.get('rate') > 5 or attr.get('rate') < 1:
            raise serializers.ValidationError('Invalid rate')
        return attr


class PanelUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'picture']


class MainPanelSerializer(serializers.Serializer):
    @staticmethod
    def get_is_unread(self):
        return Notification.objects.filter(is_read=False, user__id=self.id).exists()

    User = PanelUserSerializer(source='*',
                               data={'User': {'id': 'id', 'first_name': 'first_name', 'last_name': 'last_name',
                                              'picture': 'picture'}})

    is_unread_notif = SerializerMethodField(method_name='get_is_unread')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'username', 'telegram_id', 'picture', 'phone_number']


class BookPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'picture', 'author', 'dead_line']

    def get_expire_date(self, instance):
        history = History.objects.get(user_id=self.context['request'].user.id,
                                      book_id=instance.id,
                                      is_active=True)
        return history.end_date

    dead_line = SerializerMethodField(method_name='get_expire_date')


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_text']


class CommentPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'picture', 'comment', 'comment_id']

    def get_comment(self, instance):
        comment = Comment.objects.get(book_id=instance.id,
                                      user_id=self.context['view'].kwargs['pk'])
        return comment.comment_text

    def get_comment_id(self, instance):
        comment = Comment.objects.get(book_id=instance.id,
                                      user_id=self.context['view'].kwargs['pk'])
        return comment.id

    comment_id = SerializerMethodField(method_name='get_comment_id')
    comment = SerializerMethodField(method_name='get_comment')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'description', 'is_read', 'created_at', 'type', 'book_pic']

    def get_book_pic(self, instance):
        if instance.type is 'BR':
            history = History.objects.filter(user=self.context['request'].user,
                                             is_active=True) \
                .order_by('-created')[0].get()
            return Book.objects.get(id=history.book_id).picture
        elif instance.type is 'EX':
            history = History.objects.filter(user=self.context['request'].user,
                                             is_active=True, is_renewal=True) \
                .order_by('-created')[0].get()
            return Book.objects.get(id=history.book_id).picture
        elif instance.type is 'RT':
            history = History.objects.filter(user=self.context['request'].user,
                                             is_active=False).order_by('-created')[0].get()
            return Book.objects.get(id=history.book_id).picture
        elif instance.type is 'TW':
            numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            num = 0
            for i in numbers:
                if instance.description.contains(i):
                    num = i
                    break
            history = History.objects.filter(user=self.context['request'].user,
                                             is_active=True,
                                             end_date__lte=datetime.now() + timedelta(days=num)) \
                .order_by('-created')[0].get()
            return Book.objects.get(id=history.book_id).picture
        else:
            return None

    book_pic = SerializerMethodField(method_name='get_book_pic')


class LikeDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['like_count', 'dislike_count']
