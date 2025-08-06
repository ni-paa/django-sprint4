# blog/forms.py
from django import forms
from django.contrib.auth.forms import UserChangeForm

from .models import Comment, Post, User


class CommentForm(forms.ModelForm):
    """Форма создания/редактирования комментария."""

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    """Форма создания/редактирования публикаций."""

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M',
                attrs={'type': 'datetime-local'},
            )
        }


class ProfileForm(UserChangeForm):
    """Форма редактирования профиля пользователя."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
