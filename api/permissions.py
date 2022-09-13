from rest_framework.permissions import BasePermission, IsAuthenticated


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return IsAuthenticated and request.user.is_superuser


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return IsAuthenticated and request.user.is_staff
