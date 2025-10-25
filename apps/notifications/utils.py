from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from apps.inventory.models import Inventory
from apps.units.models import Unit

from .models import Notification

LEASE_MESSAGE_TPL = "Lease for unit '{name}' will end on {end}"
LOW_STOCK_TPL = "Item '{name}' only has {qty} units remaining"
OUT_OF_STOCK_TPL = "Item '{name}' is out of stock"


def _create_notification_once(message: str) -> None:
    Notification.objects.get_or_create(message=message)


def check_and_create_notifications() -> None:
    """
    - Find all units whose lease_end is within 2 months from today and create notifications.
    - Find inventory items with Low Stock or Out of Stock and create notifications.
    - Delete notifications older than 6 months (monthly cleanup implied by calling this periodically).
    Uses get_or_create() to avoid duplicates.
    """
    today = timezone.now().date()
    in_two_months = today + timedelta(days=60)

    # Units with lease ending within next 2 months
    units_qs = Unit.objects.filter(lease_end__gte=today, lease_end__lte=in_two_months)
    for unit in units_qs.only("name", "lease_end"):
        msg = LEASE_MESSAGE_TPL.format(name=unit.name, end=unit.lease_end.isoformat())
        _create_notification_once(msg)

    # Inventory: low stock or out of stock
    # Status is set automatically by Inventory.save()
    low_or_out_qs = Inventory.objects.filter(Q(status="Low Stock") | Q(status="Out of Stock"))
    for item in low_or_out_qs.only("name", "quantity", "status"):
        if item.quantity == 0:
            msg = OUT_OF_STOCK_TPL.format(name=item.name)
        else:
            msg = LOW_STOCK_TPL.format(name=item.name, qty=item.quantity)
        _create_notification_once(msg)

    # Cleanup: delete notifications older than 6 months
    six_months_ago = timezone.now() - timedelta(days=6 * 30)
    Notification.objects.filter(created_at__lt=six_months_ago).delete()
