# blog/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView

from .constants import POSTS_ON_PAGE
from .forms import CommentForm, PostForm, ProfileForm
from .mixins import OnlyAuthorMixin, CommentMixin, PostMixin
from .models import Category, Comment, Post, User


class IndexListView(ListView):
    """Представление для главной страницы."""

    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/index.html'
    queryset = Post.objects.published().annotate_comments()


class CategoryPostsView(ListView):
    """Представление для страницы категории."""

    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/category.html'

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs['slug'], is_published=True
        )
        return category.post_set.published().annotate_comments()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['slug'], is_published=True
        )
        return context


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(OnlyAuthorMixin, PostMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.get_object().id})


class PostDeleteView(OnlyAuthorMixin, PostMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context


class PostDetailView(DetailView):
    """Представление для детальной страницы поста."""

    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        post_id = self.kwargs['post_id']
        try:
            post = Post.objects.get(pk=post_id)
            if post.author == self.request.user:
                return post
            return Post.objects.published().get(pk=post_id)
        except Post.DoesNotExist:
            raise Http404("Пост не найден")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        ).order_by('created_at')
        return context


class ProfileView(ListView):
    """Представление для просмотра профиля."""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        username = self.kwargs['username']
        profile = get_object_or_404(User, username=username)
        posts = Post.objects.filter(author=profile).select_related(
            'author').prefetch_related('comments', 'category', 'location')
        posts_annotated = posts.annotate(comment_count=Count('comments'))
        return posts_annotated.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'profile' not in context:
            context['profile'] = get_object_or_404(
                User, username=self.kwargs['username'])
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля."""

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse('blog:profile', args={self.request.user.username})

    def get_object(self):
        return self.request.user


class AddCommentView(LoginRequiredMixin, CreateView):
    """Обработка добавления комментария к посту."""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class EditCommentView(OnlyAuthorMixin, CommentMixin, UpdateView):
    form_class = CommentForm


class DeleteCommentView(OnlyAuthorMixin, CommentMixin, DeleteView):
    pass
