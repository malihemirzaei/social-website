from django.contrib import admin

from apps.post.models import Post, Comment, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'content', 'image']
    readonly_fields = ['created_date']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['note', 'created_date']
    readonly_fields = ['created_date']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['post_id', 'user_id', 'created_date']
    readonly_fields = ['created_date']
