from rest_framework import serializers
from apps.payments.models import OccasionalPayments
from datetime import date
from apps.payments import utils as pay_utils


class OccasionalPaymentSimpleSerializer(serializers.ModelSerializer):
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
        read_only_fields = fields


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


class OccasionalPaymentWithSummarySerializer(OccasionalPaymentSerializer):
    total_occasional_payment = serializers.SerializerMethodField(read_only=True)
    total_occasional_payment_last_month = serializers.SerializerMethodField(read_only=True)

    class Meta(OccasionalPaymentSerializer.Meta):
        fields = OccasionalPaymentSerializer.Meta.fields + [
            "total_occasional_payment",
            "total_occasional_payment_last_month",
        ]
        read_only_fields = OccasionalPaymentSerializer.Meta.read_only_fields

    # Simple per-instance cache to avoid recalculation per item in the same request
    _unit_summary_cache = None

    def _get_summary(self, unit_id):
        if self._unit_summary_cache is None:
            self._unit_summary_cache = {}
        if unit_id not in self._unit_summary_cache:
            self._unit_summary_cache[unit_id] = pay_utils.unit_payments_summary(unit_id)
        return self._unit_summary_cache[unit_id]

    def get_total_occasional_payment(self, obj: OccasionalPayments):
        summary = self._get_summary(obj.unit_id)
        return f"{summary['total_occasional_payment']:.2f}"

    def get_total_occasional_payment_last_month(self, obj: OccasionalPayments):
        summary = self._get_summary(obj.unit_id)
        return f"{summary['total_occasional_payment_last_month']:.2f}"
