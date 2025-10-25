from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .utils import get_home_metrics, get_stock_metrics, get_rental_metrics


class HomeMetricsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            days = int(request.query_params.get("days", 30))
        except (TypeError, ValueError):
            days = 30
        return Response(get_home_metrics(days=days))


class StockMetricsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(get_stock_metrics())


class RentalMetricsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(get_rental_metrics())
