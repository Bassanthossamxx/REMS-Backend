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

# units types options
UNIT_TYPES = [
    ('apartment', 'Apartment'),
    ('villa', 'Villa'),
    ('office', 'Office'),
    ('shop', 'Shop'),
    ('studio', 'Studio'),
    ('penthouse', 'Penthouse'),
    ('warehouse', 'Warehouse'),
    ('retail', 'Retail'),
]
# Payment status options
class PaymentStatus(models.TextChoices):
    PAID = "paid", "Paid"
    PENDING = "pending", "Pending"
    OVERDUE = "overdue", "Overdue"

# Rent lifecycle status options
class RentStatus(models.TextChoices):
    ACTIVE = "active", "Active"  # paid ,  end date not reached
    EXPIRED = "expired", "Expired"  # end date passed
    PENDING = "pending", "Pending"  # awaiting payment
    CANCELED = "canceled", "Canceled"  # explicitly canceled

# Payment method options
class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    CREDIT_CARD = "credit_card", "Credit Card"
    ONLINE_PAYMENT = "online_payment", "Online Payment"

# Tenant lifecycle status options
class TenantStatus(models.TextChoices):
    ACTIVE = "active", "Active"          # has a rent currently ongoing
    COMPLETED = "completed", "Completed"  # has past rents only, none upcoming
    INACTIVE = "inactive", "Inactive"    # no rents at all (or only upcoming)
