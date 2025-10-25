from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .models import Inventory
from .serializers import InventorySerializer


class InventoryViewSet(ModelViewSet):
    queryset = Inventory.objects.all().order_by("-created_at")
    serializer_class = InventorySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = [
        "category",
        "status",
    ]
    search_fields = [
        "name",
        "category",
        "supplier_name",
        "status",
    ]
