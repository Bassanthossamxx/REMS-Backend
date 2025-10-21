from django_filters import rest_framework as filters
from django.db.models import Q
from apps.tenants.models import Tenant

class TenantFilter(filters.FilterSet):
    full_name = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    phone = filters.CharFilter(lookup_expr='icontains')
    address = filters.CharFilter(lookup_expr='icontains')
    search = filters.CharFilter(method='filter_search')
    status = filters.CharFilter(method='filter_status')

    class Meta:
        model = Tenant
        fields = ['full_name', 'email', 'phone', 'address', 'search', 'status']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value) |
            Q(rents__unit__name__icontains=value)
        ).distinct()

    def filter_status(self, queryset, name, value):
        today = timezone.now().date()

        def get_status_filter(rent):
            if rent.payment_status == Rent.PaymentStatus.PAID and rent.rent_end < today:
                return "completed"
            elif rent.rent_start <= today <= rent.rent_end:
                return "active"
            elif rent.rent_end < today and rent.payment_status != Rent.PaymentStatus.PAID:
                return "overdue"
            return "pending"

        return queryset.filter(
            rents__in=[rent for rent in Rent.objects.all() if get_status_filter(rent) == value]
        )
