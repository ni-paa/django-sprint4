# blog/admin.py
from django.contrib import admin

# Из модуля models импортируем модель Category...
from .models import Category, Comment, Location, Post

# Этот вариант сработает для всех моделей приложения.
admin.site.empty_value_display = 'Не задано'
# Вместо пустого значения в админке будет отображена строка "Не задано".

admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Location)
admin.site.register(Post)
