from django.urls import path

from .views import OwnerListCreateView, OwnerRetrieveUpdateDestroyView

urlpatterns = [
    path("owners/", OwnerListCreateView.as_view(), name="owner-list-create"),
    path(
        "owners/<int:pk>/",
        OwnerRetrieveUpdateDestroyView.as_view(),
        name="owner-detail",
    ),
]
