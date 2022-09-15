from django.urls import path, include
from .views import *

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('admin/users/', UserList.as_view(), name='user-list'),
    path('admin/users/<int:pk>/', UserRetrieve.as_view(), name='user-retrieve'),
    path('', BookList.as_view(), name='book-list'),
]
