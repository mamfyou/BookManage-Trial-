from django.urls import path
from .views import *

urlpatterns = [
    path('admin/users/', UserList.as_view(), name='user-list'),
    path('admin/users/<int:pk>/', UserRetrieve.as_view(), name='user-retrieve'),
]
