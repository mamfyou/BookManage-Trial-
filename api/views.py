from django.db.models import Q
from rest_framework import status
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from .serializers import *
from .permissions import *


class BookChange(RetrieveUpdateDestroyAPIView):
    serializer_class = BookSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Book.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid()
        x = serializer.validated_data['category']
        print(x)
        return super().update(request, *args, **kwargs)


class UserList(ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        return get_user_model().objects.all()


class UserRetrieve(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return get_user_model().objects.all()


class BookList(ListAPIView):
    serializer_class = MainPageSerializer

    def get_queryset(self):
        return Book.objects.all()[:1]


class BookSearch(ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        search_param = self.request.query_params.get('s')
        if search_param:
            return Book.objects.filter(
                Q(name__icontains=search_param) |
                Q(description__icontains=search_param))
        return None


class BookRetrieve(RetrieveAPIView):
    def get_serializer_class(self):
        user = self.request.user
        if History.objects.filter(
                user_id=user.id,
                book_id=self.kwargs['pk'],
                is_active=True
        ).exists():
            return RetrieveLendedBookSerializer
        return RetrieveExistingBookSerializer

    lookup_field = 'pk'

    def get_queryset(self):
        return Book.objects.all()


class LikeDislike(APIView):
    def post(self, request, *args, **kwargs):
        comment_id = self.request.data.get('comment_id', None)
        comment_obj = Comment.objects.filter(id=comment_id)
        like = request.data.get('like', None)
        dislike = request.data.get('dislike', None)
        if like and dislike:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': 'like and dislike can not exist at the same time'})
        elif like == 'true':
            comment_obj.update(like_count=F('like_count') + 1)
            return Response(status=HTTP_201_CREATED, data={'Reaction added successfully'})
        elif dislike == 'true':
            comment_obj.update(dislike_count=F('dislike_count') + 1)
            return Response(status=HTTP_201_CREATED, data={'Reaction added successfully'})
        return Response(status=HTTP_201_CREATED, data={'Invalid Input'})


class BorrowBook(ListCreateAPIView):
    serializer_class = BorrowBookDetailSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        if self.request == 'POST':
            return History.objects.all()
        return Book.objects.all()[:1]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Request Successfully Created, Wait for admin approval'},
                        status=status.HTTP_201_CREATED, headers=headers)


class ExtendBook(RetrieveUpdateAPIView):
    serializer_class = ExtendBookSerializer
    lookup_field = 'pk'

    def get_object(self):
        return History.objects.get(book_id=self.kwargs['pk'],
                                   user_id=self.request.user.id,
                                   is_active=True)


class ReturnBook(ListCreateAPIView):
    serializer_class = ReturnBookSerializer
    lookup_field = 'pk'
    queryset = Book.objects.all()

    def get(self, request, *args, **kwargs):
        obj = Book.objects.get(id=self.kwargs['pk'])
        serializer = ReturnBookSerializer(obj, data={
            'book': {'id': self.kwargs['pk'], 'name': obj.name}}, )
        return Response(serializer.initial_data)


class MainPanel(RetrieveAPIView):
    serializer_class = MainPanelSerializer
    permission_classes = [IsUserOrSuperUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return get_user_model().objects.all()


class ProfilePanel(RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsUserOrSuperUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return get_user_model().objects.all()


class BookPanel(ListAPIView):
    serializer_class = BookPanelSerializer
    permission_classes = [IsUserOrSuperUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return Book.objects.filter(bookHistory__user_id=self.kwargs['pk'], bookHistory__is_active=True)


class CommentPanel(ListAPIView):
    serializer_class = CommentPanelSerializer
    permission_classes = [IsUserOrSuperUser]
    lookup_field = 'pk'

    def get_queryset(self):
        if self.request.query_params:
            start_date = self.request.query_params['st_date']
            end_date = self.request.query_params['end_date']
            return Book.objects.filter(bookComment__user_id=self.kwargs['pk'],
                                       bookComment__comment_text__isnull=False,
                                       bookComment__created_at__gt=start_date,
                                       bookComment__created_at__lt=end_date)
        return Book.objects.filter(bookComment__user_id=self.kwargs['pk'],
                                   bookComment__comment_text__isnull=False)


class CategoryList(ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrSuperuserOrReadOnly]

    def get_queryset(self):
        return BookCategory.objects.all()


class CategoryRetrieve(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrSuperuserOrReadOnly]
    lookup_field = 'pk'

    def get_queryset(self):
        return BookCategory.objects.all()


class BookCreate(CreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrSuperuserOrReadOnly]


class CommentRetrieve(RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateDestroyCommentSerializer
    permission_classes = [IsTheCommenter]
    lookup_field = 'id'

    def get_queryset(self):
        return Comment.objects.all()


class NotifPanel(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsUserOrSuperUser]
    lookup_field = 'pk'

    def get_queryset(self):
        if self.request.query_params:
            if self.request.query_params.get('gn', False):
                print('--------------')
                return Notification.objects.filter(type='GN',
                                                   user__id=self.kwargs['pk'])
            elif self.request.query_params.get('pv', None):
                return Notification.objects.filter(type__in=['BR', 'EX', 'RT', 'TW'],
                                                   user__id=self.kwargs['pk'])
        return Notification.objects.filter(user__id=self.kwargs['pk'])

# class ReadNotif(RetrieveUpdateDestroyAPIView):
#
