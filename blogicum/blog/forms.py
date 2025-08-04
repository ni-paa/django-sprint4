# blog/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Comment, Post

User = get_user_model()


class CommentForm(forms.ModelForm):
    """Форма создания/редактирования комментария."""

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    """Форма создания/редактирования поста."""

    pub_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'}
        ),
        input_formats=[
            '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M',
            '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S'
        ]
    )

    class Meta:
        model = Post
        exclude = ('author',)


class SignUpForm(UserCreationForm):
    """Форма создания профиля."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
        )


class ProfileForm(UserChangeForm):
    """Форма редактирования профиля."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    password = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
