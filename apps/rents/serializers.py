from rest_framework import serializers
from django.utils import timezone
from apps.rents.models import Rent
from config.choices import Status

class RentSerializer(serializers.ModelSerializer):
    # Read-only, computed fields
    unit_name = serializers.SerializerMethodField(read_only=True)
    unit_type = serializers.SerializerMethodField(read_only=True)
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
            "unit_name", "unit_type",
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
        is_create = instance is None

        # Resolve current values considering partial updates
        unit = attrs.get("unit") or (instance.unit if instance else None)
        tenant = attrs.get("tenant") or (instance.tenant if instance else None)
        rent_start = attrs.get("rent_start") or (instance.rent_start if instance else None)
        rent_end = attrs.get("rent_end") or (instance.rent_end if instance else None)

        # Basic date order check
        if rent_start and rent_end and rent_end < rent_start:
            raise serializers.ValidationError({
                "rent_end": "Rent end date cannot be earlier than rent start date.",
            })

        # Determine if overlap-sensitive fields changed on update
        overlap_fields = ("unit", "tenant", "rent_start", "rent_end")
        changed_overlap_fields = False
        if not is_create:
            for f in overlap_fields:
                if f in attrs:
                    old_val = getattr(instance, f)
                    new_val = attrs.get(f, old_val)
                    if old_val != new_val:
                        changed_overlap_fields = True
                        break

        # Run overlap checks on create or when overlap-affecting fields change
        should_check_overlap = is_create or changed_overlap_fields
        if should_check_overlap and unit and tenant and rent_start and rent_end:
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
