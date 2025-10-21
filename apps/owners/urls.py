from django.urls import path
from .views import OwnerListCreateView

urlpatterns = [
    path('owners/', OwnerListCreateView.as_view(), name='owner-list-create'),
]
