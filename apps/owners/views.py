from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from .models import Owner
from .serializers import OwnerSerializer


class OwnerListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    search_fields = ["full_name"]

    def get_queryset(self):
        return super().get_queryset().prefetch_related("units__city", "units__district", "units__images")


class OwnerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related("units__city", "units__district", "units__images")
