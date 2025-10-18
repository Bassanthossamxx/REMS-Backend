# Real Estate CRM – Data Structure Overview
### Frontend : https://crmbild.netlify.app/dashboard
## Superuser

* Only **one superuser** exists.
* Manages **all system operations**: adding units, owners, tenants, payments, etc.

---

## Units

### Fields:

* **id**
* **name**: Unique; allows English letters, numbers, and `-`. >> Required
* **price_per_day**: Optional.
* **location_url**: URL.>> Required
* **location_text**: Text. >> Required
* **status**: Enum → `["available", "occupied", "in_maintenance"]`.
* **city** : Optional.
* **district**: Optional.
* **lease_information**:
    * **start_date** >> Required
    * **end_date** >> Required
* **details** (JSON): >> Required
  ```json
  {
    "details": [
      {"bedrooms": ""},
      {"bathrooms": ""},
      {"area": ""},
      {"floor": ""}
    ]
  }
  ```
* **owner_id** → Reference `Owner` >> Required
* **tenant_details** → Retrieved from `Tenant` with `tenant_id`
* **rent_details** → Retrieved from `Rent`

---

## Unit Images

### Fields:

* **id**
* **unit_id** → Reference `Unit`
* **image_url**
* Each unit can have **up to 10 images**. >> Required at least one image.

---

## Owners

### Fields:

* **id**
* **name** >> Required
* **address** : optional
* **phone_number** >> Required
* **email**  : optional
* **date_joined** (auto)
* When viewing an owner → list all related **units**.

---

## Tenants

### Fields:

* **id**
* **name** >> Required
* **phone_number** >> Required
* **email** : optional
* **address** >> Required
* **photo**: Optional
* **rate** "1-5" : Optional but start with 5 as base.
* **notes** : Optional

---

## Rent

### Fields:

* **id**
* **tenant_id** → Reference `Tenant`
* **unit_id** → Reference `Unit`
* **price** >> Required
* **start_date** >> Required
* **end_date** >> Required
* **payment_date** 
* **payment_way**: Enum → `["cash", "bank_transfer", "credit_card", "online_payment"]`
* **amount_paid** >> Required
* **payment_status**: Enum → `["paid", "pending", "overdue", "partial"]`

---

## Inventory

### Fields:

* **id**
* **item_name** >> Required 
* **category**: Enum `(still under searching)`)
* **unit_of_measure**: Enum → `["piece", "kg", "liter", "box", "set"] `(still under searching)
* **amount**  >> Required
* **lower_amount**  >> Required
* **unit_price**  >> Required
* **supplier_name** >> optional
* **status**: Enum → `["in_stock", "low_stock", "out_of_stock"]` based on `amount` and `lower_amount`

---

## Owner revnue

### Fields:

* **id**
* **amount** >> Required
* **date** >> Required
* **owner_id** → Reference `Owner` (if applicable)
* **payment_way**: Enum → `["cash", "bank_transfer", "credit_card", "online_payment"]`
* **notes** >> Optional

---

##  Expenses

> Handles recurring or occasional costs like utilities and maintenance.

### Fields:

* **id**
* **unit_id** → Reference `Unit`
* **type**: Enum → `["water", "electricity", "wifi", "maintenance", "other"]`
* **amount**
* **date**
* **status**: Enum → `["paid", "unpaid", "pending"]`

---

## Notifications

> Used for real-time alerts in dashboard/web.

### Trigger Cases:

* When **inventory item** is `out_of_stock` or `low_stock`.
* When **lease end_date** is **≤ 2 months** away.

### Fields:

* **id**
* **title**
* **message**
* **type**: Enum → `["inventory_alert", "lease_alert"]`
* **created_at**

---
## Dashboard Metrics : 
still under searching
