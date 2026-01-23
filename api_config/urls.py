from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.permissions import AllowAny

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("user.urls")),
    path("api/posts/", include("post.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
            url_name="schema"
        ),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
            url_name="schema"
        ),
        name="redoc",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
