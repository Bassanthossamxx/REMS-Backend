# Notifications API

A concise, practical reference for frontend integration.
This endpoint provides read-only notifications generated from leases and inventory.

---

## Quick Start
- Endpoint: `GET /api/notifications/`
- Auth: `Authorization: Bearer <access_token>` (JWT via SimpleJWT)
- Pagination: PageNumberPagination with `page` param, page size = 20
- Content-Type: `application/json`

Common responses:
- 200 OK, 401 Unauthorized, 403 Forbidden

---

## What generates notifications

On each request to the list endpoint, the backend will:
- Create a notification for each Unit whose `lease_end` is within the next ~60 days
  - Message format: `"Lease for unit '{name}' will end on {YYYY-MM-DD}"`
- Create notifications for inventory items in low/out-of-stock
  - Low stock message: `"Item '{name}' only has {qty} units remaining"`
  - Out of stock message: `"Item '{name}' is out of stock"`
- Clean up notifications older than ~6 months

Notes:
- Duplicates are avoided by `get_or_create(message=...)`. If the same message
  text is produced again later, no duplicate record is created.
- There is no read/unread state at the moment.

---

## Data Model (response shape)

Item fields:
- id: integer (read-only)
- message: string
- created_at: ISO datetime string (UTC)

Ordering:
- Results are always ordered newest-first by `created_at`.

---

## Pagination format

```json
{
  "count": 3,
  "next": "http://<host>/api/notifications/?page=2",
  "previous": null,
  "results": [
    { "id": 1, "message": "...", "created_at": "2025-10-22T12:34:56Z" }
  ]
}
```

---

## Endpoint

### 1) List Notifications

GET `/api/notifications/`

Request headers:
- Authorization: `Bearer <access_token>`
- Accept: `application/json`

Query params:
- page: number (optional, default 1)

Responses:
- 200 OK: Paginated list (see schema above)
- 401 Unauthorized: Missing/invalid token
- 403 Forbidden: User lacks permission (if any custom permissions are added later)

Example 200 OK:
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 42,
      "message": "Lease for unit 'Unit A-101' will end on 2025-12-01",
      "created_at": "2025-10-25T09:15:01Z"
    },
    {
      "id": 41,
      "message": "Item 'AC Filters' only has 3 units remaining",
      "created_at": "2025-10-25T09:12:44Z"
    }
  ]
}
```

Example 401 Unauthorized:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Error handling patterns

- 401 Unauthorized: token missing/expired → redirect to login or refresh token
- 403 Forbidden: role/permission issue → show a descriptive message
- Network errors: retry with backoff; show a non-blocking toast
---
#### **All Rights back to Bassanthossamxx**