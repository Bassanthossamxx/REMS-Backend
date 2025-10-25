from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("dashboard/", include("apps.dashboard.urls")),  # Include
    path("api/", include("apps.tenants.urls")),
    path("api/", include("apps.units.urls")),  # Include units app URLs
    path("api/", include("apps.owners.urls")),  # Include owners app URLs
    path("api/", include("apps.rents.urls")),  # Include rents app URLs
    path("api/", include("apps.payments.urls")),  # Include payments app URLs
    path("api/", include("apps.inventory.urls")),  # Include inventory app URLs
    path("api/", include("apps.notifications.urls")),  # Include notifications app URLs
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
