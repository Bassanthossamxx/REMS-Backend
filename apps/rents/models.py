from django.db import models
from decimal import Decimal
from django.utils import timezone


class Rent(models.Model):
    class PaymentStatus(models.TextChoices):
        PAID = "paid", "Paid"
        PENDING = "pending", "Pending"
        OVERDUE = "overdue", "Overdue"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CREDIT_CARD = "credit_card", "Credit Card"
        ONLINE_PAYMENT = "online_payment", "Online Payment"

    unit = models.ForeignKey("units.Unit", related_name="rents", on_delete=models.CASCADE)
    tenant = models.ForeignKey("tenants.Tenant", related_name="rents", on_delete=models.CASCADE)

    rent_start = models.DateField()
    rent_end = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to="rents/attachments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rent #{self.id} - {self.unit.name} ({self.tenant.full_name})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update unit status
        self.unit.update_status()

        # Update or create owner revenue
        from owners.models import OwnerRevenue
        revenue, _ = OwnerRevenue.objects.get_or_create(owner=self.unit.owner)
        revenue.update_totals()

        # Update unit financial stats
        self.unit.update_financials()
