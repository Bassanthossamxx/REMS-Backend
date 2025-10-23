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