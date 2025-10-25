# Tenants API Documentation

This document provides an overview of the endpoints available in the Tenants app, including their functionality, request parameters, and expected responses.

## Base URL
```
baseurl/api/
```

## Endpoints

### 1. List Tenants
**GET** `/tenants/`

Retrieve a list of tenants with optional filtering and search.

#### Query Parameters:
- `search` (string, optional): Case-insensitive partial search across tenant full name and unit name (e.g. `?search=john` or `?search=Unit%20A`). The search looks into `full_name` and the related unit's `name`.
- `status` (string, optional): Filter by rent status. Possible values:
  - `active`
  - `completed`
  - `overdue`
  - `pending`
  - `inactive`
- Pagination query params (standard DRF): `page`, `page_size` (if pagination is enabled).

Notes about `search` behavior:
- The endpoint uses Django REST Framework's SearchFilter. Multiple words in the `search` parameter are treated as separate terms and matched across the configured fields (`full_name`, `rents__unit__name`) using case-insensitive partial matches.
- Example: `GET /tenants/?search=john+doe` will return tenants where either `full_name` or the unit name contains `john` AND/OR `doe` depending on configured search behavior (DRF default combines terms with AND).

#### Examples:
- Search by tenant name:
  - `GET /tenants/?search=John`
- Search by unit name:
  - `GET /tenants/?search=Unit%20A`
- Combine with status filter:
  - `GET /tenants/?search=John&status=active`

#### Response (list):
```json
[
    {
        "id": 1,
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "rate": 1000.0,
        "address": "123 Main St",
        "rent": {
            "unit_name": "Unit A",
            "rent_start": "2025-01-01",
            "rent_end": "2025-12-31",
            "total_amount": 12000.0,
            "status": "active",
            "payment_status": "paid"
        }
    }
]
```

### 2. Retrieve Tenant by ID
**GET** `/tenants/{id}/`

Retrieve details of a specific tenant by their ID.

#### Response:
```json
{
    "id": 1,
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "1234567890",
    "rate": 1000.0,
    "address": "123 Main St",
    "rent": {
        "unit_name": "Unit A",
        "rent_start": "2025-01-01",
        "rent_end": "2025-12-31",
        "total_amount": 12000.0,
        "status": "active",
        "payment_status": "paid"
    }
}
```

### 3. Create Tenant
**POST** `/tenants/`

Create a new tenant.

#### Request Body:
```json
{
    "full_name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "0987654321",
    "rate": 4.5,
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
    "rate": 4.5,
    "address": "456 Elm St",
    "rent": null
}
```

### 4. Update Tenant
**PUT/PATCH** `/tenants/{id}/`

Update an existing tenant's details.

#### Request Body:
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
    "rent": null
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

## Notes
- All endpoints require admin permissions.
- Ensure proper authentication headers are included in the requests.
- Use the `status` query parameters in the list endpoint to filter results effectively.
- The `search` parameter searches both tenant full name and related unit name (configured in the view as `search_fields = ["full_name", "rents__unit__name"]`).
---
#### **all rights back to bassanthossamxx**