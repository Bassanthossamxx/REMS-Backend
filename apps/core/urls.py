from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CityViewSet, DistrictViewSet, LogoutView, SuperUserLoginView

router = DefaultRouter()
router.register(r"cities", CityViewSet, basename="city")
router.register(r"districts", DistrictViewSet, basename="district")

urlpatterns = [
    path("auth/login/", SuperUserLoginView.as_view(), name="superuser-login"),
    path("auth/logout/", LogoutView.as_view(), name="superuser-logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),
]
