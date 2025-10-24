from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('api/', include('apps.tenants.urls')),
    path('api/', include('apps.units.urls')),  # Include units app URLs
    path('api/', include('apps.owners.urls')),  # Include owners app URLs
    path('api/', include('apps.rents.urls')),  # Include rents app URLs
    path('api/', include('apps.payments.urls')),  # Include payments app URLs

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
