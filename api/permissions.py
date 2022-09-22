from rest_framework.permissions import BasePermission, IsAuthenticated
from panel_toolbox.models import History


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return IsAuthenticated and request.user.is_superuser


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return IsAuthenticated and request.user.is_staff


class IsNotBorrowed(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not History.objects.filter(id=obj.id,
                                          is_active=True,
                                          User_id=request.user.id
                                          ).exists()


class IsBorrowed(BasePermission):
    def has_object_permission(self, request, view, obj):
        return History.objects.filter(id=obj.id,
                                      is_active=True,
                                      User_id=request.user.id
                                      ).exists()
