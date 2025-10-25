from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import Owner


class OwnerSerializer(serializers.ModelSerializer):
    units_count = serializers.SerializerMethodField(read_only=True)
    total_revenue = serializers.SerializerMethodField(read_only=True)
    monthly_revenue = serializers.SerializerMethodField(read_only=True)
    units = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Owner
        fields = "__all__"
        read_only_fields = (
            "date_joined",
            "updated_at",
        )

    def get_units_count(self, obj: Owner) -> int:
        return obj.units.count()

    def get_total_revenue(self, obj: Owner):
        # Sum of owner's share across all rents for this owner's units
        from apps.rents.models import Rent

        total = Decimal("0")
        qs = Rent.objects.filter(unit__owner=obj).select_related("unit")
        for rent in qs:
            share = (rent.total_amount * rent.unit.owner_percentage) / Decimal("100")
            total += share
        # Normalize to 2 decimal places like money
        return total.quantize(Decimal("0.01")) if total else Decimal("0.00")

    def get_monthly_revenue(self, obj: Owner):
        # Current month revenue (owner's share)
        from apps.rents.models import Rent

        now = timezone.now()
        total = Decimal("0")
        qs = Rent.objects.filter(unit__owner=obj, created_at__year=now.year, created_at__month=now.month).select_related("unit")
        for rent in qs:
            share = (rent.total_amount * rent.unit.owner_percentage) / Decimal("100")
            total += share
        return total.quantize(Decimal("0.01")) if total else Decimal("0.00")

    def get_units(self, obj: Owner):
        from apps.rents.models import Rent

        units = obj.units.all().select_related("city", "district")
        today = timezone.now().date()
        data = []
        for u in units:
            # Active rent if any, else latest rent
            rent_qs = Rent.objects.filter(unit=u).order_by("-rent_start")
            active_rent = rent_qs.filter(rent_start__lte=today, rent_end__gte=today).select_related("tenant").first()
            latest_rent = active_rent or rent_qs.select_related("tenant").first()

            tenant_name = None
            rent_price = None
            rent_start = None
            rent_end = None
            if latest_rent:
                tenant_name = latest_rent.tenant.full_name
                rent_price = latest_rent.total_amount
                rent_start = latest_rent.rent_start
                rent_end = latest_rent.rent_end

            # Cover photo: first image if exists
            first_image = u.images.first()
            cover_photo = None
            if first_image:
                try:
                    cover_photo = first_image.image.url
                except Exception:
                    cover_photo = str(first_image.image)

            data.append(
                {
                    "id": u.id,
                    "name": u.name,
                    "status": u.status,
                    "price_per_day": u.price_per_day,
                    "tenant_name": tenant_name,
                    "rent_price": rent_price,
                    "rent_start": rent_start,
                    "rent_end": rent_end,
                    "address": u.location_text,
                    "city_name": u.city.name if u.city_id else None,
                    "district_name": u.district.name if u.district_id else None,
                    "location_url": u.location_url,
                    "cover_photo": cover_photo,
                }
            )
        return data

    def validate_rate(self, value):
        # Ensure 1.0 <= rate <= 5.0, allow decimals like 2.5
        if value is None:
            return value
        if Decimal("1.0") <= Decimal(value) <= Decimal("5.0"):
            return value
        raise serializers.ValidationError("Rate must be between 1.0 and 5.0.")
