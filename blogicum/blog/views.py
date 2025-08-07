# blog/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView

from .constants import POSTS_ON_PAGE
from .forms import CommentForm, PostForm, ProfileForm
from .mixins import OnlyAuthorMixin, CommentMixin, PostMixin
from .models import Category, Comment, Post, User


def process_posts(posts=Post.objects.all(), apply_filters=True,
                  use_select_related=True,
                  apply_annotation=True):
    """Фильтрация, аннотирование и сортировка постов."""
    if apply_filters:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    if use_select_related:
        posts = posts.select_related('category', 'location', 'author')
    if apply_annotation:
        posts = posts.annotate(
            comment_count=Count('comments')).order_by(*Post._meta.ordering)
    return posts


class IndexListView(ListView):
    """Главная страница."""

    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/index.html'
    queryset = process_posts()


class CategoryPostsView(ListView):
    """Отображение публикаций в категории."""

    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/category.html'

    def get_category(self):
        return get_object_or_404(
            Category, slug=self.kwargs['slug'], is_published=True
        )

    def get_queryset(self):
        return process_posts(self.get_category().posts.all())


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):

    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(OnlyAuthorMixin, PostMixin, UpdateView):
    """Редактирование публикации."""

    form_class = PostForm

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs[self.pk_url_kwarg]])


class PostDeleteView(OnlyAuthorMixin, PostMixin, DeleteView):
    """Удаление публикации."""

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs,
                                        form=PostForm(instance=self.object))

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostDetailView(DetailView):
    """Детальная страница публикации."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = super().get_object()
        if self.request.user == post.author:
            return post
        return super().get_object(process_posts(
            use_select_related=False,
            apply_annotation=False
        ))

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=CommentForm(),
            comments=self.object.comments.select_related('author'),
        )


class ProfileView(ListView):
    """Просмотр профиля."""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_ON_PAGE

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        author = self.get_author()
        return process_posts(
            author.posts.all(),
            apply_filters=self.request.user != author)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            profile=self.get_author(),
        )


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


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
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class EditCommentView(OnlyAuthorMixin, CommentMixin, UpdateView):
    form_class = CommentForm


class DeleteCommentView(OnlyAuthorMixin, CommentMixin, DeleteView):
    pass
