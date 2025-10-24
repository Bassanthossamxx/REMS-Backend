from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryViewSet

router = DefaultRouter()
router.register(r'stock', InventoryViewSet, basename='stock')

urlpatterns = [
    path('', include(router.urls)),
]
