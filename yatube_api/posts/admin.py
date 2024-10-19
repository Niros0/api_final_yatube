from django.contrib import admin
from.models import Follow


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    search_fields = ('user__username', 'following__username')


admin.site.register(Follow, FollowAdmin)
