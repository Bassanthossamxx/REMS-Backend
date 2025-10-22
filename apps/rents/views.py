from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from apps.rents.models import Rent
from apps.rents.serializers import RentSerializer

# Admin-only CRUD for rents
class RentViewSet(viewsets.ModelViewSet):
    queryset = Rent.objects.select_related("unit", "tenant").all().order_by("-created_at")
    serializer_class = RentSerializer
    permission_classes = [IsAdminUser]
    # Enable filtering by foreign keys using default DjangoFilterBackend
    filterset_fields = ["unit", "tenant"]

    def get_queryset(self):
        # Start from the base queryset
        qs = super().get_queryset()
        params = self.request.query_params

        # Support explicit aliases `unit_id` and `tenant_id` in addition to default `unit`/`tenant`
        unit_id = params.get("unit_id")
        tenant_id = params.get("tenant_id")

        # Apply filters if provided (AND semantics when both present)
        if unit_id:
            qs = qs.filter(unit_id=unit_id)
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)

        return qs
