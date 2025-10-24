from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from apps.payments.models import OccasionalPayments
from apps.payments.serializers import OccasionalPaymentSerializer
from apps.units.models import Unit

# Create your views here.


class UnitPaymentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OccasionalPaymentSerializer

    def get_queryset(self):
        unit_id = self.kwargs.get("unit_id")
        return OccasionalPayments.objects.select_related("unit").filter(unit_id=unit_id)

    def perform_create(self, serializer):
        unit_id = self.kwargs.get("unit_id")
        unit = get_object_or_404(Unit, pk=unit_id)
        serializer.save(unit=unit)


class UnitPaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OccasionalPaymentSerializer

    def get_queryset(self):
        unit_id = self.kwargs.get("unit_id")
        return OccasionalPayments.objects.select_related("unit").filter(unit_id=unit_id)
