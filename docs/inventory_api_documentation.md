# Inventory (Stock) API

A single, complete reference for frontend developers. Covers endpoints, fields, required/optional params, filters/search, pagination, auth, and example requests/responses.

---

## Contents

- Quick Start
- Enums and Constraints
- Pagination Format
- 1. Stock Items
  - 1.1 List Stock
  - 1.2 Retrieve Stock Item
  - 1.3 Create Stock Item
  - 1.4 Update Stock Item (PUT/PATCH)
  - 1.5 Delete Stock Item
  - Notes (Stock)

---

## Quick Start
- API Base: `/api/stock/`
- Auth header (required for all endpoints):
  `Authorization: Bearer <access_token>`
- Content types:
  `application/json`
- Pagination: `PageNumberPagination (page=1..)` — default page size = 20
- Permissions: Admin only (`IsAdminUser`)

Common responses:
- `200 OK`, `201 Created`, `204 No Content`
- `400 Bad Request (validation)`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`

---

## Enums and Constraints

These are server-side choices used by the Inventory model.

- category: one of
  - `Maintenance`, `Electrical`, `Plumbing`, `Security`, `Cleaning`, `Furniture`
- unit_of_measure: one of
  - `Pieces`, `Boxes`, `Gallons`, `Liters`, `Kits`, `Sets`, `Meters`, `Feet`
- status (read-only, computed by backend):
  - `In Stock`, `Low Stock`, `Out of Stock`

---

## Pagination Format

```json
{
  "count": 123,
  "next": "http://<host>/api/stock/?page=2",
  "previous": null,
  "results": []
}
```

---

# 1. Stock Items

Base: `/api/stock/`

Permissions: Admin only (`IsAdminUser`)

### Model Fields (Request/Response)

| Field           | Type    | Required | Read-only | Constraints / Notes |
| --------------- | ------- | -------- | --------- | ------------------- |
| id              | integer | —        | yes       | Auto generated |
| name            | string  | yes      | no        | Max 100 chars |
| description     | string  | no       | no        | Optional text |
| category        | string  | yes      | no        | Choices: see Enums |
| quantity        | integer | yes      | no        | Positive integer (>= 0) |
| lower_quantity  | integer | yes      | no        | Threshold for low stock (>= 0) |
| unit_of_measure | string  | yes      | no        | Choices: see Enums |
| unit_price      | decimal | yes      | no        | `max_digits=10`, `decimal_places=2` |
| total_value     | decimal | —        | yes       | Computed: `quantity * unit_price`; `max_digits=12`, `decimal_places=2` |
| supplier_name   | string  | no       | no        | Optional, max 255 chars |
| status          | string  | —        | yes       | Computed from `quantity` vs `lower_quantity`: `In Stock` / `Low Stock` / `Out of Stock` |
| created_at      | datetime| —        | yes       | ISO 8601 |
| updated_at      | datetime| —        | yes       | ISO 8601 |

Notes:
- `status` and `total_value` are computed by the server on create/update. Do not send them in requests.
- If `quantity == 0` → `status = Out of Stock`; if `0 < quantity <= lower_quantity` → `Low Stock`; else `In Stock`.
- Decimal fields are returned as JSON strings by DRF (e.g., `"12.50"`).

---

### Filters and Search (List endpoint)

- Filters (exact): `category`, `status`
- Search (partial, case-insensitive): `search` across `name`, `category`, `supplier_name`, `status`
- Ordering: not supported on this endpoint.

Examples:
- `/api/stock/?category=Maintenance`
- `/api/stock/?status=Low%20Stock`
- `/api/stock/?search=cable`

---

## 1.1 List Stock

GET `/api/stock/`

Query params:
- `page`: page number (default 1)
- `category`: filter by category
- `status`: filter by computed status
- `search`: search across name/category/supplier_name/status

Response 200 OK (paginated):

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "name": "LED Bulb E27",
      "description": "Warm white 12W",
      "category": "Electrical",
      "quantity": 50,
      "lower_quantity": 10,
      "unit_of_measure": "Pieces",
      "unit_price": "2.50",
      "total_value": "125.00",
      "supplier_name": "BrightCo",
      "status": "In Stock",
      "created_at": "2025-10-01T09:12:11Z",
      "updated_at": "2025-10-01T09:12:11Z"
    },
    {
      "id": 11,
      "name": "PVC Pipe 1/2\"",
      "description": null,
      "category": "Plumbing",
      "quantity": 2,
      "lower_quantity": 5,
      "unit_of_measure": "Meters",
      "unit_price": "3.00",
      "total_value": "6.00",
      "supplier_name": null,
      "status": "Low Stock",
      "created_at": "2025-10-05T10:20:00Z",
      "updated_at": "2025-10-05T10:20:00Z"
    }
  ]
}
```

