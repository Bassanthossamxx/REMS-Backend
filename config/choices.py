from django.db import models

# unit status options
class Status(models.TextChoices):
    AVAILABLE = "available", "Available"
    OCCUPIED = "occupied", "Occupied"
    IN_MAINTENANCE = "in_maintenance", "In Maintenance"

# Occasional Payment types options
class PaymentType(models.TextChoices):
    MAINTENANCE = "maintenance", "Maintenance"
    REPAIR = "repair", "Repair"
    CLEANING = "cleaning", "Cleaning"
    OTHER = "other", "Other"
