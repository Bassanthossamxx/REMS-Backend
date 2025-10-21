from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SuperUserLoginView, LogoutView, CityViewSet, DistrictViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'districts', DistrictViewSet, basename='district')

urlpatterns = [
    path("auth/login/", SuperUserLoginView.as_view(), name="superuser-login"),
    path("auth/logout/", LogoutView.as_view(), name="superuser-logout"),
    path("api/", include(router.urls)),
]
