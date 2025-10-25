from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone

from config.choices import TenantStatus


class Tenant(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    rate = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=TenantStatus.choices, default=TenantStatus.INACTIVE)

    def __str__(self):
        return self.full_name

    # Compute and persist average review rating into the tenant.rate field
    def recalc_rate(self, save: bool = True):
        agg = self.reviews.aggregate(avg=Avg("rate"))
        avg_rate = agg["avg"]
        # If no reviews, keep default behavior as 5.0
        new_rate = round(float(avg_rate), 1) if avg_rate is not None else 5.0
        if float(self.rate) != new_rate:
            self.rate = new_rate
            if save:
                self.save(update_fields=["rate"])

    def update_status(self, save: bool = True):
        """Compute tenant lifecycle status based on rents.
        - active: has a rent that includes today
        - completed: has past rents only (no active or upcoming)
        - inactive: no rents at all or only upcoming rents (or mix of past+upcoming but none active)
        """
        today = timezone.now().date()
        rents = self.rents.all()
        if rents.filter(rent_start__lte=today, rent_end__gte=today).exists():
            new_status = TenantStatus.ACTIVE
        else:
            has_past = rents.filter(rent_end__lt=today).exists()
            has_upcoming = rents.filter(rent_start__gt=today).exists()
            if has_past and not has_upcoming:
                new_status = TenantStatus.COMPLETED
            else:
                new_status = TenantStatus.INACTIVE

        if self.status != new_status:
            self.status = new_status
            if save:
                self.save(update_fields=["status"])


class Review(models.Model):
    tenant = models.ForeignKey(Tenant, related_name="reviews", on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    # allow fractional ratings like 4.5
    rate = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Review({self.tenant_id}) rate={self.rate}"

    def save(self, *args, **kwargs):
        is_update = self.pk is not None
        # On update, we won't allow changing tenant via serializer; if changed manually, recalc both
        prev_tenant_id = None
        if is_update:
            try:
                prev_tenant_id = type(self).objects.only("tenant_id").get(pk=self.pk).tenant_id
            except type(self).DoesNotExist:
                prev_tenant_id = None
        super().save(*args, **kwargs)
        # Recalc for affected tenant(s)
        if prev_tenant_id and prev_tenant_id != self.tenant_id:
            Tenant.objects.filter(pk=prev_tenant_id).first() and Tenant.objects.get(pk=prev_tenant_id).recalc_rate()
        self.tenant.recalc_rate()

    def delete(self, *args, **kwargs):
        tenant = self.tenant
        super().delete(*args, **kwargs)
        tenant.recalc_rate()
