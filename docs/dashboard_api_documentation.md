# Dashboard API

A concise reference for admin-only dashboard endpoints: endpoints, auth, fields, and example requests/responses.

---

## Quick Start
- Base: `dashboard/` (no `api/` prefix)
- Endpoints (admin only):
  - `GET /dashboard/home-metrics/?days=30`
  - `GET /dashboard/stock-metrics/`
  - `GET /dashboard/rental-metrics/`
- Auth header (required for all endpoints):
  - `Authorization: Bearer <access_token>`
- Permissions: Admin only (`IsAdminUser`)
- Content types: `application/json`

Common responses:
- `200 OK`
- `401 Unauthorized` — missing/invalid token
- `403 Forbidden` — user is not admin

---

## Authorization
All dashboard endpoints require a valid JWT access token and admin privileges.

Example header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

If you don't yet have a token, see the Auth docs for obtaining `access`/`refresh` tokens and include the `access` token in requests.

---

## 1. Home Metrics

GET `BaseUrl/dashboard/home-metrics/?days=30`

- Description: Summary metrics for the home dashboard.
- Permissions: Admin only
- Query params:
  - `days` (optional, integer, default `30`): Only affects `new_tenants`. Other metrics are overall or snapshot.

Response fields:

| Field                   | Type    | Description |
| ----------------------- | ------- | ----------- |
| total_units             | integer | Total number of units (current snapshot) |
| total_units_occupied    | integer | Units currently occupied (status = `occupied`) |
| total_revenue           | number  | Company revenue from all paid rents (overall). Computed as sum of `total_amount * (1 - owner_percentage/100)` |
| pending_payments        | number  | Sum of `total_amount` for all pending rents (overall) |
| new_tenants             | integer | Tenants created in the last `days` (default 30) |

Example request (curl):

```bash
curl -X GET "BaseUrl/dashboard/home-metrics/?days=30" ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Accept: application/json"
```

Example response (200):

```json
{
  "total_units": 125,
  "total_units_occupied": 74,
  "total_revenue": 64000.0,
  "pending_payments": 8200.0,
  "new_tenants": 9
}
```

Notes:
- Values are computed live on each request. There is no caching.
- Only `new_tenants` respects the `days` param; other metrics are overall (or current snapshot).

---

## 2. Stock Metrics

GET `BaseUrl/dashboard/stock-metrics/`

- Description: Inventory stock overview.
- Permissions: Admin only

Response fields:

| Field               | Type    | Description |
| ------------------- | ------- | ----------- |
| total_items         | integer | Total items posted in inventory |
| in_stock_items      | integer | Items with status = `In Stock` |
| out_of_stock_items  | integer | Items with status = `Out of Stock` |
| low_stock_items     | integer | Items with status = `Low Stock` |

Example request (curl):

```bash
curl -X GET "BaseUrl/dashboard/stock-metrics/" ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Accept: application/json"
```

Example response (200):

```json
{
  "total_items": 48,
  "in_stock_items": 31,
  "out_of_stock_items": 7,
  "low_stock_items": 10
}
```

---

## 3. Rental Management Metrics

GET `BaseUrl/dashboard/rental-metrics/`

- Description: Payment totals for rents by status.
- Permissions: Admin only

Response fields:

| Field           | Type   | Description |
| --------------- | ------ | ----------- |
| total_collected | number | Sum of `total_amount` for paid rents |
| pending         | number | Sum of `total_amount` for pending rents |
| overdue         | number | Sum of `total_amount` for overdue rents |

Example request (curl):

```bash
curl -X GET "http://localhost:8000/rental-metrics/" ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Accept: application/json"
```

Example response (200):

```json
{
  "total_collected": 51200.0,
  "pending": 8200.0,
  "overdue": 3600.0
}
```

---

## Errors
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Authenticated but not an admin user

---
#### All Rights Back to Bassanthossamxx
