from django.db import models
from decimal import Decimal
from core.models import City, District
from owners.models import Owner


class Unit(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        IN_MAINTENANCE = "in_maintenance", "In Maintenance"

    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(Owner, related_name="units", on_delete=models.CASCADE)
    city = models.ForeignKey(City, related_name="units", on_delete=models.CASCADE)
    district = models.ForeignKey(District, related_name="units", on_delete=models.CASCADE)
    location_url = models.URLField()
    location_text = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    details = models.JSONField(
        default=dict,
        help_text="Example: {'type': 'Apartment', 'bedrooms': 2, 'bathrooms': 2, 'area': 850, 'floor': '1st Floor'}"
    )

    price_per_day = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    owner_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Totals
    total_rent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_occasional = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_owner_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_my_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name

    def update_status(self):
        """Auto mark unit as occupied if there is an active rent."""
        from rents.models import Rent
        active = Rent.objects.filter(unit=self, rent_start__lte=models.F("rent_end")).exists()
        self.status = self.Status.OCCUPIED if active else self.Status.AVAILABLE
        self.save(update_fields=["status"])

    def update_financials(self):
        """Recalculate all money values for this unit."""
        from rents.models import Rent
        from units.models import OccasionalPayment

        total_rent = Rent.objects.filter(unit=self).aggregate(total=models.Sum("total_amount"))["total"] or Decimal(0)
        total_occ = OccasionalPayment.objects.filter(unit=self).aggregate(total=models.Sum("amount"))["total"] or Decimal(0)
        owner_share = (total_rent * self.owner_percentage) / Decimal(100)
        my_revenue = total_rent - owner_share - total_occ

        self.total_rent = total_rent
        self.total_occasional = total_occ
        self.total_owner_revenue = owner_share
        self.total_my_revenue = my_revenue
        self.save()


class UnitImage(models.Model):
    unit = models.ForeignKey(Unit, related_name="images", on_delete=models.CASCADE)
    image = models.URLField(help_text="Cloudinary image URL")

    def __str__(self):
        return f"Image for {self.unit.name}"


class OccasionalPayment(models.Model):
    """Extra costs to subtract from revenue — maintenance, cleaning, etc."""
    class PaymentType(models.TextChoices):
        MAINTENANCE = "maintenance", "Maintenance"
        REPAIR = "repair", "Repair"
        CLEANING = "cleaning", "Cleaning"
        OTHER = "other", "Other"

    unit = models.ForeignKey(Unit, related_name="occasional_payments", on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, related_name="occasional_payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=30, choices=PaymentType.choices)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_type} - {self.amount} ({self.unit.name})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update unit + owner revenue
        self.unit.update_financials()
        from owners.models import OwnerRevenue
        revenue, _ = OwnerRevenue.objects.get_or_create(owner=self.owner)
        revenue.update_totals()
