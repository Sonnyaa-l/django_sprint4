"""Формы приложения users."""
from django import forms
from django.contrib.auth import get_user_model


class UserEditForm(forms.ModelForm):
    """Форма редактирования профиля пользователя."""

    class Meta:
        """Настройки формы."""

        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')
