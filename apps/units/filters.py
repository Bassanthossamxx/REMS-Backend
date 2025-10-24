from django_filters import rest_framework as filters
from django.utils.dateparse import parse_date
from django.db.models import Q
from apps.units.models import Unit


class UnitFilter(filters.FilterSet):
    """
    FilterSet for Unit list filtering.
    Supports:
    - Filtering by type, city, district, and status.
    - Filtering by rent date window (from_date/to_date)
    - Filtering by owner lease_start and lease_end (lease_from / lease_to)
    """
    from_date = filters.CharFilter(method='filter_from_date', label='From Date')
    to_date = filters.CharFilter(method='filter_to_date', label='To Date')
    lease_from = filters.DateFilter(field_name='lease_start', lookup_expr='gte')
    lease_to = filters.DateFilter(field_name='lease_end', lookup_expr='lte')

    class Meta:
        model = Unit
        fields = ['type', 'city', 'district', 'status', 'lease_from', 'lease_to']

    def filter_from_date(self, queryset, name, value):
        """
        Show units that are AVAILABLE from a specific date.
        If any rent overlaps that date range → exclude it (since it's occupied).
        """
        from_date_parsed = parse_date(value)
        if not from_date_parsed:
            return queryset

        # Include units with no rent or with rents ending before that date
        return queryset.exclude(
            rents__rent_end__gte=from_date_parsed,
            rents__rent_start__lte=from_date_parsed
        ).distinct()

    def filter_to_date(self, queryset, name, value):
        """
        Show units that are AVAILABLE up to a specific date.
        """
        to_date_parsed = parse_date(value)
        if not to_date_parsed:
            return queryset

        return queryset.exclude(
            rents__rent_start__lte=to_date_parsed,
            rents__rent_end__gte=to_date_parsed
        ).distinct()
