from django.db import models
from decimal import Decimal
from django.utils import timezone
from apps.core.models import City, District
from apps.owners.models import Owner
from config.choices import Status, PaymentType , UNIT_TYPES
from config.validation import validate_map_url
from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.rents.models import Rent


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
        null=False
    )
    bedrooms = models.PositiveIntegerField(
        help_text="Number of bedrooms in the unit.",
        blank=False,
        null=False
    )
    bathrooms = models.PositiveIntegerField(
        help_text="Number of bathrooms in the unit.",
        blank=False,
        null=False
    )
    area = models.PositiveIntegerField(
        help_text="Area of the unit in square meters.",
        blank=False,
        null=False
    )

    price_per_day = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    owner_percentage = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        help_text="Owner's percentage (e.g., 30 or 50.5). Required.",
        default=0
    )

    # Totals
    total_rent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_occasional = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_owner_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_my_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Detect previous owner before saving (if updating existing instance)
        prev_owner_id = None
        if self.pk:
            prev_owner_id = type(self).objects.filter(pk=self.pk).values_list("owner_id", flat=True).first()

        super().save(*args, **kwargs)

        # Recompute financials WITHOUT calling self.save() to avoid recursion
        from django.db.models import Sum
        # Aggregate totals
        total_rent = Rent.objects.filter(unit=self).aggregate(total=models.Sum("total_amount"))["total"] or Decimal(0)
        from apps.units.models import OccasionalPayment  # local import
        total_occ = OccasionalPayment.objects.filter(unit=self).aggregate(total=models.Sum("amount"))["total"] or Decimal(0)
        owner_share = (total_rent * (self.owner_percentage or Decimal(0))) / Decimal(100)
        my_revenue = total_rent - owner_share - total_occ
        type(self).objects.filter(pk=self.pk).update(
            total_rent=total_rent,
            total_occasional=total_occ,
            total_owner_revenue=owner_share,
            total_my_revenue=my_revenue,
        )
        # Ensure the in-memory instance reflects new totals for serializers/responses
        self.total_rent = total_rent
        self.total_occasional = total_occ
        self.total_owner_revenue = owner_share
        self.total_my_revenue = my_revenue

        # Update OwnerRevenue for current and previous owners
        from apps.owners.models import OwnerRevenue, Owner as OwnerModel
        revenue, _ = OwnerRevenue.objects.get_or_create(owner=self.owner)
        revenue.update_totals()
        if prev_owner_id and prev_owner_id != self.owner_id:
            prev_owner = OwnerModel.objects.filter(pk=prev_owner_id).first()
            if prev_owner:
                prev_rev, _ = OwnerRevenue.objects.get_or_create(owner=prev_owner)
                prev_rev.update_totals()

    def update_status(self):
        """Auto mark unit as occupied if there is an active rent."""
        from apps.rents.models import Rent

        today = timezone.now().date()
        active = Rent.objects.filter(
            unit=self,
            rent_start__lte=today,
            rent_end__gte=today
        ).exists()

        self.status = Status.OCCUPIED if active else Status.AVAILABLE
        self.save(update_fields=["status"])

    def update_financials(self):
        """Recalculate all money values for this unit."""
        total_rent = Rent.objects.filter(unit=self).aggregate(total=models.Sum("total_amount"))["total"] or Decimal(0)

        # Local import to avoid circular dependency
        from apps.units.models import OccasionalPayment
        total_occ = OccasionalPayment.objects.filter(unit=self).aggregate(total=models.Sum("amount"))["total"] or Decimal(0)

        owner_share = (total_rent * self.owner_percentage) / Decimal(100)
        my_revenue = total_rent - owner_share - total_occ

        self.total_rent = total_rent
        self.total_occasional = total_occ
        self.total_owner_revenue = owner_share
        self.total_my_revenue = my_revenue
        self.save()

    @property
    def current_tenant(self):
        """Return active tenant details if unit is occupied."""
        from apps.rents.models import Rent

        today = timezone.now().date()
        rent = (
            Rent.objects
            .filter(unit=self, rent_start__lte=today, rent_end__gte=today)
            .select_related("tenant")
            .first()
        )

        if rent:
            return {
                "name": rent.tenant.full_name,
                "rent_start": rent.rent_start,
                "rent_end": rent.rent_end,
            }
        return None

class UnitImage(models.Model):
    unit = models.ForeignKey(Unit, related_name="images", on_delete=models.CASCADE)
    image = CloudinaryField("image", help_text="Cloudinary image field")

    def __str__(self):
        return f"Image for {self.unit.name}"