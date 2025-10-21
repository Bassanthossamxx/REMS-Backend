from rest_framework import serializers
from django.utils import timezone
from apps.tenants.models import Tenant
from apps.rents.models import Rent


class TenantListSerializer(serializers.ModelSerializer):
    rent_info = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "rate",
            "address",
            "rent_info",
        ]

    def get_rent_info(self, obj):
        today = timezone.now().date()
        latest_rent = (
            Rent.objects.filter(tenant=obj)
            .select_related("unit")
            .order_by("-rent_start")
            .first()
        )
        if not latest_rent:
            return None

        if latest_rent.payment_status == Rent.PaymentStatus.PAID and latest_rent.rent_end < today:
            rent_status = "completed"
        elif latest_rent.rent_start <= today <= latest_rent.rent_end:
            rent_status = "active"
        elif latest_rent.rent_end < today and latest_rent.payment_status != Rent.PaymentStatus.PAID:
            rent_status = "overdue"
        else:
            rent_status = "pending"

        return {
            "unit_name": latest_rent.unit.name,
            "rent_start": latest_rent.rent_start,
            "rent_end": latest_rent.rent_end,
            "total_amount": latest_rent.total_amount,
            "status": rent_status,
            "payment_status": latest_rent.payment_status,
        }
