from django.db import models
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
