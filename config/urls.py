from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),

    # Google / allauth
    path("accounts/", include("allauth.urls")),

    # Обычная авторизация проекта
    path("auth/", include("accounts.urls")),

    # Распознавание
    path("recognize/", include("recognize.urls")),

    # Основные страницы
    path("", include("pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
