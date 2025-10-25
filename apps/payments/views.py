from django.shortcuts import render, get_object_or_404
from rest_framework import generics, views, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.utils import timezone
from datetime import date, datetime
from decimal import Decimal
from django.db.models import Sum, F

from apps.payments.models import OccasionalPayments, OwnerPayment
from apps.payments.serializers import (
    OccasionalPaymentSerializer,
    OccasionalPaymentWithSummarySerializer,
    OwnerPaymentCreateSerializer,
    OwnerPaymentSummarySerializer,
    UnitPaymentSummarySerializer,
)
from apps.payments import utils as pay_utils
from apps.units.models import Unit
from apps.owners.models import Owner
from apps.rents.models import Rent



class UnitPaymentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OccasionalPaymentWithSummarySerializer
        return OccasionalPaymentSerializer

    def get_queryset(self):
        unit_id = self.kwargs.get("unit_id")
        return OccasionalPayments.objects.select_related("unit").filter(unit_id=unit_id)

    def perform_create(self, serializer):
        unit_id = self.kwargs.get("unit_id")
        unit = get_object_or_404(Unit, pk=unit_id)
        serializer.save(unit=unit)

    def list(self, request, *args, **kwargs):
        # Ensure unit exists, otherwise return 404
        unit_id = self.kwargs.get("unit_id")
        get_object_or_404(Unit, pk=unit_id)
        return super().list(request, *args, **kwargs)


class UnitPaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OccasionalPaymentSerializer

    def get_queryset(self):
        unit_id = self.kwargs.get("unit_id")
        return OccasionalPayments.objects.select_related("unit").filter(unit_id=unit_id)


# --- Analytics Endpoints ---
class OwnerPaymentSummaryView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, owner_id: int):
        # Calculate via utils for clarity and reuse
        summary = pay_utils.calculate_owner_payment_summary(owner_id)
        serializer = OwnerPaymentSummarySerializer(summary)
        return Response(serializer.data)


class OwnerPaymentCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OwnerPaymentCreateSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        owner = get_object_or_404(Owner, pk=self.kwargs.get("owner_id"))
        ctx.update({"owner": owner})
        return ctx


class UnitPaymentSummaryView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, unit_id: int):
        # Calculate via utils for clarity and reuse
        summary = pay_utils.calculate_unit_payment_summary(unit_id)
        serializer = UnitPaymentSummarySerializer(summary)
        return Response(serializer.data)


class CompanyPaymentSummaryView(views.APIView):
    """
    Company-side summary: what remains for the company after paying owners and occasional deductions.
    Equivalent to /api/payments/all/payments/me
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        summary = pay_utils.calculate_company_payment_summary(unit_id=None)
        return Response(summary)


class CompanyPaymentSummaryPerUnitView(views.APIView):
    """
    Company-side summary for a specific unit: /api/payments/all/payments/me/<unit_id>/
    """
    permission_classes = [IsAdminUser]

    def get(self, request, unit_id: int):
        # Ensure unit exists
        get_object_or_404(Unit, pk=unit_id)
        summary = pay_utils.calculate_company_payment_summary(unit_id=unit_id)
        return Response(summary)

