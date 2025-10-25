from __future__ import annotations
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum, QuerySet
from apps.payments.models import OccasionalPayments


def unit_payments_summary(unit_id: int) -> dict:
    """
    Compute totals and last-month queryset for a given unit.
    Returns dict with keys:
      - total_occasional_payment: Decimal
      - total_occasional_payment_last_month: Decimal
      - last_month_qs: QuerySet[OccasionalPayments]
    """
    qs: QuerySet[OccasionalPayments] = OccasionalPayments.objects.filter(unit_id=unit_id)

    agg_all = qs.aggregate(total_all=Sum("amount"))
    total_all = agg_all.get("total_all") or Decimal("0.00")

    # Previous calendar month range
    today = date.today()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    last_month_qs = qs.filter(payment_date__gte=first_day_prev_month, payment_date__lte=last_day_prev_month)

    agg_last = last_month_qs.aggregate(total_last=Sum("amount"))
    total_last = agg_last.get("total_last") or Decimal("0.00")

    return {
        "total_occasional_payment": total_all,
        "total_occasional_payment_last_month": total_last,
        "last_month_qs": last_month_qs.order_by("id"),
    }
