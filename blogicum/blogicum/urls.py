from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.urls import include, path, reverse_lazy

from blog import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', views.CreateView.as_view(
        template_name='registration/registration_form.html',
        form_class=UserCreationForm,
        success_url=reverse_lazy('blog:index')
    ),
        name='registration'),
    path('', include('blog.urls', namespace='blog')),
]

# Подключаем панель дебага
# if settings.DEBUG:
#     urlpatterns += [
#         path("__debug__/", include("debug_toolbar.urls")),
#     ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
