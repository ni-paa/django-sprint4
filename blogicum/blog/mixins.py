from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail', post_id=self.kwargs['post_id'])
