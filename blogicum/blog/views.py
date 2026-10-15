"""Вьюхи блога."""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()


def _published_posts():
    """Базовый queryset опубликованных постов."""
    return Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    ).annotate(
        comment_count_annotated=Count('comments'),
    ).order_by('-pub_date')


def index(request):
    """Главная страница: список опубликованных постов с пагинацией."""
    post_list = _published_posts()
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Страница отдельного поста с комментариями и формой."""
    post = get_object_or_404(Post, pk=post_id)

    # Проверка видимости поста
    is_author = request.user == post.author
    is_staff = request.user.is_staff

    # Пост не опубликован — только автор и админ
    if not post.is_published and not (is_author or is_staff):
        raise Http404

    # Категория снята с публикации — только автор и админ
    if not post.category.is_published and not (is_author or is_staff):
        raise Http404

    # Дата публикации в будущем — только автор и админ
    if post.pub_date > timezone.now() and not (is_author or is_staff):
        raise Http404

    comments = post.comments.select_related('author').order_by('created_at')
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, slug):
    """Посты одной категории."""
    category = get_object_or_404(Category, slug=slug, is_published=True)
    post_list = _published_posts().filter(category=category)
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    """Профиль пользователя."""
    author = get_object_or_404(User, username=username)
    if request.user == author:
        post_list = Post.objects.filter(author=author).order_by('-pub_date')
    else:
        post_list = _published_posts().filter(author=author)
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'profile': author,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    """Создание нового поста."""
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    """Удаление поста."""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html',
                  {'form': PostForm(instance=post)})


@login_required
@require_POST
def add_comment(request, post_id):
    """Добавление комментария к посту."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        Post.objects.filter(pk=post.pk).update(
            comment_count=post.comments.count()
        )
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request, 'blog/comment.html',
        {'form': form, 'comment': comment},
    )


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        Post.objects.filter(pk=post_id).update(
            comment_count=Post.objects.get(pk=post_id).comments.count()
        )
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request, 'blog/comment.html',
        {'comment': comment},
    )


@login_required
def edit_profile(request, username=None):
    """Редактирование профиля."""
    from django.contrib.auth import get_user_model
    from users.forms import UserEditForm

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
