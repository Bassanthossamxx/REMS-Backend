from rest_framework import serializers
from apps.payments.models import OccasionalPayments
from datetime import date


class OccasionalPaymentSerializer(serializers.ModelSerializer):


    class Meta:
        model = OccasionalPayments
        fields = [
            "id",
            "unit",
            "category",
            "amount",
            "payment_method",
            "payment_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at", "unit")
        extra_kwargs = {
            "category": {"required": True},
            "amount": {"required": True},
            "payment_method": {"required": True},
        }
