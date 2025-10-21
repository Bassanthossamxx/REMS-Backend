from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from apps.core.models import City, District

class CitySerializer(serializers.ModelSerializer):
    districts = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['id', 'name', 'created_at', 'updated_at', 'districts']

    def get_districts(self, obj):
        return obj.district_set.values_list('name', flat=True)

class DistrictSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = District
        fields = ['id', 'name', 'city', 'city_name', 'created_at', 'updated_at']

    def validate_city(self, value):
        if not value:
            raise serializers.ValidationError("City is required.")
        return value

class SuperUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)

        if not user or not user.is_superuser:
            raise AuthenticationFailed('Invalid credentials or not a superuser')

        return user
