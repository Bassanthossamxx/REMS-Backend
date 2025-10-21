from django_filters import rest_framework as filters
from django.utils.dateparse import parse_date
from apps.units.models import Unit
from django.db.models import Q

class UnitFilter(filters.FilterSet):
    from_date = filters.CharFilter(method='filter_from_date', label='From Date')
    to_date = filters.CharFilter(method='filter_to_date', label='To Date')

    class Meta:
        model = Unit
        fields = ['type', 'city', 'district', 'status']

    def filter_from_date(self, queryset, name, value):
        from_date_parsed = parse_date(value)
        if from_date_parsed:
            return queryset.filter(
                Q(rents__rent_start__gte=from_date_parsed) | Q(rents__isnull=True)
            ).distinct()
        return queryset

    def filter_to_date(self, queryset, name, value):
        to_date_parsed = parse_date(value)
        if to_date_parsed:
            return queryset.filter(
                Q(rents__rent_end__lte=to_date_parsed) | Q(rents__isnull=True)
            ).distinct()
        return queryset
