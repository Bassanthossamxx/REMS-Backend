from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from config.choices import PaymentMethod, OccasionalPaymentCategory
from datetime import date


class OccasionalPayments(models.Model):
    unit = models.ForeignKey(
        "units.Unit",
        related_name="occasional_payments",
        on_delete=models.CASCADE,
    )
    category = models.CharField(
        max_length=20,
        choices=OccasionalPaymentCategory.choices,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )
    payment_date = models.DateField(default=date.today , null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        unit_name = getattr(self.unit, "name", str(self.unit_id))
        cat = self.category if self.category else "Unknown"
        return f"OccasionalPayment[{cat}] - {unit_name} - {self.amount}"
