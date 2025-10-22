from django.db import models
from decimal import Decimal
from django.utils import timezone
from config.choices import PaymentStatus, PaymentMethod, RentStatus

class Rent(models.Model):
    # Backward compatible: allow referencing choice enums as Rent.PaymentStatus
    PaymentStatus = PaymentStatus

    unit = models.ForeignKey("units.Unit", related_name="rents", on_delete=models.CASCADE)
    tenant = models.ForeignKey("tenants.Tenant", related_name="rents", on_delete=models.CASCADE)

    rent_start = models.DateField()
    rent_end = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    status = models.CharField(max_length=20, choices=RentStatus.choices, default=RentStatus.PENDING)
    notes = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to="rents/attachments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rent #{self.id} - {self.unit.name} ({self.tenant.full_name})"

    def _compute_status(self):
        """
        Determine the rent lifecycle status based on payment status and dates.
        Rules:
        - If status is explicitly set to CANCELED, keep it unchanged.
        - If paid and today <= rent_end => ACTIVE
        - If paid and today > rent_end => EXPIRED
        - If payment pending => PENDING
        - If payment overdue => EXPIRED if end date passed, else PENDING
        """
        if self.status == RentStatus.CANCELED:
            return  # don't override explicit cancellations

        today = timezone.now().date()

        if self.payment_status == PaymentStatus.PAID:
            if today <= self.rent_end:
                self.status = RentStatus.ACTIVE
            else:
                self.status = RentStatus.EXPIRED
        elif self.payment_status == PaymentStatus.PENDING:
            self.status = RentStatus.PENDING
        elif self.payment_status == PaymentStatus.OVERDUE:
            # If rent already ended and payment overdue, mark as expired; otherwise treat as pending
            if self.rent_end < today:
                self.status = RentStatus.EXPIRED
            else:
                self.status = RentStatus.PENDING
        else:
            # Fallback: keep current or default to pending
            self.status = self.status or RentStatus.PENDING

    def save(self, *args, **kwargs):
        # Compute current lifecycle status before saving
        self._compute_status()
        super().save(*args, **kwargs)

        # Update unit status
        self.unit.update_status()

        # Update or create owner revenue using the unit's owner
        from apps.owners.models import OwnerRevenue
        revenue, _ = OwnerRevenue.objects.get_or_create(owner=self.unit.owner)
        revenue.update_totals()

        # Update unit financial stats
        self.unit.update_financials()
