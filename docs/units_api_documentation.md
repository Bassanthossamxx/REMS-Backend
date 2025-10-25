#  Units, Cities & Districts API

A single, clean reference for frontend developers.
It covers endpoints, required fields, enums, filtering, ordering, pagination, auth header, and common responses.

---

## Contents

* [Quick Start](#quick-start)
* [Enums and Constraints](#enums-and-constraints)
* [Pagination Format](#pagination-format)
* [1. Units](#1-units)

  * [1.1 List Units](#11-list-units)
  * [1.2 Retrieve Unit](#12-retrieve-unit)
  * [1.3 Create Unit](#13-create-unit)
  * [1.4 Update Unit](#14-update-unit)
  * [1.5 Delete Unit](#15-delete-unit)
  * [Notes (Units)](#notes-units)
* [2. Cities](#2-cities)
* [3. Districts](#3-districts)

---

## Quick Start

* Base URL: `http://<host>/`
* Auth header (required for all endpoints):
  `Authorization: Bearer <access_token>`
* Content types:
  `application/json` or `multipart/form-data` (for file uploads)
* Pagination:
  `PageNumberPagination (page=1..)` — page size = 20

Common responses:

* `200 OK`, `201 Created`, `204 No Content`
* `400 Bad Request (validation)`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`

---

## Enums and Constraints

* Unit status: `available | occupied | in_maintenance`
* Unit type: `apartment | villa | office | shop | studio | penthouse | warehouse | retail`
* location_url: must be a valid map link (Google/Apple Maps)
  e.g. `google.com/maps`, `maps.app.goo.gl`, `goo.gl/maps`, `maps.apple.com`

---

## Pagination Format

```json
{
  "count": 123,
  "next": "baseurl/api/units/?page=2",
  "previous": null,
  "results": []
}
```

# 1. Units

**Base:** `/api/units/`
**Permissions:** Admin only (`IsAdminUser`)

---

### Model Fields (Request/Response)

| Field            | Type                 | Notes                                                                                         |
| ---------------- | -------------------- | --------------------------------------------------------------------------------------------- |
| id               | integer              | read-only                                                                                     |
| name             | string               | unique, required                                                                              |
| owner            | integer              | Owner id, required                                                                            |
| city             | integer              | City id, required                                                                             |
| district         | integer              | District id, required                                                                         |
| location_url     | string               | valid Google/Apple Maps URL, required                                                         |
| location_text    | string               | required                                                                                      |
| lease_start      | date                 | required, date format `YYYY-MM-DD`                                                            |
| lease_end        | date                 | required, date format `YYYY-MM-DD`                                                            |
| status           | string               | default: available                                                                            |
| type             | string               | required                                                                                      |
| bedrooms         | integer              | >= 0, required                                                                                |
| bathrooms        | integer              | >= 0, required                                                                                |
| area             | integer              | >= 0, required                                                                                |
| price_per_day    | decimal              | default 0                                                                                     |
| owner_percentage | decimal              | 0..100 (default 0)                                                                            |
| images (request) | array of files       | write-only, optional (replaces existing on update)                                            |
| images (response)| array of strings     | response-only list of image URLs                                                              |
| Extra            | response only        | `details { type, bedrooms, bathrooms, area }`                                                 |
| Extra            | response only        | `payments_summary { total_occasional_payment, total_occasional_payment_last_month, last_month_payments[] }` |
| Extra            | response only        | `unit_payment_summary { unit_id, unit_name, owner_id, owner_name, owner_percentage, total_this_month, total, total_occasional_this_month, total_occasional, total_after_occasional_this_month, total_after_occasional, company_total_this_month, company_total }` |
| Extra            | response only        | `rent_payment_history[]` — list of `{ amount, date, status }` (date format `YYYY-MM-DD`, most recent first) |

---

### 1.1 List Units

**GET** `/api/units/`

**Filters:**
`type`, `city`, `district`, `status`,
`from_date=YYYY-MM-DD`, `to_date=YYYY-MM-DD`

**Ordering:**
`ordering=name` or `ordering=-price_per_day`
(Multiple supported, e.g. `ordering=city,-area`)

**Pagination:** `page=1..`

**Response 200 OK (paginated)**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "name": "Unit A-101",
      "location_text": "5th Avenue, Building 2",
      "city_name": "Cairo",
      "district_name": "Nasr City",
      "current_tenant_name": null,
      "price_per_day": "120.00",
      "type": "apartment",
      "status": "available"
    },
    {
      "name": "Unit B-202",
      "location_text": "Downtown",
      "city_name": "Giza",
      "district_name": "Dokki",
      "current_tenant_name": "John Doe",
      "price_per_day": "180.00",
      "type": "villa",
      "status": "occupied"
    }
  ]
}
```

---

### 1.2 Retrieve Unit

**GET** `/api/units/{id}/`

```json
{
  "id": 12,
  "name": "Unit A-101",
  "owner": 3,
  "city": 1,
  "district": 5,
  "location_url": "https://www.google.com/maps/place/...",
  "location_text": "5th Avenue, Building 2",
  "lease_start": "2025-05-01",
  "lease_end": "2026-05-01",
  "status": "available",
  "type": "apartment",
  "bedrooms": 2,
  "bathrooms": 1,
  "area": 90,
  "price_per_day": "120.00",
  "owner_percentage": "30.00",
  "details": { "type": "apartment", "bedrooms": 2, "bathrooms": 1, "area": 90 },
  "images": [
    "/media/units/12/image-1.jpg",
    "/media/units/12/image-2.jpg"
  ],
  "payments_summary": {
    "total_occasional_payment": "275.50",
    "total_occasional_payment_last_month": "95.50",
    "last_month_payments": [
      {
        "id": 11,
        "unit": 12,
        "category": "maintenance",
        "amount": "95.50",
        "payment_method": "cash",
        "payment_date": "2025-09-14",
        "notes": null,
        "created_at": "2025-09-14T08:00:00Z",
        "updated_at": "2025-09-14T08:00:00Z"
      }
    ]
  },
  "unit_payment_summary": {
    "unit_id": 12,
    "unit_name": "A-101",
    "owner_id": 3,
    "owner_name": "Ahmed Ali",
    "owner_percentage": "0.6000",
    "total_this_month": "10000.00",
    "total": "100000.00",
    "total_occasional_this_month": "1000.00",
    "total_occasional": "2000.00",
    "total_after_occasional_this_month": "9000.00",
    "total_after_occasional": "98000.00",
    "company_total_this_month": "3600.00",
    "company_total": "39200.00"
  },
  "rent_payment_history": [
    { "amount": "1200.00", "date": "2025-09-30", "status": "paid" },
    { "amount": "800.00", "date": "2025-08-31", "status": "pending" }
  ]
}
```

---

### 1.3 Create Unit

**POST** `/api/units/`

Content-Type:

* `application/json` (no images)
* `multipart/form-data` (with images)

**Required fields:**
`name, owner, city, district, location_url, location_text, lease_start, lease_end, type, bedrooms, bathrooms, area`

**Optional:**
`status, price_per_day, owner_percentage, images[]`

**201 Created**

```json
{
  "id": 12,
  "name": "Unit A-101"
}
```

**400 Bad Request (example)**

```json
{
  "lease_start": ["This field is required."],
  "lease_end": ["This field is required."],
  "location_url": ["Invalid map URL."]
}
```

---

### 1.4 Update Unit

**PUT/PATCH** `/api/units/{id}/`

JSON or multipart/form-data
If images provided → replaces all.

**200 OK**

(same structure as [Retrieve Unit](#12-retrieve-unit))

---

### 1.5 Delete Unit

**DELETE** `/api/units/{id}/`
→ `204 No Content`

---

### Notes (Units)

* `lease_start` / `lease_end` reflect when the owner gave the unit to the company (not tenant leases).
* Images upload are write-only in requests; responses include a list of image URLs under `images`.
* `unit_payment_summary` provides embedded analytics for the unit (rent totals, deductions, owner/company shares). The same analytics are also available via the standalone endpoint `GET /api/all/payments/unit/{unit_id}/`.
* Use filters for `from_date` and `to_date` to find available units in a range.
* List endpoint is compact; retrieve gives full details.
* `rent_payment_history` lists all rents for the unit with `{ amount, date, status }`, sorted most recent first by `payment_date`; `date` uses the `YYYY-MM-DD` format.

---


# 2. Cities

Base: `/api/cities/`

Permissions: Admin only (`IsAdminUser`)

---

### Fields (City)

* `id` (read-only)
* `name` (required, unique)
* `created_at`, `updated_at` (read-only)
* `districts`: array of district names (read-only convenience field)

---

### 2.1 List Cities

GET `/api/cities/`

200 OK (paginated)

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": []
}
```

---

### 2.2 Retrieve City

GET `/api/cities/{id}/`

```json
{
  "id": 1,
  "name": "Cairo"
}
```

---

### 2.3 Create City

POST `/api/cities/`

201 Created

```json
{
  "id": 1,
  "name": "Cairo"
}
```

---

### 2.4 Update City

PUT/PATCH `/api/cities/{id}/`

200 OK (same shape as retrieve)

---

### 2.5 Delete City

DELETE `/api/cities/{id}/`
→ `204 No Content`

---

# 3. Districts

Base: `/api/districts/`

Permissions: Admin only (`IsAdminUser`)

---

### Fields (District)

* `id` (read-only)
* `name` (required)
* `city` (City id, required)
* `city_name` (read-only)
* `created_at`, `updated_at` (read-only)

---

### 3.1 List Districts

GET `/api/districts/`

200 OK (paginated)

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": []
}
```

---

### 3.2 Retrieve District

GET `/api/districts/{id}/`

```json
{
  "id": 5,
  "name": "Nasr City"
}
```

---

### 3.3 Create District

POST `/api/districts/`

201 Created

```json
{
  "id": 6,
  "name": "Zamalek"
}
```

400 Bad Request (examples)

```json
{
  "city": ["City is required."],
  "name": ["This field may not be blank."]
}
```

---

### 3.4 Update District

PUT/PATCH `/api/districts/{id}/`

200 OK (same shape as retrieve)

---

### 3.5 Delete District

DELETE `/api/districts/{id}/`
→ `204 No Content`

---
#### **all rights back to bassanthossamxx**
