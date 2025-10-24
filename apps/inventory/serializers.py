from rest_framework import serializers
from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"
        read_only_fields = (
            "id",
            "total_value",
            "status",
            "created_at",
            "updated_at",
        )
