from django.urls import path, include, re_path
from .views import *

urlpatterns = [
    # Authentication
    path('auth/', include('rest_framework.urls')),
    # User Panel
    path('panel/<int:pk>/', MainPanel.as_view(), name='panel-main-page'),
    path('panel/<int:pk>/profile/', ProfilePanel.as_view(), name='panel-profile'),
    path('panel/<int:pk>/books/', BookPanel.as_view(), name='panel-books'),
    path('panel/<int:pk>/comments/', CommentPanel.as_view(), name='panel-comments'),
    path('panel/<int:pk>/comments/<int:id>/edit/', CommentRetrieve.as_view(), name='panel-comment-update'),
    path('panel/<int:pk>/notification/', NotifPanel.as_view(), name='panel-notification'),
    # path('panel/<int:pk>/notification/reads', NotifPanel.as_view(), name='panel-comments'),
    # Admin Panel
    path('admin/users/', UserList.as_view(), name='user-list'),
    path('admin/users/<int:pk>/', UserRetrieve.as_view(), name='user-retrieve'),
    path('category/', CategoryList.as_view(), name='category-list'),
    path('category/<int:pk>/', CategoryRetrieve.as_view(), name='category-list'),
    # search
    path('search/', BookSearch.as_view(), name='book-search'),
    # books
    path('', BookList.as_view(), name='book-list'),
    path('create/', BookCreate.as_view(), name='book-list'),
    path('books/<int:pk>/', BookRetrieve.as_view(), name='book-retrieve'),
    path('books/<int:pk>/likedislike/', LikeDislike.as_view(), name='book-retrieve'),
    path('books/<int:pk>/change/', BookChange.as_view(), name='book-list'),
    path('books/<int:pk>/borrow/', BorrowBook.as_view(), name='book-borrow'),
    path('books/<int:pk>/extend/', ExtendBook.as_view(), name='book-extend'),
    path('books/<int:pk>/return/', ReturnBook.as_view(), name='book-feedback'),
]
