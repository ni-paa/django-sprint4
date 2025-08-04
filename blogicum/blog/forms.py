# blog/forms.py
from django import forms

from .models import Comment, Post, User


class CommentForm(forms.ModelForm):
    """Форма создания/редактирования комментария."""

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    """Форма создания/редактирования поста."""

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M',
                attrs={'type': 'datetime-local'},
            )
        }


class ProfileForm(forms.ModelForm):
    """Форма редактирования профиля."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
