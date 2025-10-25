from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict

from django.db.models import QuerySet, Sum
from django.utils import timezone

from apps.owners.models import Owner
from apps.payments.models import OccasionalPayments, OwnerPayment
from apps.rents.models import Rent
from apps.units.models import Unit

# Common Decimal quantization constants (no behavior change)
TWO_PLACES = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")


def start_of_current_month_datetime() -> datetime:
    """Return timezone-aware datetime for the first moment of the current month."""
    first_day = date.today().replace(day=1)
    return timezone.make_aware(datetime.combine(first_day, datetime.min.time()))


def start_of_current_month_date() -> date:
    """Return date for the first day of the current month."""
    return date.today().replace(day=1)


def unit_payments_summary(unit_id: int) -> dict:
    """
    Existing helper retained: totals for occasional payments only.
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


# --- Analytics helpers ---


def calculate_owner_payment_summary(owner_id: int) -> dict:
    """
    Build per-owner payment summary.
    Payload keys (unchanged):
      owner_id, owner_name, total_this_month, total, total_occasional_this_month,
      total_occasional, total_after_occasional_this_month, total_after_occasional,
      owner_total_this_month, owner_total, paid_to_owner_total, still_need_to_pay, units
    """
    owner = Owner.objects.get(pk=owner_id)
    start_dt = start_of_current_month_datetime()
    start_d = start_of_current_month_date()

    units_qs = Unit.objects.filter(owner=owner).only("id", "name", "owner_percentage")
    unit_ids = list(units_qs.values_list("id", flat=True))

    # Totals before (rent) and occasional
    total_before_all_time = Rent.objects.filter(unit_id__in=unit_ids).aggregate(total=Sum("total_amount")).get("total") or Decimal("0.00")
    total_before_this_month = Rent.objects.filter(unit_id__in=unit_ids, payment_date__gte=start_dt).aggregate(total=Sum("total_amount")).get("total") or Decimal("0.00")

    total_occasional_all_time = OccasionalPayments.objects.filter(unit_id__in=unit_ids).aggregate(total=Sum("amount")).get("total") or Decimal("0.00")
    total_occasional_this_month = OccasionalPayments.objects.filter(unit_id__in=unit_ids, payment_date__gte=start_d).aggregate(total=Sum("amount")).get("total") or Decimal("0.00")

    total_after_all_time = total_before_all_time - total_occasional_all_time
    total_after_this_month = total_before_this_month - total_occasional_this_month

    # Per-unit grouped aggregates (all-time and this month) for detailed breakdown
    rents_by_unit_all = {uid: amt or Decimal("0.00") for uid, amt in (Rent.objects.filter(unit_id__in=unit_ids).values_list("unit_id").annotate(s=Sum("total_amount")).values_list("unit_id", "s"))}
    rents_by_unit_month = {
        uid: amt or Decimal("0.00")
        for uid, amt in (Rent.objects.filter(unit_id__in=unit_ids, payment_date__gte=start_dt).values_list("unit_id").annotate(s=Sum("total_amount")).values_list("unit_id", "s"))
    }
    occ_by_unit_all = {
        uid: amt or Decimal("0.00") for uid, amt in (OccasionalPayments.objects.filter(unit_id__in=unit_ids).values_list("unit_id").annotate(s=Sum("amount")).values_list("unit_id", "s"))
    }
    occ_by_unit_month = {
        uid: amt or Decimal("0.00")
        for uid, amt in (OccasionalPayments.objects.filter(unit_id__in=unit_ids, payment_date__gte=start_d).values_list("unit_id").annotate(s=Sum("amount")).values_list("unit_id", "s"))
    }

    unit_rows = []
    owner_total_all_time = Decimal("0.00")
    owner_total_this_month = Decimal("0.00")

    for u in units_qs:
        before_all = rents_by_unit_all.get(u.id, Decimal("0.00"))
        before_m = rents_by_unit_month.get(u.id, Decimal("0.00"))
        occ_all = occ_by_unit_all.get(u.id, Decimal("0.00"))
        occ_m = occ_by_unit_month.get(u.id, Decimal("0.00"))
        after_all = before_all - occ_all
        after_m = before_m - occ_m
        frac = (u.owner_percentage or Decimal("0")) / Decimal("100")
        o_all = (after_all * frac).quantize(TWO_PLACES)
        o_m = (after_m * frac).quantize(TWO_PLACES)

        unit_rows.append(
            {
                "unit_id": u.id,
                "unit_name": u.name,
                "owner_percentage": frac.quantize(FOUR_PLACES),
                "total": before_all.quantize(TWO_PLACES),
                "total_this_month": before_m.quantize(TWO_PLACES),
                "total_occasional": occ_all.quantize(TWO_PLACES),
                "total_occasional_this_month": occ_m.quantize(TWO_PLACES),
                "total_after_occasional": after_all.quantize(TWO_PLACES),
                "total_after_occasional_this_month": after_m.quantize(TWO_PLACES),
                "owner_total": o_all,
                "owner_total_this_month": o_m,
            }
        )
        owner_total_all_time += o_all
        owner_total_this_month += o_m

    paid_to_owner_total = OwnerPayment.objects.filter(owner=owner).aggregate(total=Sum("amount")).get("total") or Decimal("0.00")
    still_need_to_pay = (owner_total_all_time - paid_to_owner_total).quantize(TWO_PLACES)

    (total_after_all_time - owner_total_all_time).quantize(TWO_PLACES)
    (total_after_this_month - owner_total_this_month).quantize(TWO_PLACES)

    return {
        "owner_id": owner.id,
        "owner_name": owner.full_name,
        "total_this_month": total_before_this_month.quantize(TWO_PLACES),
        "total": total_before_all_time.quantize(TWO_PLACES),
        "total_occasional_this_month": total_occasional_this_month.quantize(TWO_PLACES),
        "total_occasional": total_occasional_all_time.quantize(TWO_PLACES),
        "total_after_occasional_this_month": total_after_this_month.quantize(TWO_PLACES),
        "total_after_occasional": total_after_all_time.quantize(TWO_PLACES),
        "owner_total_this_month": owner_total_this_month.quantize(TWO_PLACES),
        "owner_total": owner_total_all_time.quantize(TWO_PLACES),
        "paid_to_owner_total": Decimal(paid_to_owner_total).quantize(TWO_PLACES),
        "still_need_to_pay": still_need_to_pay,
        "units": unit_rows,
    }


def calculate_unit_payment_summary(unit_id: int) -> dict:
    """
    Build per-unit payment summary.
    Payload keys (unchanged):
      unit_id, unit_name, owner_id, owner_name, owner_percentage, total_this_month, total,
      total_occasional_this_month, total_occasional, total_after_occasional_this_month,
      total_after_occasional, company_total_this_month, company_total
    """
    unit = Unit.objects.select_related("owner").get(pk=unit_id)
    start_dt = start_of_current_month_datetime()
    start_d = start_of_current_month_date()

    total_before_all_time = Rent.objects.filter(unit=unit).aggregate(total=Sum("total_amount")).get("total") or Decimal("0.00")
    total_before_this_month = Rent.objects.filter(unit=unit, payment_date__gte=start_dt).aggregate(total=Sum("total_amount")).get("total") or Decimal("0.00")

    total_occasional_all_time = OccasionalPayments.objects.filter(unit=unit).aggregate(total=Sum("amount")).get("total") or Decimal("0.00")
    total_occasional_this_month = OccasionalPayments.objects.filter(unit=unit, payment_date__gte=start_d).aggregate(total=Sum("amount")).get("total") or Decimal("0.00")

    total_after_all_time = total_before_all_time - total_occasional_all_time
    total_after_this_month = total_before_this_month - total_occasional_this_month

    frac = (unit.owner_percentage or Decimal("0")) / Decimal("100")
    owner_total_all_time = (total_after_all_time * frac).quantize(TWO_PLACES)
    owner_total_this_month = (total_after_this_month * frac).quantize(TWO_PLACES)

    company_total_all_time = (total_after_all_time - owner_total_all_time).quantize(TWO_PLACES)
    company_total_this_month = (total_after_this_month - owner_total_this_month).quantize(TWO_PLACES)

    return {
        "unit_id": unit.id,
        "unit_name": unit.name,
        "owner_id": unit.owner_id,
        "owner_name": unit.owner.full_name,
        "owner_percentage": frac.quantize(FOUR_PLACES),
        "total_this_month": total_before_this_month.quantize(TWO_PLACES),
        "total": total_before_all_time.quantize(TWO_PLACES),
        "total_occasional_this_month": total_occasional_this_month.quantize(TWO_PLACES),
        "total_occasional": total_occasional_all_time.quantize(TWO_PLACES),
        "total_after_occasional_this_month": total_after_this_month.quantize(TWO_PLACES),
        "total_after_occasional": total_after_all_time.quantize(TWO_PLACES),
        "company_total_this_month": company_total_this_month,
        "company_total": company_total_all_time,
    }


def calculate_company_payment_summary(unit_id: int | None = None) -> dict:
    """
    Build company-wide payment summary, optionally scoped to a unit.
    Payload keys (unchanged):
      total_this_month, total, total_occasional_this_month, total_occasional,
      total_after_occasional_this_month, total_after_occasional,
      owner_total_this_month, owner_total, company_total_this_month, company_total,
      [unit_id if provided]
    """
    start_dt = start_of_current_month_datetime()
    start_d = start_of_current_month_date()

    units_qs = Unit.objects.all().only("id", "owner_percentage")
    if unit_id is not None:
        units_qs = units_qs.filter(pk=unit_id)
    unit_ids = list(units_qs.values_list("id", flat=True))

    total_before_all_time = Rent.objects.filter(unit_id__in=unit_ids).aggregate(total=Sum("total_amount")).get("total") or Decimal("0.00")
    total_before_this_month = Rent.objects.filter(unit_id__in=unit_ids, payment_date__gte=start_dt).aggregate(total=Sum("total_amount")).get("total") or Decimal("0.00")

    total_occasional_all_time = OccasionalPayments.objects.filter(unit_id__in=unit_ids).aggregate(total=Sum("amount")).get("total") or Decimal("0.00")
    total_occasional_this_month = OccasionalPayments.objects.filter(unit_id__in=unit_ids, payment_date__gte=start_d).aggregate(total=Sum("amount")).get("total") or Decimal("0.00")

    total_after_all_time = total_before_all_time - total_occasional_all_time
    total_after_this_month = total_before_this_month - total_occasional_this_month

    # Compute owner totals by unit, then company = total_after - owner_total
    perc_map = {u.id: (u.owner_percentage or Decimal("0")) for u in units_qs}
    rents_by_unit_all = {uid: amt or Decimal("0.00") for uid, amt in (Rent.objects.filter(unit_id__in=unit_ids).values_list("unit_id").annotate(s=Sum("total_amount")).values_list("unit_id", "s"))}
    occ_by_unit_all = {
        uid: amt or Decimal("0.00") for uid, amt in (OccasionalPayments.objects.filter(unit_id__in=unit_ids).values_list("unit_id").annotate(s=Sum("amount")).values_list("unit_id", "s"))
    }
    rents_by_unit_month = {
        uid: amt or Decimal("0.00")
        for uid, amt in (Rent.objects.filter(unit_id__in=unit_ids, payment_date__gte=start_dt).values_list("unit_id").annotate(s=Sum("total_amount")).values_list("unit_id", "s"))
    }
    occ_by_unit_month = {
        uid: amt or Decimal("0.00")
        for uid, amt in (OccasionalPayments.objects.filter(unit_id__in=unit_ids, payment_date__gte=start_d).values_list("unit_id").annotate(s=Sum("amount")).values_list("unit_id", "s"))
    }

    owner_total_all_time = Decimal("0.00")
    owner_total_this_month = Decimal("0.00")

    for uid, before_all in rents_by_unit_all.items():
        occ_all = occ_by_unit_all.get(uid, Decimal("0.00"))
        after_all = before_all - occ_all
        frac = Decimal(perc_map.get(uid, Decimal("0"))) / Decimal("100")
        owner_total_all_time += after_all * frac

    for uid, before_m in rents_by_unit_month.items():
        occ_m = occ_by_unit_month.get(uid, Decimal("0.00"))
        after_m = before_m - occ_m
        frac = Decimal(perc_map.get(uid, Decimal("0"))) / Decimal("100")
        owner_total_this_month += after_m * frac

    owner_total_all_time = owner_total_all_time.quantize(TWO_PLACES)
    owner_total_this_month = owner_total_this_month.quantize(TWO_PLACES)

    company_total_all_time = (total_after_all_time - owner_total_all_time).quantize(TWO_PLACES)
    company_total_this_month = (total_after_this_month - owner_total_this_month).quantize(TWO_PLACES)

    payload: Dict[str, Any] = {
        "total_this_month": total_before_this_month.quantize(TWO_PLACES),
        "total": total_before_all_time.quantize(TWO_PLACES),
        "total_occasional_this_month": total_occasional_this_month.quantize(TWO_PLACES),
        "total_occasional": total_occasional_all_time.quantize(TWO_PLACES),
        "total_after_occasional_this_month": total_after_this_month.quantize(TWO_PLACES),
        "total_after_occasional": total_after_all_time.quantize(TWO_PLACES),
        "owner_total_this_month": owner_total_this_month,
        "owner_total": owner_total_all_time,
        "company_total_this_month": company_total_this_month,
        "company_total": company_total_all_time,
    }

    if unit_id is not None:
        payload["unit_id"] = unit_id

    return payload
