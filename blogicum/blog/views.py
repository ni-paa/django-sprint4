# blog/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView

from .constants import POSTS_ON_PAGE
from .forms import CommentForm, PostForm, ProfileForm
from .mixins import OnlyAuthorMixin, CommentMixin, PostMixin
from .models import Category, Comment, Post, User


class BlogIndexListView(ListView):
    """Главная страница."""

    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/index.html'
    queryset = Post.objects.published(
    ).annotate_comments().select_related()


class CategoryPostsView(ListView):
    """Страницы для категории."""

    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs['slug'], is_published=True
        )
        published_posts = Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category=self.category
        ).order_by('-pub_date')
        posts_with_comments = published_posts.annotate(
            comment_count=Count('comments')
        )
        filtered_posts = posts_with_comments.filter(
            category__is_published=True
        )
        return filtered_posts

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, category=self.category)


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):

    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(OnlyAuthorMixin, PostMixin, UpdateView):

    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=[self.get_object().id])


class PostDeleteView(OnlyAuthorMixin, PostMixin, DeleteView):

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs,
                                        form=PostForm(instance=self.object))

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostDetailView(DetailView):
    """Представление для детальной страницы поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if self.request.user != post.author:
            if not post.is_published:
                raise Http404
        return post

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=CommentForm(),
            comments=self.object.comments.select_related('author'),
            )


class ProfileView(ListView):
    """Представление для просмотра профиля."""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_ON_PAGE

    def get_user(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_posts(self):
        return (
            Post.objects
            .select_related('category', 'author', 'location')
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )

    def get_posts_with_filter(self):
        return (
            self.get_posts()
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        )

    def get_queryset(self):
        if self.request.user == self.get_user():
            return self.get_posts().filter(author=self.get_user())
        return self.get_posts_with_filter().filter(author=self.get_user())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user()
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля."""

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', args=[self.request.user.username])


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
        return reverse('blog:post_detail', args={self.kwargs['post_id']})


class EditCommentView(OnlyAuthorMixin, CommentMixin, UpdateView):
    form_class = CommentForm


class DeleteCommentView(OnlyAuthorMixin, CommentMixin, DeleteView):
    pass
