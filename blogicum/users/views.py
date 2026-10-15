"""Вьюхи приложения users."""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserEditForm


class RegistrationView(CreateView):
    """Регистрация нового пользователя."""

    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/registration_form.html'


@login_required
def edit_profile(request, username=None):
    """Редактирование профиля пользователя."""
    user_model = get_user_model()

    if username is None:
        user = request.user
    else:
        user = get_object_or_404(user_model, username=username)
        if request.user != user:
            return redirect('blog:profile', username=username)

    form = UserEditForm(
        request.POST or None,
        request.FILES or None,
        instance=user,
    )
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=user.username)
    return render(request, 'blog/user.html', {'form': form})
