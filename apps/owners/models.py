from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator


class Owner(models.Model):
    full_name = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    address = models.TextField(blank=True, null=True)
    rate = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=5.0,
        validators=[MinValueValidator(Decimal("1.0")), MaxValueValidator(Decimal("5.0"))],
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class OwnerRevenue(models.Model):
    """Tracks total rent and payments for each owner."""

    class PaymentWay(models.TextChoices):
        CASH = "cash", "Cash"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CREDIT_CARD = "credit_card", "Credit Card"
        ONLINE_PAYMENT = "online_payment", "Online Payment"

    owner = models.ForeignKey(Owner, related_name="revenues", on_delete=models.CASCADE)
    total_rent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    still_not_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_occasional = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"OwnerRevenue({self.owner.full_name})"

    def update_totals(self):
        """Recalculate owner revenue values dynamically.

        - total_rent: sum of all rents for this owner's units
        - total_occasional: sum of all occasional payments for this owner
        - net_revenue: owner's share = sum over units(total_rent(unit) * owner_percentage/100)
        - paid_total: sum of OwnerPayment amounts
        - still_not_paid: max(net_revenue - paid_total, 0)
        """
        from django.db.models import Sum
        from apps.units.models import OccasionalPayment, Unit
        from apps.rents.models import Rent

        # Total paid to the owner so far
        total_paid = self.payments.aggregate(total=models.Sum("amount"))["total"] or Decimal(0)
        self.paid_total = total_paid

        # Sum all rents for this owner’s units
        total_rent_sum = Rent.objects.filter(unit__owner=self.owner).aggregate(sum=Sum("total_amount"))["sum"] or Decimal(0)
        self.total_rent = total_rent_sum

        # Sum all occasional payments for this owner’s units (informational)
        total_occ = OccasionalPayment.objects.filter(owner=self.owner).aggregate(sum=Sum("amount"))["sum"] or Decimal(0)
        self.total_occasional = total_occ

        # Compute owner's share across units using each unit's owner_percentage
        units_qs = (
            Unit.objects
            .filter(owner=self.owner)
            .annotate(unit_total=Sum("rents__total_amount"))
        )
        owner_share_total = Decimal(0)
        for u in units_qs:
            unit_total = u.unit_total or Decimal(0)
            owner_share_total += (unit_total * (u.owner_percentage or Decimal(0))) / Decimal(100)

        # Owner net revenue is the share owed to owner (not reducing occasional here)
        self.net_revenue = owner_share_total
        self.still_not_paid = max(self.net_revenue - self.paid_total, Decimal(0))

        self.save()


class OwnerPayment(models.Model):
    """Each individual payment entry for an owner."""
    revenue = models.ForeignKey(OwnerRevenue, related_name="payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_way = models.CharField(max_length=20, choices=OwnerRevenue.PaymentWay.choices, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto update totals whenever a payment is added or changed
        self.revenue.update_totals()

    def __str__(self):
        return f"{self.amount} paid to {self.revenue.owner.full_name}"
