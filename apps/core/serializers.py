from rest_framework import serializers
from django.contrib.auth import authenticate

class SuperUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data.get("email"), password=data.get("password"))
        if not user or not user.is_superuser:
            raise serializers.ValidationError("Invalid credentials or not a superuser.")
        return user
