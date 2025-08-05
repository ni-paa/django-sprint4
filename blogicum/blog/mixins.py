from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Comment, Post


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail', self.kwargs['post_id'])


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(
            Comment,
            post__id=self.kwargs['post_id'],
            pk=self.kwargs['comment_id'],
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.get_object().post.id})


class PostMixin:
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username_slug': self.request.user.username},
        )
