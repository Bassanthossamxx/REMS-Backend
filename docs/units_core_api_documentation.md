# Units, Cities & Districts API

A single, clean reference for frontend developers. It covers endpoints, required fields, enums, filtering, ordering, pagination, auth header, and common responses.

---

## Contents

- [Quick Start](#quick-start)
- [Enums and Constraints](#enums-and-constraints)
- [Pagination Format](#pagination-format)
- [1. Units](#1-units)
  - [1.1 List Units](#11-list-units)
  - [1.2 Retrieve Unit](#12-retrieve-unit)
  - [1.3 Create Unit](#13-create-unit)
  - [1.4 Update Unit](#14-update-unit)
  - [1.5 Delete Unit](#15-delete-unit)
  - [Notes (Units)](#notes-units)
- [2. Cities](#2-cities)
  - [Fields (City)](#fields-city)
  - [2.1 List Cities](#21-list-cities)
  - [2.2 Retrieve City](#22-retrieve-city)
  - [2.3 Create City](#23-create-city)
  - [2.4 Update City](#24-update-city)
  - [2.5 Delete City](#25-delete-city)
- [3. Districts](#3-districts)
  - [Fields (District)](#fields-district)
  - [3.1 List Districts](#31-list-districts)
  - [3.2 Retrieve District](#32-retrieve-district)
  - [3.3 Create District](#33-create-district)
  - [3.4 Update District](#34-update-district)
  - [3.5 Delete District](#35-delete-district)
- [Examples (curl)](#examples-curl)
- [Notes & Caveats](#notes--caveats)

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
* Occasional payment types (FYI only): `maintenance | repair | cleaning | other`
* location_url: must be a valid map link (Google/Apple Maps)
  e.g. `google.com/maps`, `maps.app.goo.gl`, `goo.gl/maps`, `maps.apple.com`

---

## Pagination Format

```json
{
  "count": 123,
  "next": "http://<host>/api/units/?page=2",
  "previous": null,
  "results": []
}
```

---

# 1. Units

Base: `/api/units/`

Permissions: Admin only (`IsAdminUser`)

### Model Fields (Request/Response)

| Field               | Type           | Notes                                              |
| ------------------- | -------------- | -------------------------------------------------- |
| id                  | integer        | read-only                                          |
| name                | string         | unique, required                                   |
| owner               | integer        | Owner id, required                                 |
| city                | integer        | City id, required                                  |
| district            | integer        | District id, required                              |
| location_url        | string         | valid Google/Apple Maps URL, required              |
| location_text       | string         | required                                           |
| status              | string         | default: available                                 |
| type                | string         | required                                           |
| bedrooms            | integer        | >= 0, required                                     |
| bathrooms           | integer        | >= 0, required                                     |
| area                | integer        | >= 0, required                                     |
| price_per_day       | decimal        | default 0                                          |
| owner_percentage    | decimal        | 0..100 (default 0)                                 |
| total_rent          | decimal        | read-only                                          |
| total_occasional    | decimal        | read-only                                          |
| total_owner_revenue | decimal        | read-only                                          |
| total_my_revenue    | decimal        | read-only                                          |
| images              | array of files | write-only, optional (replaces existing on update) |
| Extra               | response only  | `details { type, bedrooms, bathrooms, area }`      |

---

### 1.1 List Units

GET `/api/units/`

Filters: `type, city, district, status, from_date=YYYY-MM-DD, to_date=YYYY-MM-DD`

Ordering: `ordering=name` or `ordering=-price_per_day` (multiple supported, e.g. `ordering=city,-area`)

Pagination: `page=1..`

200 OK (paginated)

Returns a compact projection per unit with these fields only:

- name (string)
- location_text (string)
- city_name (string)
- district_name (string)
- current_tenant_name (string or null if no active tenant)
- price_per_day (decimal as string)
- type (string)
- status (string)

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

> Note: The list endpoint returns a compact payload. Use [Retrieve Unit](#12-retrieve-unit) for the full detailed shape.

---

### 1.2 Retrieve Unit

GET `/api/units/{id}/`

```json
{
  "id": 12,
  "name": "Unit A-101",
  "owner": 3,
  "city": 1,
  "district": 5,
  "location_url": "https://www.google.com/maps/place/...",
  "location_text": "5th Avenue, Building 2",
  "status": "available",
  "type": "apartment",
  "bedrooms": 2,
  "bathrooms": 1,
  "area": 90,
  "price_per_day": "120.00",
  "owner_percentage": "30.00",
  "total_rent": "0.00",
  "total_occasional": "0.00",
  "total_owner_revenue": "0.00",
  "total_my_revenue": "0.00",
  "details": { "type": "apartment", "bedrooms": 2, "bathrooms": 1, "area": 90 }
}
```

---

### 1.3 Create Unit

POST `/api/units/`

Content-Type:

* `application/json` (no images)
* `multipart/form-data` (with images)

Required fields:
`name, owner, city, district, location_url, location_text, type, bedrooms, bathrooms, area`

Optional:
`status, price_per_day, owner_percentage, images[]`

201 Created

```json
{
  "id": 12,
  "name": "Unit A-101"
}
```

400 Bad Request (examples)

```json
{
  "location_url": ["Invalid map URL. Please provide a valid map link."],
  "type": ["This field is required."],
  "bedrooms": ["A valid integer is required."]
}
```

---

### 1.4 Update Unit

PUT/PATCH `/api/units/{id}/`

* JSON or multipart/form-data
* PATCH: send only changed fields (if images provided → replaces all)

200 OK (same shape as retrieve)

---

### 1.5 Delete Unit

DELETE `/api/units/{id}/`
→ `204 No Content`

---

### Notes (Units)

* List endpoint returns a compact shape: `name, location_text, city_name, district_name, current_tenant_name (null if none), price_per_day, type, status`.
* Use retrieve to get the full unit details.
* Images are write-only: accepted on create/update, not returned in GET.
* `from_date` and `to_date` include units with no rents.

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

# Examples (curl)

> Replace `<host>` and tokens as needed. Use `^` as line continuation on Windows CMD.

---

### List units (first page)

```bash
curl -X GET "http://<host>/api/units/?page=1" ^
  -H "Authorization: Bearer <access_token>"
```

### Filter units by city and type

```bash
curl -X GET "http://<host>/api/units/?city=1&type=apartment&ordering=-price_per_day" ^
  -H "Authorization: Bearer <access_token>"
```

### Create a unit (JSON)

```bash
curl -X POST http://<host>/api/units/ ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Unit A-101\", ... }"
```

### Create a unit (multipart with images)

```bash
curl -X POST http://<host>/api/units/ ^
  -H "Authorization: Bearer <access_token>" ^
  -F "name=Unit A-101" ^
  ...
  -F "images=@C:\\path\\to\\image1.jpg"
```

### Update a unit

```bash
curl -X PATCH http://<host>/api/units/12/ ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"status\":\"in_maintenance\",\"price_per_day\":150}"
```

### Delete a unit

```bash
curl -X DELETE http://<host>/api/units/12/ ^
  -H "Authorization: Bearer <access_token>"
```

### Create a city

```bash
curl -X POST http://<host>/api/cities/ ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Cairo\"}"
```

### Create a district

```bash
curl -X POST http://<host>/api/districts/ ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Nasr City\",\"city\":1}"
```

---

# Notes & Caveats

* Images are not returned in GET responses.
* Date filters (`from_date` / `to_date`) include units with no rents.
* District creation requires an existing city id.
* Write endpoints return standard DRF validation errors (400).

---

