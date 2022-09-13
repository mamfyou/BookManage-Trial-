from django.shortcuts import render
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