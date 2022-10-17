from django.db.models import Q
from rest_framework import status
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from .serializers import *
from .permissions import *
from panel_toolbox.models import *


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
    filterset_fields = ['category']

    def get_queryset(self):
        search_param = self.request.query_params.get('s')
        if search_param:
            return Book.objects.filter(
                Q(name__icontains=search_param))
        return Book.objects.all()


class BookRetrieve(RetrieveAPIView):
    def get_serializer_class(self):
        user = self.request.user
        if History.objects.filter(
                user_id=user.id,
                book_id=self.kwargs['pk'],
                is_active=True,
                is_accepted=True,
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(status=201, data={'message': 'Book extension request created successfully'})


class ReturnBook(ListCreateAPIView):
    serializer_class = ReturnBookSerializer
    lookup_field = 'pk'
    queryset = Book.objects.all()

    def get(self, request, *args, **kwargs):
        obj = Book.objects.get(id=self.kwargs['pk'])
        serializer = ReturnBookSerializer(obj, data={
            'book': {'id': self.kwargs['pk'], 'name': obj.name}}, )
        return Response(serializer.initial_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data={'message': 'Request created successfully'}, status=status.HTTP_201_CREATED,
                        headers=headers)


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
    filterset_fields = ['type']

    def get_queryset(self):
        return Notification.objects.filter(user__id=self.kwargs['pk'])


class ReqAdmin(ListAPIView):
    serializer_class = RequestAdminSerializer
    permission_classes = [IsSuperUser]
    filterset_fields = ['type']

    def get_queryset(self):
        if self.request.query_params:
            start_date = self.request.query_params['st_date']
            end_date = self.request.query_params['end_date']
            return Request.objects.filter(created__gt=start_date,
                                          created__lt=end_date, is_read=False)
        return Request.objects.filter(is_read=False)


class ReqResponse(CreateAPIView):

    def post(self, request, *args, **kwargs):
        request_id = self.request.data.get('id', None)
        response = self.request.data.get('response', None)
        request_obj = None
        history_br = None
        history_ex = None
        history_rt = None
        book = None
        if request_id is not None:
            request_obj = Request.objects.get(id=request_id)
            book = Book.objects.get(id=request_obj.book_id)
        if request_obj.type == 'BR':
            history_br = History.objects.get(user_id=request.user.id,
                                             book_id=request_obj.book_id,
                                             is_active=True,
                                             is_accepted=False)
            if response == 'true':
                request_obj.update(is_read=True)
                history_br.update(is_accepted=True,
                                  start_date=timezone.now(),
                                  end_date=datetime.now() + timedelta(days=request_obj.metadata['end_date']))
                Notification.objects.create(type='BR',
                                            title='Borrow Response',
                                            user_id=request.user.id,
                                            description=f'Your Borrow Request for book {book.name} is confirmed, congratulations',
                                            )
                book.count -= 1
                book.wanted_to_read += 1
            elif response == 'false':
                history_br.update(is_active=False)
                request_obj.update(is_read=True)
                Notification.objects.create(type='BR',
                                            title='Borrow Response',
                                            user_id=request.user.id,
                                            description=f'Your Borrow Request for book {book.name} is declined, unfortunately',
                                            )
        elif request_obj.type == 'EX':
            history_ex = History.objects.get(user_id=request.user.id,
                                             book_id=request_obj.book_id,
                                             is_active=True,
                                             is_accepted=True)
            if response == 'true':
                request_obj.update(is_read=True)
                history_ex.update(is_renewal=True,
                                  end_date=F('end_date') + timedelta(days=request_obj.metadata['end_date']))
                Notification.objects.create(
                    type='EX',
                    title='Extend Response',
                    user_id=request.user.id,
                    description=f'Your Extend Request for book {book.name} is accepted, congratulations',
                )
            elif response == 'false':
                request_obj.update(is_read=True)
                Notification.objects.create(type='EX',
                                            title='Extend Response',
                                            user_id=request.user.id,
                                            description=f'Your Extend Request for book {book.name} is declined, unfortunately',
                                            )
        elif request_obj.type == 'RT':
            history_rt = History.objects.get(user_id=request.user.id,
                                             book_id=request_obj.book_id,
                                             is_active=True,
                                             is_accepted=True)
            if response == 'true':
                request_obj.update(is_read=True)
                history_rt.update(is_active=False)
                Notification.objects.create(type='RT',
                                            title='Return Response',
                                            user_id=request.user.id,
                                            description=f'Your Return Request for book {book.name} is accepted',
                                            )
                book.count += 1


class AvailableNotification(CreateAPIView):

    def create(self, request, *args, **kwargs):
        if request.data.get('book_id', None) is None:
            raise ValidationError('Book id is None')
        elif not Book.objects.filter(id=request.data.get('book_id', None)).exists():
            raise ValidationError('Invalid Book id')
        elif AvailableNotification.objects.filter(
                book_id=request.data.get('book_id', None),
                user_id=request.user.id).exists():
            raise ValidationError('Notification already exists')
        Notification.objects.create(
            user_id=request.user.id,
            book_id=request.data.get('book_id'),
        )
