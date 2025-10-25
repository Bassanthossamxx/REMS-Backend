from django.urls import path
from .views import HomeMetricsView, StockMetricsView, RentalMetricsView

urlpatterns = [
    path('home/metrics/', HomeMetricsView.as_view(), name='home_metrics'),
    path('stock/metrics/', StockMetricsView.as_view(), name='stock_metrics'),
    path('rental/metrics/', RentalMetricsView.as_view(), name='rental_metrics'),
]
