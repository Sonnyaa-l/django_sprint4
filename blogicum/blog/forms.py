"""Формы блога."""
from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма создания и редактирования поста."""

    class Meta:
        """Настройки формы."""

        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }


class CommentForm(forms.ModelForm):
    """Форма создания и редактирования комментария."""

    class Meta:
        """Настройки формы."""

        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }
