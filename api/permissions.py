from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from panel_toolbox.models import History


class IsAdminOrSuperuserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS \
               or request.user.is_superuser \
               or request.user.is_staff


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return IsAuthenticated and request.user.is_superuser


class IsAdminOrSuperuser(BasePermission):
    def has_permission(self, request, view):
        return IsAuthenticated and request.user.is_staff or request.user.is_superuser


class IsNotBorrowed(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not History.objects.filter(id=obj.id,
                                          is_active=True,
                                          user_id=request.user.id
                                          ).exists()


class IsBorrowed(BasePermission):

    def has_permission(self, request, view):
        return History.objects.filter(book_id=view.kwargs['pk'],
                                      user_id=request.user,
                                      is_active=True
                                      ).exists()


class IsUserOrSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.id is view.kwargs['pk'] or request.user.is_superuser
