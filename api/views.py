from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework.generics import *
from .serializers import *
from .permissions import *


class UserList(ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        return get_user_model().objects.all()


class UserRetrieve(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser, IsAdmin]
    lookup_field = 'pk'

    def get_queryset(self):
        return get_user_model().objects.all()


class BookList(ListAPIView):
    serializer_class = MainPageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['id']

    def get_queryset(self):
        return Book.objects.all()[:1]


class BookSearch(ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        get_params = self.request.query_params.get('search')
        return Book.objects.filter(
            Q(name__icontains=get_params) |
            Q(description__icontains=get_params))


class BookRetrieve(RetrieveAPIView):
    serializer_class = RetrieveBookPageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Book.objects.all()