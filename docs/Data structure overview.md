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

| Field         | Type                  | Description                                                                 |
|---------------|-----------------------|-----------------------------------------------------------------------------|
| id            | UUID                  | Primary key                                                                 |
| name          | CharField             | Unique identifier (allows letters, numbers, and hyphens)                    |
| city          | ForeignKey(City)      | City where the unit is located                                              |
| district      | ForeignKey(District)  | District of the unit                                                        |
| location_text | TextField             | location text detailed; required                                            |
| details       | JsonField             | bedrooms , area , bathrooms , floor, type ; required                              |
| lease_info    | JsonField             | two dates and will use them to notifaction; required                        |
| location_url  | URLField              | location url from map ; will need validation ; required                     |
| description   | TextField             | Unit details; optional                                                      |
| price_per_day | DecimalField          | Optional; used for rental pricing  for day                                  |
| owner_id      | UUID                  | forgien key choose owner name or id                                         |
| status        | ChoiceField           | Available, Rented, or Under Maintenance "rented will be based on rent table |
| created_at    | DateTimeField         | Creation timestamp                                                          |
| updated_at    | DateTimeField         | Last update timestamp                                                       |

- Each unit will also be linked to its image URLs (stored as a JSON list), the tenant ID if currently rented get details of person and payment, and the related rent record ID. This connection allows calculating the unit’s total payments, tracking its rental status, and determining the owner’s revenue and owned units.
---

### 3.4 UnitImages

Represents images associated with each unit.
minmal one image at leaset
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

| Field       | Type          | Description                  |
|-------------|---------------|------------------------------|
| id          | UUID          | Primary key                  |
| full_name   | CharField     | Owner’s full name; required  |
| phone       | CharField     | Contact number; required     |
| email       | EmailField    | Optional                     |
| address     | TextField     | Optional                     |
| rate        | decimalField  | start with 5 base but 1 -> 5 |
| units_count | intgerField   | from units table             |
| update_at   | DateTimeField | update timestamp             |
| date_joined | DateTimeField | Creation timestamp           |

- will be linked with units tables to get unit details  and rent each unit price and owner revnue details too
---

### 3.6 Tenants

Represents individuals or companies renting units.

**Fields:**

| Field      | Type          | Description                   |
|------------|---------------|-------------------------------|
| id         | UUID          | Primary key                   |
| full_name  | CharField     | Tenant’s full name ; required |
| phone      | CharField     | Contact number; required      |
| email      | EmailField    | Optional                      |
| rate       | decimalField  | start with 5 base but 1 -> 5  |
| address    | TextField     | Optional                      |
| created_at | DateTimeField | Creation timestamp            |

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
| payment_date     | DateTimeField      | Creation payment timestamp             |

- will add attachment and details or notes too
- will add total revnue for super user and owner total after that to manage with owner revnue table

---

### 3.8 Inventory

Represents items or materials used for maintenance or furnishing.

**Fields:**

| Field           | Type          | Description                          |
| --------------- | ------------- | ------------------------------------ |
| id              | UUID          | Primary key                          |
| name            | CharField     | Item name                            |
| category        | ChociesField     | Item category > choices and can post it too |                            |
| quantity        | IntegerField  | Stock quantity                        |
| lower_quantity        | IntegerField  | Stock quantity                        |
| unit_of_measure | ChoiceField   | Piece, Box, Meter, etc.              |
| unit_prices | intgerField       | price of one item
| supplier_name | CharField   |  name of supplier; optional             |
| status          | ChoiceField   | In Stock, Low Stock, or Out of Stock |
| created_at      | DateTimeField | Creation timestamp                   |

- category : Maintenance , Electrical , Plumbing , Security , Cleaning , Furniture
- unit_of_measure : Pieces , Boxes , Gallons , Liters , Kits , Sets , Meters , Feet

---

##  3.9 Owner Revenue

| Field          | Type       | Description                                                  |
| -------------- | ---------- | ------------------------------------------------------------ |
| id             | UUID       | Primary key                                                  |
| owner_id       | FK → Owner | Reference owner                                              |
| amount         | Decimal    | Required                                                     |
| date           | Date       | Required                                                     |
| total_rent     | Decimal    | Calculated from rent table                                   |
| paid           | Boolean    | Whether amount is paid                                       |
| still_not_paid | Decimal    | `total_rent - paid_amount`                                   |
| payment_way    | Enum       | `["cash", "bank_transfer", "credit_card", "online_payment"]` |
| notes          | Text       | Optional                                                     |

>  Endpoint to record each owner payment event.

---

## 4.0  Payments

Handles recurring or occasional property expenses (e.g., utilities, maintenance).

| Field   | Type      | Description                                                |
| ------- | --------- | ---------------------------------------------------------- |
| id      | UUID      | Primary key                                                |
| unit_id | FK → Unit | Related unit                                               |
| type    | Enum      | `["water", "electricity", "wifi", "maintenance", "other"]` |
| amount  | Decimal   | Cost value                                                 |
| date    | Date      | Payment date                                               |
| status  | Enum      | `["paid", "unpaid", "pending"]`                            |

---

## 5.0 Notifications *(Future Enhancement)*

### Triggered When:

* Inventory item becomes `low_stock` or `out_of_stock`
* Lease `end_date` ≤ 2 months

| Field      | Type     | Description                          |
| ---------- | -------- | ------------------------------------ |
| id         | UUID     | Primary key                          |
| title      | String   | Notification title                   |
| message    | Text     | Alert message                        |
| type       | Enum     | `["inventory_alert", "lease_alert"]` |
| created_at | DateTime | Timestamp                            |

---

##  Dashboard Metrics *(Future Enhancement)*

To include:
Total Units
Occupied units
occupancy rate
Total Revenue for superuser
Pending Payments
Maintenance Requests
New Tenants This month
Recent Activity
- stock :
Total Items
In Stock
Low Stock
Out of Stock

---


## 4. Filtering Capabilities

### Unit Filtering

The system allows filtering units by:

* City
* District
* Status
* date
* type
* details

**Examples:**

```
GET /api/units/?city=Riyadh
GET /api/units/?city=Riyadh&district=Al Olaya
```

Dynamic filters are also supported through a `filters.py` configuration using `django-filter`.

---

## 5. Notes

* Only the superuser manages all data.
* Each entity can be extended later for multi-user support if required.
* Cities and districts can be preloaded with Saudi Arabia’s most common regions for convenience.
