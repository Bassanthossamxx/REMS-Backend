import uuid
from django.db import models

class Inventory(models.Model):
    CATEGORY_CHOICES = [
        ("Maintenance", "Maintenance"),
        ("Electrical", "Electrical"),
        ("Plumbing", "Plumbing"),
        ("Security", "Security"),
        ("Cleaning", "Cleaning"),
        ("Furniture", "Furniture"),
    ]

    UNIT_CHOICES = [
        ("Pieces", "Pieces"),
        ("Boxes", "Boxes"),
        ("Gallons", "Gallons"),
        ("Liters", "Liters"),
        ("Kits", "Kits"),
        ("Sets", "Sets"),
        ("Meters", "Meters"),
        ("Feet", "Feet"),
    ]

    STATUS_CHOICES = [
        ("In Stock", "In Stock"),
        ("Low Stock", "Low Stock"),
        ("Out of Stock", "Out of Stock"),
    ]
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    lower_quantity = models.PositiveIntegerField(default=5)
    unit_of_measure = models.CharField(max_length=50, choices=UNIT_CHOICES)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    supplier_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="In Stock")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_value = self.quantity * self.unit_price
        if self.quantity == 0:
            self.status = "Out of Stock"
        elif self.quantity <= self.lower_quantity:
            self.status = "Low Stock"
        else:
            self.status = "In Stock"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.status})"
