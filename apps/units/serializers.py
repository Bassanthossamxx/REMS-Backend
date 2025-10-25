from rest_framework import serializers
from rest_framework.serializers import ImageField
from apps.units.models import Unit, UnitImage
from apps.owners.models import Owner
from apps.payments import utils as pay_utils
from apps.payments.serializers import OccasionalPaymentSimpleSerializer


class UnitListSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)
    current_tenant_name = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            "id",
            "name",
            "location_text",
            "city_name",
            "district_name",
            "current_tenant_name",
            "price_per_day",
            "type",
            "status",
            "lease_start",
            "lease_end",
        ]
        read_only_fields = fields

    def get_current_tenant_name(self, obj: Unit):
        ct = getattr(obj, "current_tenant", None)
        return (ct or {}).get("name") if ct else None


class UnitSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    owner = serializers.PrimaryKeyRelatedField(queryset=Owner.objects.all())
    bedrooms = serializers.IntegerField(required=True)
    bathrooms = serializers.IntegerField(required=True)
    area = serializers.IntegerField(required=True)

    class Meta:
        model = Unit
        fields = "__all__"

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        unit = super().create(validated_data)

        for image in images:
            UnitImage.objects.create(unit=unit, image=image)

        unit.update_status()
        return unit

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        unit = super().update(instance, validated_data)

        if images is not None:
            instance.images.all().delete()
            for image in images:
                UnitImage.objects.create(unit=unit, image=image)

        unit.update_status()
        return unit

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["details"] = {
            "type": instance.type,
            "bedrooms": instance.bedrooms,
            "bathrooms": instance.bathrooms,
            "area": instance.area,
        }
        # Include related images
        representation["images"] = [
            image.image.url for image in instance.images.all()
        ]

        # Add payments summary via utils (occasional payments quick summary)
        try:
            summary = pay_utils.unit_payments_summary(instance.id)
            representation["payments_summary"] = {
                "total_occasional_payment": f"{summary['total_occasional_payment']:.2f}",
                "total_occasional_payment_last_month": f"{summary['total_occasional_payment_last_month']:.2f}",
                "last_month_payments": OccasionalPaymentSimpleSerializer(
                    summary["last_month_qs"], many=True
                ).data,
            }
        except Exception:
            representation["payments_summary"] = {
                "total_occasional_payment": "0.00",
                "total_occasional_payment_last_month": "0.00",
                "last_month_payments": [],
            }

        # Embed full unit payment analytics (rent + deductions + shares) by calling the existing util
        representation["unit_payment_summary"] = pay_utils.calculate_unit_payment_summary(instance.id)

        return representation


class UnitImageSerializer(serializers.ModelSerializer):
    image = ImageField()

    class Meta:
        model = UnitImage
        fields = ["id", "unit", "image"]
