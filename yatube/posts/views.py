from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Group, User, Post
from .utils import pagntr

from .forms import PostForm


POSTS_AMOUNT = 10


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = pagntr(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups.select_related('group', 'author')
    page_obj = pagntr(request, post_list)
    context = {
        'page_obj': page_obj,
        'group': group,

    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related('author').filter(
        author__username=username
    )
    page_obj = pagntr(request, post_list)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not request.method == 'POST':
        context = {
            'form': form
        }
        return render(request, 'posts/create_post.html', context)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    context = {
        'form': form
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    is_edit = True
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        if not form.is_valid():
            context = {
                'form': form,
                'is_edit': is_edit,
                'post_id': post_id,
            }
            return render(request, 'posts/create_post.html', context)
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': is_edit,
        'post_id': post_id,
    }
    return render(request, 'posts/create_post.html', context)
