"""Регистрация моделей блога в админке."""
from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настройки отображения постов в админке."""

    list_display = ('title', 'author', 'pub_date', 'is_published')
    list_filter = ('is_published', 'category', 'location')
    search_fields = ('title', 'text')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройки отображения категорий в админке."""

    list_display = ('title', 'slug', 'is_published')
    search_fields = ('title', 'slug')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Настройки отображения локаций в админке."""

    list_display = ('name', 'is_published')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Настройки отображения комментариев в админке."""

    list_display = ('text', 'author', 'post', 'created_at')
    search_fields = ('text',)
