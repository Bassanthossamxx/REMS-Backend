from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tenants.views import TenantViewSet, ReviewViewSet

router = DefaultRouter()
# Important: register 'tenants/reviews' BEFORE 'tenants' to avoid shadowing by the tenant detail route
router.register(r'tenants/reviews', ReviewViewSet, basename='tenant-review')
router.register(r'tenants', TenantViewSet, basename='tenant')

urlpatterns = [
    path('', include(router.urls)),
]
