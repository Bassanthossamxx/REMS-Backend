from rest_framework import serializers
from django.utils import timezone
from apps.tenants.models import Tenant, Review
from apps.rents.models import Rent
from apps.rents.serializers import RentSerializer


class ReviewSerializer(serializers.ModelSerializer):
    # Expose formatted date as yyyy-mm-dd
    date = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "tenant",
            "comment",
            "rate",
            "date",
        ]
        read_only_fields = ["id", "date"]

    def get_date(self, obj):
        return obj.created_at.date().isoformat()


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
            "status",     # tenant lifecycle status
            "rent_info",  # nearest/current rent
        ]

    def get_rent_info(self, obj):
        """Return the nearest rent to today for this tenant as a serialized dict.
        Preference order: active today > next upcoming > latest past. None if no rents.
        Uses prefetched rents when available to minimize queries.
        """
        today = timezone.now().date()
        rents_qs = getattr(obj, "rents", None)
        if rents_qs is None:
            # Fallback if not prefetched
            rents_qs = Rent.objects.filter(tenant=obj).select_related("unit", "tenant")
        else:
            rents_qs = rents_qs.all()  # ensure queryset

        active = None
        upcoming = None
        latest_past = None
        upcoming_min_start = None
        latest_past_max_end = None

        # Single pass over rents
        for r in rents_qs:
            if r.rent_start <= today <= r.rent_end:
                active = r
                break  # active wins immediately
            if r.rent_start > today:
                if upcoming is None or r.rent_start < upcoming_min_start:
                    upcoming = r
                    upcoming_min_start = r.rent_start
            elif r.rent_end < today:
                if latest_past is None or r.rent_end > latest_past_max_end:
                    latest_past = r
                    latest_past_max_end = r.rent_end

        target = active or upcoming or latest_past
        return RentSerializer(target).data if target else None


class TenantDetailSerializer(TenantListSerializer):
    rents = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta(TenantListSerializer.Meta):
        fields = TenantListSerializer.Meta.fields + [
            "rents",      # full rent history for this tenant
            "reviews",    # list of reviews
        ]

    def get_rents(self, obj):
        """Return all rents for this tenant as a list of serialized dicts, newest first."""
        rents_qs = getattr(obj, "rents", None)
        if rents_qs is None:
            rents_qs = Rent.objects.filter(tenant=obj).select_related("unit", "tenant").order_by("-rent_start", "-id")
        else:
            rents_qs = rents_qs.all()
        return RentSerializer(rents_qs, many=True).data

    def get_reviews(self, obj):
        reviews_qs = getattr(obj, "reviews", None)
        if reviews_qs is None:
            reviews_qs = obj.reviews.all()
        else:
            reviews_qs = reviews_qs.all()
        # Return minimal shape per requirements
        return [
            {
                "comment": r.comment,
                "rate": float(r.rate) if r.rate is not None else None,
                "date": r.created_at.date().isoformat(),
            }
            for r in reviews_qs
        ]
