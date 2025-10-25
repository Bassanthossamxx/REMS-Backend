from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import City, District
from apps.core.serializers import CitySerializer, DistrictSerializer

from .serializers import SuperUserLoginSerializer


class SuperUserLoginView(generics.GenericAPIView):
    serializer_class = SuperUserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Logged in successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return Response({"error": "Refresh token required"}, status=400)
        try:
            RefreshToken(token).blacklist()
            return Response({"message": "Logged out successfully"}, status=200)
        except TokenError as e:
            # Token is invalid, expired or already blacklisted
            return Response({"error": str(e)}, status=400)
        except Exception:
            return Response({"error": "Invalid token"}, status=400)


class CityViewSet(ModelViewSet):
    queryset = City.objects.prefetch_related("district_set").all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminUser]


class DistrictViewSet(ModelViewSet):
    queryset = District.objects.select_related("city").all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        if not serializer.validated_data.get("city"):
            raise serializers.ValidationError({"city": "City is required."})
        serializer.save()
