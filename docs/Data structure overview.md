# Real Estate CRM – Data Structure Overview

## 1. Overview

The Real Estate CRM system is a backend management solution built with **Django** and **Django REST Framework**, designed for a single superuser to manage all core operations of real estate units, tenants, owners, payments, and inventory.

The system supports full CRUD operations and provides filtering capabilities, including city and district-based queries.

---

## 2. User Roles

### Superuser

* Only one superuser exists.
* Manages all entities in the system.
* Has full control over creating, updating, and deleting records.

---

## 3. Core Entities

### 3.1 Cities

Represents major cities in Saudi Arabia.

**Fields:**

| Field | Type      | Description       |
| ----- | --------- | ----------------- |
| id    | UUID      | Primary key       |
| name  | CharField | City name, unique |

---

### 3.2 Districts

Represents districts (neighborhoods) that belong to specific cities.

**Fields:**

| Field | Type             | Description                                 |
| ----- | ---------------- | ------------------------------------------- |
| id    | UUID             | Primary key                                 |
| name  | CharField        | District name                               |
| city  | ForeignKey(City) | References the city the district belongs to |

**Notes:**

* Each city can have multiple districts.
* Districts are used for filtering and location-based searches.

---

### 3.3 Units

Represents real estate units available for rent or sale.

**Fields:**

| Field         | Type                 | Description                                              |
| ------------- | -------------------- | -------------------------------------------------------- |
| id            | UUID                 | Primary key                                              |
| name          | CharField            | Unique identifier (allows letters, numbers, and hyphens) |
| city          | ForeignKey(City)     | City where the unit is located                           |
| district      | ForeignKey(District) | District of the unit                                     |
| description   | TextField            | Unit details                                             |
| price_per_day | DecimalField         | Optional; used for rental pricing                        |
| area          | FloatField           | Unit size in square meters                               |
| status        | ChoiceField          | Available, Rented, or Under Maintenance                  |
| created_at    | DateTimeField        | Creation timestamp                                       |
| updated_at    | DateTimeField        | Last update timestamp                                    |

---

### 3.4 UnitImages

Represents images associated with each unit.

**Fields:**

| Field       | Type             | Description      |
| ----------- | ---------------- | ---------------- |
| id          | UUID             | Primary key      |
| unit        | ForeignKey(Unit) | Associated unit  |
| image       | ImageField       | Image file       |
| uploaded_at | DateTimeField    | Upload timestamp |

---

### 3.5 Owners

Represents property owners.

**Fields:**

| Field      | Type          | Description        |
| ---------- | ------------- | ------------------ |
| id         | UUID          | Primary key        |
| full_name  | CharField     | Owner’s full name  |
| phone      | CharField     | Contact number     |
| email      | EmailField    | Optional           |
| address    | TextField     | Optional           |
| created_at | DateTimeField | Creation timestamp |

---

### 3.6 Tenants

Represents individuals or companies renting units.

**Fields:**

| Field       | Type          | Description           |
| ----------- | ------------- | --------------------- |
| id          | UUID          | Primary key           |
| full_name   | CharField     | Tenant’s full name    |
| phone       | CharField     | Contact number        |
| email       | EmailField    | Optional              |
| national_id | CharField     | National or ID number |
| created_at  | DateTimeField | Creation timestamp    |

---

### 3.7 Rentals

Represents active or completed rental agreements between tenants and units.

**Fields:**

| Field          | Type               | Description                    |
| -------------- | ------------------ | ------------------------------ |
| id             | UUID               | Primary key                    |
| unit           | ForeignKey(Unit)   | Rented unit                    |
| tenant         | ForeignKey(Tenant) | Tenant renting the unit        |
| start_date     | DateField          | Rental start date              |
| end_date       | DateField          | Rental end date                |
| total_amount   | DecimalField       | Total rent                     |
| payment_status | ChoiceField        | Paid, Pending, or Overdue      |
| payment_method | ChoiceField        | Cash, Bank Transfer, or Credit |
| created_at     | DateTimeField      | Creation timestamp             |

---

### 3.8 Inventory

Represents items or materials used for maintenance or furnishing.

**Fields:**

| Field           | Type          | Description                          |
| --------------- | ------------- | ------------------------------------ |
| id              | UUID          | Primary key                          |
| name            | CharField     | Item name                            |
| quantity        | IntegerField  | Stock quantity                       |
| unit_of_measure | ChoiceField   | Piece, Box, Meter, etc.              |
| status          | ChoiceField   | In Stock, Low Stock, or Out of Stock |
| created_at      | DateTimeField | Creation timestamp                   |

---

## 4. Filtering Capabilities

### Unit Filtering

The system allows filtering units by:

* City
* District
* Status

**Examples:**

```
GET /api/units/?city=Riyadh
GET /api/units/?city=Riyadh&district=Al Olaya
```

Dynamic filters are also supported through a `filters.py` configuration using `django-filter`.

---

## 5. Relationships Summary

| Entity   | Relationship        | Related Entity | Type        |
| -------- | ------------------- | -------------- | ----------- |
| City     | has many            | Districts      | One-to-Many |
| District | belongs to          | City           | Many-to-One |
| Unit     | belongs to          | City           | Many-to-One |
| Unit     | belongs to          | District       | Many-to-One |
| Unit     | has many            | UnitImages     | One-to-Many |
| Unit     | can have one active | Rental         | One-to-One  |
| Rental   | belongs to          | Tenant         | Many-to-One |
| Rental   | belongs to          | Unit           | Many-to-One |

---

## 6. Notes

* Only the superuser manages all data.
* Each entity can be extended later for multi-user support if required.
* Cities and districts can be preloaded with Saudi Arabia’s most common regions for convenience.
