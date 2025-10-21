from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from apps.tenants.models import Tenant
from apps.rents.models import Rent
from .serializers import TenantListSerializer
from apps.tenants.filters import TenantFilter


class TenantViewSet(ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TenantFilter
    permission_classes = [IsAdminUser]
