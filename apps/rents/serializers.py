from rest_framework import serializers
from django.utils import timezone
from apps.rents.models import Rent
from config.choices import Status

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
            "payment_status": {"required": True, "allow_null": False},
            "payment_method": {"required": True, "allow_null": False},
            "payment_date": {"required": True, "allow_null": False},
        }

    # --- Validators ---
    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        unit = attrs.get("unit") or getattr(instance, "unit", None)
        tenant = attrs.get("tenant") or getattr(instance, "tenant", None)
        rent_start = attrs.get("rent_start") or getattr(instance, "rent_start", None)
        rent_end = attrs.get("rent_end") or getattr(instance, "rent_end", None)

        # Basic date order check
        if rent_start and rent_end and rent_end < rent_start:
            raise serializers.ValidationError({
                "rent_end": "Rent end date cannot be earlier than rent start date.",
            })

        # Overlap checks only when we have unit, tenant, and both dates
        if unit and tenant and rent_start and rent_end:
            qs = Rent.objects.all()
            if instance and instance.pk:
                qs = qs.exclude(pk=instance.pk)

            # 1) Unit can't have two rents that overlap
            if qs.filter(unit=unit, rent_start__lte=rent_end, rent_end__gte=rent_start).exists():
                raise serializers.ValidationError({
                    "unit": "This unit already has a rent overlapping with the selected dates.",
                })

            # 2) Tenant can't rent more than one unit at the same time
            if qs.filter(tenant=tenant, rent_start__lte=rent_end, rent_end__gte=rent_start).exists():
                raise serializers.ValidationError({
                    "tenant": "This tenant already has another rent overlapping with the selected dates.",
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
