from datetime import date
from decimal import Decimal

from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import City, District
from apps.owners.models import Owner
from config.choices import UNIT_TYPES, Status
from config.validation import validate_map_url


class Unit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(Owner, related_name="units", on_delete=models.CASCADE)
    city = models.ForeignKey(City, related_name="units", on_delete=models.CASCADE)
    district = models.ForeignKey(District, related_name="units", on_delete=models.CASCADE)
    location_url = models.URLField(validators=[validate_map_url])
    location_text = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    type = models.CharField(
        max_length=20,
        choices=UNIT_TYPES,
        help_text="Type of the unit (e.g., Apartment, Villa, etc.).",
        blank=False,
        null=False,
    )
    bedrooms = models.PositiveIntegerField(help_text="Number of bedrooms in the unit.", blank=False, null=False)
    bathrooms = models.PositiveIntegerField(help_text="Number of bathrooms in the unit.", blank=False, null=False)
    area = models.PositiveIntegerField(help_text="Area of the unit in square meters.", blank=False, null=False)

    price_per_day = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    owner_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        help_text="Owner's percentage (e.g., 30 or 50.5). Required.",
        default=0,
    )
    lease_start = models.DateField(default=date.today)
    lease_end = models.DateField(default=date.today)

    def __str__(self):
        return self.name

    def clean(self):
        # Ensure lease_end is strictly after lease_start
        if self.lease_start and self.lease_end and self.lease_end <= self.lease_start:
            raise ValidationError({"lease_end": "Lease end date must be after lease start date."})

    def save(self, *args, **kwargs):
        # Validate model before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def update_status(self):
        """
        Enforce status rules based on active rents:
        - If there is an active rent today => force status to OCCUPIED.
        - If there is no active rent today and current status is OCCUPIED => revert to AVAILABLE.
        - If status is IN_MAINTENANCE => keep it as is regardless of active rent.
        Does NOT modify lease_start/lease_end.
        """
        from django.utils import timezone

        from apps.rents.models import Rent

        today = timezone.now().date()
        active = Rent.objects.filter(
            unit=self,
            rent_start__lte=today,
            rent_end__gte=today,
        ).exists()

        # Keep maintenance as is
        if self.status == Status.IN_MAINTENANCE:
            return

        # Determine new status
        new_status = None
        if active and self.status != Status.OCCUPIED:
            new_status = Status.OCCUPIED
        elif not active and self.status == Status.OCCUPIED:
            new_status = Status.AVAILABLE

        if new_status and self.status != new_status:
            type(self).objects.filter(pk=self.pk).update(status=new_status)
            self.status = new_status


class UnitImage(models.Model):
    unit = models.ForeignKey(Unit, related_name="images", on_delete=models.CASCADE)
    image = CloudinaryField("image", help_text="Cloudinary image field")

    def __str__(self):
        return f"Image for {self.unit.name}"
