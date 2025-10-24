from django.db import models
from config.choices import STATUS_CHOICES , UNIT_CHOICES ,CATEGORY_CHOICES

class Inventory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField()
    lower_quantity = models.PositiveIntegerField()
    unit_of_measure = models.CharField(max_length=50, choices=UNIT_CHOICES)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
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
