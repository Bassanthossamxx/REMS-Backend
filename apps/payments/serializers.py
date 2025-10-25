from rest_framework import serializers

from apps.payments import utils as pay_utils
from apps.payments.models import OccasionalPayments, OwnerPayment


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


# --- Owner payout tracking (create) ---
class OwnerPaymentCreateSerializer(serializers.ModelSerializer):
    # Accept amount_paid in request and map to model's amount
    amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)

    class Meta:
        model = OwnerPayment
        fields = ["id", "owner", "amount_paid", "notes", "date"]
        read_only_fields = ("id", "owner", "date")

    def create(self, validated_data):
        owner = self.context["owner"]
        amount = validated_data.pop("amount_paid")
        notes = validated_data.get("notes")
        return OwnerPayment.objects.create(owner=owner, amount=amount, notes=notes)


# New: read serializer for payout history
class OwnerPaymentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerPayment
        fields = ["id", "owner", "amount", "notes", "date"]
        read_only_fields = fields


# --- Analytics serializers matching utils keys ---
class OwnerUnitBreakdownSerializer(serializers.Serializer):
    unit_id = serializers.IntegerField()
    unit_name = serializers.CharField()
    owner_percentage = serializers.DecimalField(max_digits=5, decimal_places=4)

    # Totals as provided by utils.calculate_owner_payment_summary per unit row
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)

    total_occasional = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_occasional_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)

    total_after_occasional = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_after_occasional_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)

    owner_total = serializers.DecimalField(max_digits=14, decimal_places=2)
    owner_total_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)


class OwnerPaymentSummarySerializer(serializers.Serializer):
    owner_id = serializers.IntegerField()
    owner_name = serializers.CharField()

    # Totals (naming aligned with utils)
    total_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)
    total = serializers.DecimalField(max_digits=14, decimal_places=2)

    total_occasional_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_occasional = serializers.DecimalField(max_digits=14, decimal_places=2)

    total_after_occasional_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_after_occasional = serializers.DecimalField(max_digits=14, decimal_places=2)

    owner_total_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)
    owner_total = serializers.DecimalField(max_digits=14, decimal_places=2)

    paid_to_owner_total = serializers.DecimalField(max_digits=14, decimal_places=2)
    still_need_to_pay = serializers.DecimalField(max_digits=14, decimal_places=2)

    units = OwnerUnitBreakdownSerializer(many=True)

    # New: embed payout history
    payments_history = OwnerPaymentReadSerializer(many=True, read_only=True)


class UnitPaymentSummarySerializer(serializers.Serializer):
    unit_id = serializers.IntegerField()
    unit_name = serializers.CharField()
    owner_id = serializers.IntegerField()
    owner_name = serializers.CharField()
    owner_percentage = serializers.DecimalField(max_digits=5, decimal_places=4)

    # Totals (naming aligned with utils)
    total_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)
    total = serializers.DecimalField(max_digits=14, decimal_places=2)

    total_occasional_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_occasional = serializers.DecimalField(max_digits=14, decimal_places=2)

    total_after_occasional_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_after_occasional = serializers.DecimalField(max_digits=14, decimal_places=2)

    company_total_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)
    company_total = serializers.DecimalField(max_digits=14, decimal_places=2)
