from rest_framework import serializers
from rest_framework.serializers import ImageField
from apps.units.models import Unit, UnitImage
from apps.owners.models import Owner  # Assuming the Owner model is in apps.owners.models

class UnitListSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)
    current_tenant_name = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            "name",
            "location_text",
            "city_name",
            "district_name",
            "current_tenant_name",
            "price_per_day",
            "type",
            "status",
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
        fields = '__all__'  # Include all fields from the Unit model

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        unit = super().create(validated_data)

        for image in images:
            UnitImage.objects.create(unit=unit, image=image)

        return unit

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        unit = super().update(instance, validated_data)

        if images is not None:
            unit.images.all().delete()
            for image in images:
                UnitImage.objects.create(unit=unit, image=image)

        return unit

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['details'] = {
            'type': instance.type,  # Corrected from 'unit_type' to 'type'
            'bedrooms': instance.bedrooms,
            'bathrooms': instance.bathrooms,
            'area': instance.area
        }
        return representation

    def filter_queryset(self, queryset):
        unit_type = self.context['request'].query_params.get('type', None)
        if unit_type:
            queryset = queryset.filter(unit_type__iexact=unit_type)
        return queryset


class UnitImageSerializer(serializers.ModelSerializer):
    image = ImageField()

    class Meta:
        model = UnitImage
        fields = ['id', 'unit', 'image']
