from django.urls import path
from apps.payments.views import (
    UnitPaymentListCreateView,
    UnitPaymentDetailView,
    OwnerPaymentSummaryView,
    OwnerPaymentCreateView,
    UnitPaymentSummaryView,
    CompanyPaymentSummaryView,
    CompanyPaymentSummaryPerUnitView,
)

urlpatterns = [
    # Occasional payments CRUD per unit
    path('payments/<int:unit_id>/', UnitPaymentListCreateView.as_view(), name='unit-payments-list-create'),
    path('payments/<int:unit_id>/<int:pk>/', UnitPaymentDetailView.as_view(), name='unit-payments-detail'),

    # Analytics and owner payouts
    path('payments/all/owner/<int:owner_id>/', OwnerPaymentSummaryView.as_view(), name='owner-payments-summary'),
    path('payments/owner/<int:owner_id>/pay/', OwnerPaymentCreateView.as_view(), name='owner-payments-create'),
    path('payments/all/unit/<int:unit_id>/', UnitPaymentSummaryView.as_view(), name='unit-payments-summary'),

    # Company shares ("me")
    path('payments/all/payments/me/', CompanyPaymentSummaryView.as_view(), name='company-payments-summary'),
    path('payments/all/payments/me/<int:unit_id>/', CompanyPaymentSummaryPerUnitView.as_view(), name='company-payments-summary-unit'),
]
