from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied


class PostOrReadOnly(permissions.BasePermission):
    message = "У вас нет прав для выполнения этого действия."

    def has_permission(self, request, view):
        if (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        ):
            return True
        raise AuthenticationFailed(self.message)

    def has_object_permission(self, request, view, obj):
        if (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and obj.author == request.user
            )
        ):
            return True
        raise PermissionDenied(self.message)
