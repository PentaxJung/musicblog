from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.http import require_POST

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Post
from .forms import PostForm, CustomUserCreationForm


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_delete(request, pk):
    post = Post.objects.filter(pk=pk)
    post.delete()
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return redirect('post_list')


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@require_POST
def likes(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        if post.like_users.filter(pk=request.user.pk).exists():
            post.like_users.remove(request.user)
        else:
            post.like_users.add(request.user)
        return redirect('post_list')
    return redirect('login')