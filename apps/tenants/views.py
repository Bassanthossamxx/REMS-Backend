from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import SearchFilter

from apps.tenants.models import Tenant
from apps.rents.models import Rent
from .serializers import TenantListSerializer
from apps.tenants.filters import TenantFilter


class TenantViewSet(ModelViewSet):
    queryset = Tenant.objects.all().prefetch_related(
        Prefetch(
            "rents",
            queryset=Rent.objects.select_related("unit", "tenant").order_by("-rent_start", "-id"),
        )
    )
    serializer_class = TenantListSerializer
    # Allow filtering by the existing TenantFilter and searching by tenant name or unit name
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["full_name", "rents__unit__name"]
    filterset_class = TenantFilter
    permission_classes = [IsAdminUser]

    # Ensure tenant status is fresh on every GET
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        items = page if page is not None else list(queryset)

        for tenant in items:
            try:
                tenant.update_status()
            except Exception:
                pass

        serializer = self.get_serializer(items, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.update_status()
        except Exception:
            pass
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
