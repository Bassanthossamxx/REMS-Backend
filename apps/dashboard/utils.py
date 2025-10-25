from datetime import timedelta

from django.db.models import Sum, F, Value, DecimalField, ExpressionWrapper
from django.utils import timezone

from apps.inventory.models import Inventory
from apps.rents.models import Rent
from apps.units.models import Unit
from apps.tenants.models import Tenant
from config.choices import Status, PaymentStatus


def get_home_metrics(days: int = 30) -> dict:
    """
    Compute dashboard home metrics.
    - total_units: total units in the system (snapshot)
    - total_units_occupied: units currently occupied (snapshot)
    - total_revenue: company revenue from all PAID rents (overall)
    - pending_payments: sum of total_amount for all PENDING rents (overall)
    - new_tenants: tenants created within the last `days`
    """
    now = timezone.now()
    since = now - timedelta(days=days)

    # Snapshot: totals
    total_units = Unit.objects.count()
    total_units_occupied = Unit.objects.filter(status=Status.OCCUPIED).count()

    # Company revenue (overall) = sum(total_amount * (1 - owner_percentage/100)) over all PAID rents
    company_share_expr = ExpressionWrapper(
        F("total_amount") * (Value(1) - (F("unit__owner_percentage") / Value(100))),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    company_revenue_sum = (
        Rent.objects.filter(payment_status=PaymentStatus.PAID).aggregate(total=Sum(company_share_expr))["total"]
        or 0
    )

    # Pending rents sum (overall)
    pending_sum = (
        Rent.objects.filter(payment_status=PaymentStatus.PENDING).aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    # New tenants created in the last window only
    new_tenants = Tenant.objects.filter(created_at__gte=since).count()

    return {
        "total_units": total_units,
        "total_units_occupied": total_units_occupied,
        "total_revenue": float(company_revenue_sum),
        "pending_payments": float(pending_sum),
        "new_tenants": new_tenants,
    }


def get_stock_metrics() -> dict:
    """
    Inventory stock metrics.
    - total_items: total items posted in inventory
    - in_stock_items: items with status "In Stock"
    - out_of_stock_items: items with status "Out of Stock"
    - low_stock_items: items with status "Low Stock"
    """
    total_items_posted = Inventory.objects.count()
    in_stock_items = Inventory.objects.filter(status="In Stock").count()
    out_of_stock_items = Inventory.objects.filter(status="Out of Stock").count()
    low_stock_items = Inventory.objects.filter(status="Low Stock").count()

    return {
        "total_items": total_items_posted,
        "in_stock_items": in_stock_items,
        "out_of_stock_items": out_of_stock_items,
        "low_stock_items": low_stock_items,
    }


def get_rental_metrics() -> dict:
    """
    Rental management metrics.
    - total_collected: sum of total_amount for paid rents
    - pending: sum for pending rents
    - overdue: sum for overdue rents
    """
    total_collected_sum = (
        Rent.objects.filter(payment_status=PaymentStatus.PAID).aggregate(total=Sum("total_amount"))["total"] or 0
    )
    pending_sum = (
        Rent.objects.filter(payment_status=PaymentStatus.PENDING).aggregate(total=Sum("total_amount"))["total"] or 0
    )
    overdue_sum = (
        Rent.objects.filter(payment_status=PaymentStatus.OVERDUE).aggregate(total=Sum("total_amount"))["total"] or 0
    )

    return {
        "total_collected": float(total_collected_sum),
        "pending": float(pending_sum),
        "overdue": float(overdue_sum),
    }
