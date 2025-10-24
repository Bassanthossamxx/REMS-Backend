from django.urls import path
from apps.payments.views import UnitPaymentListCreateView, UnitPaymentDetailView

urlpatterns = [
    path('payments/<int:unit_id>/', UnitPaymentListCreateView.as_view(), name='unit-payments-list-create'),
    path('payments/<int:unit_id>/<int:pk>/', UnitPaymentDetailView.as_view(), name='unit-payments-detail'),
]
