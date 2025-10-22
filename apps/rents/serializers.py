from rest_framework import serializers
from apps.rents.models import Rent

class RentSerializer(serializers.ModelSerializer):
    # Read-only, computed fields
    unit_name = serializers.SerializerMethodField(read_only=True)
    unit_type = serializers.SerializerMethodField(read_only=True)
    unit_type_value = serializers.SerializerMethodField(read_only=True)
    tenant_name = serializers.SerializerMethodField(read_only=True)
    tenant_email = serializers.SerializerMethodField(read_only=True)
    tenant_phone = serializers.SerializerMethodField(read_only=True)
    duration = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Rent
        fields = [
            # model fields
            "id", "unit", "tenant", "rent_start", "rent_end", "total_amount",
            "payment_status", "payment_method", "payment_date", "status",
            "notes", "attachment", "created_at",
            # computed fields
            "unit_name", "unit_type", "unit_type_value",
            "tenant_name", "tenant_email", "tenant_phone",
            "duration",
        ]
        extra_kwargs = {
            "tenant": {"required": True, "allow_null": False},
            "unit": {"required": True, "allow_null": False},
        }

    # --- Validators ---
    def validate(self, attrs):
        rent_start = attrs.get("rent_start") or getattr(self.instance, "rent_start", None)
        rent_end = attrs.get("rent_end") or getattr(self.instance, "rent_end", None)
        if rent_start and rent_end and rent_end < rent_start:
            raise serializers.ValidationError({
                "rent_end": "Rent end date cannot be earlier than rent start date.",
            })
        return attrs

    # --- Computed fields ---
    def get_unit_name(self, obj):
        return getattr(obj.unit, "name", None)

    def get_unit_type(self, obj):
        try:
            return obj.unit.get_type_display()
        except Exception:
            return getattr(obj.unit, "type", None)

    def get_unit_type_value(self, obj):
        return getattr(obj.unit, "type", None)

    def get_tenant_name(self, obj):
        return getattr(obj.tenant, "full_name", None)

    def get_tenant_email(self, obj):
        return getattr(obj.tenant, "email", None)

    def get_tenant_phone(self, obj):
        return getattr(obj.tenant, "phone", None)

    def get_duration(self, obj):
        start = getattr(obj, "rent_start", None)
        end = getattr(obj, "rent_end", None)
        if not start or not end:
            return None
        days = max((end - start).days, 0)
        if days < 30:
            return f"{days} day" + ("s" if days != 1 else "")
        months = days // 30
        rem = days % 30
        month_str = f"{months} month" + ("s" if months != 1 else "")
        if rem:
            day_str = f"{rem} day" + ("s" if rem != 1 else "")
            return f"{month_str} {day_str}"
        return month_str
