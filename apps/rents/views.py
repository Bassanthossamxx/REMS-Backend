from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
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

    # --- Ensure fresh computed data on every GET ---
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        items = page if page is not None else list(queryset)

        # Recompute status and cascade updates by saving each item
        for rent in items:
            try:
                rent.save()
            except Exception:
                # Avoid breaking the response if a single item fails to update
                pass

        serializer = self.get_serializer(items, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.save()
        except Exception:
            pass
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
