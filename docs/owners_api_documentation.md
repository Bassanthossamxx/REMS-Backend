# Owners API Documentation

This document describes the Owners endpoints, request/response shapes, validation, and examples for frontend integration.

Base URL prefix: `/api/`

Authentication and permissions:
- Authentication: JWT Bearer token required in the `Authorization` header: `Authorization: Bearer <token>`
- Permissions: Admin users only (non-admin users will receive HTTP 403 Forbidden)

Pagination:
- The list endpoint uses page-number pagination
- Query parameter: `page` (default page size is 20)
- Response shape: `{ count, next, previous, results: [...] }`

---

## Owner object shape

Fields present in list and detail responses:
- `id` (integer)
- `full_name` (string, unique, required)
- `phone` (string, unique, required)
- `email` (string, unique, optional; may be null)
- `address` (string, optional; may be null)
- `rate` (decimal as string, one decimal place allowed; must be between 1.0 and 5.0 inclusive)
- `date_joined` (ISO 8601 datetime, read-only)
- `updated_at` (ISO 8601 datetime, read-only)
- `units_count` (integer, computed)
- `total_revenue` (decimal string with 2 fraction digits, computed)
- `monthly_revenue` (decimal string with 2 fraction digits, computed)
- `units` (array of unit summary objects, computed)

Unit summary object fields (inside `units`):
- `id` (integer)
- `name` (string)
- `status` (string, e.g., `available` or `occupied`)
- `price_per_day` (decimal string with 2 fraction digits)
- `tenant_name` (string or null; active tenant if present, otherwise latest tenant)
- `rent_price` (decimal string or null; from active/latest rent)
- `rent_start` (ISO 8601 date or null)
- `rent_end` (ISO 8601 date or null)
- `address` (string; unit location text)
- `city_name` (string or null)
- `district_name` (string or null)
- `location_url` (string URL)
- `cover_photo` (string URL or null; first image if any)

Revenue calculation notes:
- `total_revenue`: Sum of the owner’s share across all rents for this owner’s units, where share = `rent.total_amount * (unit.owner_percentage / 100)`
- `monthly_revenue`: Same share formula but only for rents created in the current month (based on `Rent.created_at`)

Validation rules:
- `full_name`, `phone`, `email` must be unique across owners (email is optional; multiple null emails are allowed at the database level)
- `rate` must be between 1.0 and 5.0 (inclusive); values like `2.5` are allowed

---

## List Owners

GET `/api/owners/`

Headers:
- `Authorization: Bearer <token>`

Query parameters:
- `page` (optional): page number
- `search` (optional): case-insensitive partial match on owner `full_name`
  - Examples: `?search=John`, `?search=doe`

Response 200 (application/json):
```
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 12,
      "full_name": "John Doe",
      "phone": "+15551234567",
      "email": "john@example.com",
      "address": "123 Main St, City",
      "rate": "4.5",
      "date_joined": "2025-10-10T09:43:12Z",
      "updated_at": "2025-10-21T19:05:30Z",
      "units_count": 2,
      "total_revenue": "13500.00",
      "monthly_revenue": "4500.00",
      "units": [
        {
          "id": 101,
          "name": "Unit A-11",
          "status": "occupied",
          "price_per_day": "150.00",
          "tenant_name": "Alice Smith",
          "rent_price": "3000.00",
          "rent_start": "2025-10-01",
          "rent_end": "2025-10-20",
          "address": "Near Central Park",
          "city_name": "Cairo",
          "district_name": "Nasr City",
          "location_url": "https://maps.example.com/?q=...",
          "cover_photo": "https://res.cloudinary.com/.../image/upload/v.../unit_a11.jpg"
        }
      ]
    }
  ]
}
```



Errors:
- 401 Unauthorized if missing/invalid token
- 403 Forbidden if user is not an admin

---

## Create Owner

POST `/api/owners/`

Headers:
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

Request body:
```
{
  "full_name": "John Doe",
  "phone": "+15551234567",
  "email": "john@example.com",
  "address": "123 Main St, City",
  "rate": 4.5
}
```

Notes:
- `full_name` (required, unique)
- `phone` (required, unique)
- `email` (optional, unique)
- `rate` (optional; defaults to 5.0; must be between 1.0 and 5.0)

Response 201 (application/json): returns the full Owner object including computed fields (see Owner object shape)

Example 201 response:
```
{
  "id": 12,
  "full_name": "John Doe",
  "phone": "+15551234567",
  "email": "john@example.com",
  "address": "123 Main St, City",
  "rate": "4.5",
  "date_joined": "2025-10-10T09:43:12Z",
  "updated_at": "2025-10-21T19:05:30Z",
  "units_count": 0,
  "total_revenue": "0.00",
  "monthly_revenue": "0.00",
  "units": []
}
```

Validation error examples (400 Bad Request):
- Duplicate phone:
```
{
  "phone": ["owner with this phone already exists."]
}
```
- Invalid rate:
```
{
  "rate": ["Rate must be between 1.0 and 5.0."]
}
```

Other errors:
- 401 Unauthorized
- 403 Forbidden

---

## Retrieve Owner

GET `/api/owners/{id}/`

Headers:
- `Authorization: Bearer <token>`

Response 200 (application/json): Full Owner object (same shape as list item)

Errors:
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found if the owner does not exist

---

## Update Owner (Full)

PUT `/api/owners/{id}/`

Headers:
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

Request body (send all mutable fields):
```
{
  "full_name": "John Doe",
  "phone": "+15557654321",
  "email": "john.new@example.com",
  "address": "456 Market Rd, New City",
  "rate": 3.5
}
```

Response 200 (application/json): Full Owner object

Errors:
- 400 Bad Request on uniqueness violations or invalid `rate`
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found

---

## Update Owner (Partial)

PATCH `/api/owners/{id}/`

Headers:
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

Request body (example):
```
{
  "rate": 2.5
}
```

Response 200 (application/json): Full Owner object

Errors:
- 400 Bad Request on invalid field values
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found

---

## Delete Owner

DELETE `/api/owners/{id}/`

Headers:
- `Authorization: Bearer <token>`

Response 204 No Content

Errors:
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found

---

