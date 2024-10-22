from rest_framework import permissions


class PostOrReadOnly(permissions.BasePermission):
    message = "У вас нет прав для выполнения этого действия."

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
