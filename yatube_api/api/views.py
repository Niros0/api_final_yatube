from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from .permissions import PostOrReadOnly
from posts.models import Post, Comment, Group, Follow
from .serializers import (PostSerializer,
                          CommentSerializer,
                          GroupSerializer,
                          FollowGetSerializer,
                          FollowPostSerializer)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (PostOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        super().perform_destroy(instance)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (PostOrReadOnly,)

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return Comment.objects.filter(post=post)

    def _save_comment(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)

    def perform_create(self, serializer):
        self._save_comment(serializer)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого комментария запрещено!')
        self._save_comment(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого комментария запрещено!')
        super().perform_destroy(instance)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (PostOrReadOnly,)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    permission_classes = (IsAuthenticated,)
    search_fields = ('following__username',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FollowGetSerializer
        elif self.request.method == 'POST':
            return FollowPostSerializer

    def get_queryset(self):
        queryset = Follow.objects.filter(user=self.request.user)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(following__username__icontains=search)
        return queryset

    def perform_create(self, serializer):
        following = serializer.validated_data.get('following')
        if following == self.request.user:
            raise serializers.ValidationError({"following": "Вы не можете подписаться на самого себя"})
        if Follow.objects.filter(user=self.request.user, following=following).exists():
            raise serializers.ValidationError({"following": "Вы уже подписаны на этого пользователя"})
        serializer.save(user=self.request.user)

    http_method_names = ['get', 'post']
