from django.urls import path
from .views import SuperUserLoginView, LogoutView

urlpatterns = [
    path("login/", SuperUserLoginView.as_view(), name="superuser-login"),
    path("logout/", LogoutView.as_view(), name="superuser-logout"),
]