Errors:
- `401 Unauthorized` if missing/invalid token
- `403 Forbidden` if not admin

---

## 1.2 Retrieve Stock Item

GET `/api/stock/{id}/`

Response 200 OK:

```json
{
  "id": 11,
  "name": "PVC Pipe 1/2\"",
  "description": null,
  "category": "Plumbing",
  "quantity": 2,
  "lower_quantity": 5,
  "unit_of_measure": "Meters",
  "unit_price": "3.00",
  "total_value": "6.00",
  "supplier_name": null,
  "status": "Low Stock",
  "created_at": "2025-10-05T10:20:00Z",
  "updated_at": "2025-10-05T10:20:00Z"
}
```

Errors:
- `404 Not Found` if id does not exist
- `401/403` as above

---

## 1.3 Create Stock Item

POST `/api/stock/`

Content-Type: `application/json`

Required fields: `name, category, quantity, lower_quantity, unit_of_measure, unit_price`

Optional: `description, supplier_name`

Example request body:

```json
{
  "name": "Dish Soap 1L",
  "description": "Lemon scented",
  "category": "Cleaning",
  "quantity": 24,
  "lower_quantity": 6,
  "unit_of_measure": "Liters",
  "unit_price": "1.75",
  "supplier_name": "CleanPlus"
}
```

201 Created (full object):

```json
{
  "id": 25,
  "name": "Dish Soap 1L",
  "description": "Lemon scented",
  "category": "Cleaning",
  "quantity": 24,
  "lower_quantity": 6,
  "unit_of_measure": "Liters",
  "unit_price": "1.75",
  "total_value": "42.00",
  "supplier_name": "CleanPlus",
  "status": "In Stock",
  "created_at": "2025-10-24T12:00:00Z",
  "updated_at": "2025-10-24T12:00:00Z"
}
```

400 Bad Request (examples):

```json
{
  "category": ["\"Gardening\" is not a valid choice."],
  "unit_of_measure": ["This field is required."],
  "quantity": ["A valid integer is required."]
}
```

---

## 1.4 Update Stock Item (PUT/PATCH)

PUT/PATCH `/api/stock/{id}/`

- Send only updatable fields: `name, description, category, quantity, lower_quantity, unit_of_measure, unit_price, supplier_name`
- Do not send read-only: `id, total_value, status, created_at, updated_at`
- The server recomputes `total_value` and `status` on every update.

PATCH example:

```json
{
  "quantity": 0
}
```

200 OK (full object, after recompute):

```json
{
  "id": 11,
  "name": "PVC Pipe 1/2\"",
  "description": null,
  "category": "Plumbing",
  "quantity": 0,
  "lower_quantity": 5,
  "unit_of_measure": "Meters",
  "unit_price": "3.00",
  "total_value": "0.00",
  "supplier_name": null,
  "status": "Out of Stock",
  "created_at": "2025-10-05T10:20:00Z",
  "updated_at": "2025-10-24T12:10:30Z"
}
```

Errors:
- `404 Not Found` if id does not exist
- `400 Bad Request` for invalid choices/types

---

## 1.5 Delete Stock Item

DELETE `/api/stock/{id}/`

Response:
- `204 No Content` on success
- `404 Not Found` if id not found

---

## Notes (Stock)

- `status` is derived; you cannot set it manually.
- `total_value = quantity * unit_price` is recalculated on every save.
- Use `lower_quantity` to trigger `Low Stock` when quantity is at or below the threshold.
- Search is partial and case-insensitive across `name`, `category`, `supplier_name`, `status`.
- Ordering by fields is not enabled on this endpoint.
___
#### **all rights back to bassanthossamxx**