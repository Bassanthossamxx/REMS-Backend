# Tenants API Documentation

This document describes the Tenants API, including listing tenants, retrieving tenant details, and managing tenant reviews.

## Base URL
```
baseurl/api/
```

## Authentication & Permissions
- All endpoints require authentication and `IsAdminUser` permission unless noted.
- Include a valid JWT access token in the Authorization header: `Authorization: Bearer <token>`.

## Endpoints

### 1. List Tenants
**GET** `/tenants/`

Returns a paginated list of tenants with summary fields and nearest/current rent info.

#### Query parameters
- `search`: case-insensitive search across tenant full name and related unit name (SearchFilter over `[full_name, rents__unit__name]`).
- `status`: filter by tenant lifecycle status (`active`, `completed`, `inactive`).
- Standard pagination: `page`, `page_size`.

#### Response item:
```json
{
  "id": 1,
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "1234567890",
  "rate": 4.5,
  "address": "123 Main St",
  "status": "active",
  "rent_info": {
    "id": 10,
    "unit": 3,
    "tenant": 1,
    "rent_start": "2025-01-01",
    "rent_end": "2025-12-31",
    "total_amount": 12000.0,
    "payment_status": "paid",
    "payment_method": "card",
    "payment_date": "2025-01-01",
    "status": "active",
    "notes": null,
    "attachment": null,
    "created_at": "2025-01-02T10:00:00Z",
    "unit_name": "Unit A",
    "unit_type": "Apartment",
    "tenant_name": "John Doe",
    "tenant_email": "john.doe@example.com",
    "tenant_phone": "1234567890",
    "duration": "12 months"
  }
}
```

**Notes:**
- The list response does NOT include full rent history or reviews.

### 2. Retrieve Tenant Details
**GET** `/tenants/{id}/`

Returns tenant details including full rent history and reviews.

#### Response:
```json
{
  "id": 1,
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "1234567890",
  "rate": 4.3,
  "address": "123 Main St",
  "status": "active",
  "rent_info": { ... },
  "rents": [
    {
      "id": 10,
      "unit": 3,
      "tenant": 1,
      "rent_start": "2025-01-01",
      "rent_end": "2025-12-31",
      "total_amount": 12000.0,
      "payment_status": "paid",
      "payment_method": "card",
      "payment_date": "2025-01-01",
      "status": "active",
      "notes": null,
      "attachment": null,
      "created_at": "2025-01-02T10:00:00Z",
      "unit_name": "Unit A",
      "unit_type": "Apartment",
      "tenant_name": "John Doe",
      "tenant_email": "john.doe@example.com",
      "tenant_phone": "1234567890",
      "duration": "12 months"
    }
  ],
  "reviews": [
    { "comment": "Great tenant", "rate": 4.5, "date": "2025-10-25" },
    { "comment": "Paid on time", "rate": 5.0, "date": "2025-10-20" }
  ]
}
```

**Notes:**
- `reviews` items include: `comment` (string), `rate` (number), `date` (yyyy-mm-dd).
- `rate` is the tenant average across all reviews, recalculated automatically on review create/update/delete.

### 3. Create Tenant
**POST** `/tenants/`

Create a new tenant.

#### Request body:
```json
{
  "full_name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "0987654321",
  "rate": 5.0,
  "address": "456 Elm St"
}
```

#### Response:
```json
{
  "id": 2,
  "full_name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "0987654321",
  "rate": 5.0,
  "address": "456 Elm St",
  "status": "inactive",
  "rent_info": null
}
```

### 4. Update Tenant
**PUT/PATCH** `/tenants/{id}/`

Update an existing tenant's details.

#### Request body:
```json
{
    "full_name": "Jane Smith",
    "email": "jane.smith@example.com",
    "rate": 3.8
}
```

#### Response:
```json
{
    "id": 2,
    "full_name": "Jane Smith",
    "email": "jane.smith@example.com",
    "phone": "0987654321",
    "rate": 3.8,
    "address": "456 Elm St",
    "status": "inactive",
    "rent_info": null
}
```

### 5. Delete Tenant
**DELETE** `/tenants/{id}/`

Delete a tenant by their ID.

#### Response:
```json
{
    "detail": "Tenant deleted successfully."
}
```

### 6. Reviews CRUD
- All reviews endpoints are under `tenants/reviews`.

**List reviews**
- **GET** `/tenants/reviews/`
- Optional filters: `tenant` (e.g., `/tenants/reviews/?tenant=1`)

**Create review**
- **POST** `/tenants/reviews/`

#### Request body:
```json
{
  "tenant": 1,
  "comment": "lgtm",
  "rate": 4.5
}
```

#### Response:
```json
{
  "id": 5,
  "tenant": 1,
  "comment": "lgtm",
  "rate": 4.5,
  "date": "2025-10-25"
}
```

**Retrieve review**
- **GET** `/tenants/reviews/{id}/`

**Update review**
- **PUT/PATCH** `/tenants/reviews/{id}/`

**Delete review**
- **DELETE** `/tenants/reviews/{id}/`

**Behavior:**
- When a review is created, updated, or deleted, the tenant's average rate is recomputed and saved to `tenant.rate` (1 decimal). When no reviews exist, rate defaults to 5.0.

## Search & Filtering
- Tenants list supports search across `full_name` and `rents__unit__name`.
- Reviews list supports search across tenant full name and review comment; filter by tenant via `?tenant=ID`.

## Status Field
- `status` reflects tenant lifecycle derived from rents:
  - `active`: has a rent that includes today
  - `completed`: has past rents only (no active or upcoming)
  - `inactive`: no rents or only upcoming rents

---
All rights reserved to the project owner.
