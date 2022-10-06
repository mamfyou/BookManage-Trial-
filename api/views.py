from django.db.models import Q
from rest_framework import status
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .permissions import *
from datetime import datetime, timedelta


class BookChange(RetrieveUpdateDestroyAPIView):
    serializer_class = BookSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Book.objects.all()


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
                user_id=user.id,
                book_id=self.kwargs['pk'],
                is_active=True
        ).exists():
            return RetrieveLendedBookSerializer
        return RetrieveExistingBookSerializer

    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Book.objects.all()


class BorrowBook(ListCreateAPIView):
    serializer_class = BorrowBookDetailSerializer
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated, IsBorrowed]
    lookup_field = 'pk'

    def get_object(self):
        return History.objects.get(book_id=self.kwargs['pk'],
                                   user_id=self.request.user.id,
                                   is_active=True)


class ReturnBook(ListCreateAPIView):
    serializer_class = ReturnBookSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    queryset = Book.objects.all()

    def get(self, request, *args, **kwargs):
        obj = Book.objects.get(id=self.kwargs['pk'])
        serializer = ReturnBookSerializer(obj, data={
            'book': {'id': self.kwargs['pk'], 'name': obj.name}}, )
        return Response(serializer.initial_data)


class MainPanel(RetrieveAPIView):
    serializer_class = MainPanelSerializer
    permission_classes = [IsAuthenticated, IsUserOrSuperUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return get_user_model().objects.all()


class ProfilePanel(RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsUserOrSuperUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return get_user_model().objects.all()


class BookPanel(ListAPIView):
    serializer_class = BookPanelSerializer
    permission_classes = [IsAuthenticated, IsUserOrSuperUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return Book.objects.filter(id__gt=24, id__lt=35)


class CommentPanel(ListAPIView):
    serializer_class = CommentPanelSerializer
    permission_classes = [IsAuthenticated, IsUserOrSuperUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return Book.objects.filter(BookFeedback__User_id=self.kwargs['pk'])


class CategoryList(ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperuserOrReadOnly]

    def get_queryset(self):
        return BookCategory.objects.all()


class CategoryRetrieve(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperuserOrReadOnly]
    lookup_field = 'pk'

    def get_queryset(self):
        return BookCategory.objects.all()


class BookCreate(CreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperuserOrReadOnly]
