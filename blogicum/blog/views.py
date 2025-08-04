# blog/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView

from .forms import CommentForm, PostForm, ProfileForm, SignUpForm
from .mixins import OnlyAuthorMixin
from .models import Category, Comment, Post, User


class IndexListView(ListView):
    """Представление для главной страницы."""

    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'
    queryset = Post.objects.published().annotate_comments()


class CategoryPostsView(ListView):
    """Представление для страницы категории."""

    model = Post
    paginate_by = 10
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


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        if not Post.objects.filter(pk=self.object.pk).exists():
            raise ValueError("Post was not created")
        return response

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


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
    paginate_by = 10

    def get_queryset(self):
        self.profile_user = get_object_or_404(User,
                                              username=self.kwargs['username'])
        queryset = self.profile_user.post_set.with_related(
        ).annotate_comments()
        if self.request.user != self.profile_user:
            queryset = queryset.published()
        return queryset.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile_user
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля."""

    model = User
    form_class = ProfileForm
    template_name = 'blog/create.html'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # form.instance = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class AddCommentView(LoginRequiredMixin, CreateView):
    """Обработка добавления комментария к посту."""

    model = Comment
    form_class = CommentForm

    def get(self, request, *args, **kwargs):
        # Проверяем существование поста при GET-запросе
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if not post.is_accessible_by(self.request.user):
            raise Http404('Post not found')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if not post.is_accessible_by(self.request.user):
            raise Http404('Post not found')

        form.instance.author = self.request.user
        form.instance.post = post
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class EditCommentView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class DeleteCommentView(OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class UserCreateView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
