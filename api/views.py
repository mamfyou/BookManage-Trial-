from django.db.models import Q
from rest_framework import status
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .permissions import *


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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Book.objects.all()[:1]


class BookSearch(ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

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
                User_id=user.id,
                Book_id=self.kwargs['pk'],
                is_active=True
        ).exists():
            return RetrieveLendedBookSerializer
        return RetrieveExistingBookSerializer

    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Book.objects.all()


class BorrowBook(CreateAPIView):
    serializer_class = BorrowBookSerializer
    permission_classes = [IsAuthenticated, IsNotBorrowed]
    lookup_field = 'pk'

    def create(self, request, *args, **kwargs):
        already_exists_filter = History.objects.filter(User_id=request.user.id, Book_id=kwargs['pk'],
                                                       is_active=True).exists()
        if already_exists_filter:
            raise ValidationError('You already borrowed this book')
        History.objects.create(User_id=request.user.id,
                               Book_id=kwargs['pk'],
                               is_active=True,
                               start_date=timezone.now(),
                               end_date=request.data['end_date'])
        return Response(status=status.HTTP_201_CREATED)


class ExtendBook(UpdateAPIView):
    serializer_class = ExtendBookSerializer
    permission_classes = [IsAuthenticated, IsBorrowed]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        history = History.objects.get(User_id=request.user.id, Book_id=kwargs['pk'], is_active=True)
        history.end_date = request.data['new_end_date']
        history.save()
        return Response(status=status.HTTP_201_CREATED)


class ReturnBook(APIView):
    serializer_class = ReturnBookSerializer
    permission_classes = [IsAuthenticated, IsBorrowed]
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        book_id = Book.objects.get(id=kwargs['pk']).id
        book_name = Book.objects.get(id=kwargs['pk']).name
        # book_pic = Book.objects.get(id=kwargs['pk']).picture
        book = {
            'id': book_id,
            'name': book_name,
            # 'picture': book_pic,
        }
        return Response(book, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        Feedback.objects.create(
            User_id=request.user.id,
            Book_id=kwargs['pk'],
            comment=request.data['comment'],
            rate=request.data['rate'],
            is_read=request.data['is_read'],
        )
        History.objects.get(User_id=request.user.id, Book_id=kwargs['pk'], is_active=True).update(is_active=False)
        return Response(status=status.HTTP_201_CREATED)
