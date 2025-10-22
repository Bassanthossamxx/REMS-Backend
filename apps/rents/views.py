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
