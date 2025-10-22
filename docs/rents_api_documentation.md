# Rents API Documentation

This document describes the Rents API for the frontend: endpoints, required vs optional fields, validation rules, edge cases, and request/response examples. All endpoints are admin-only.

## Base URL
- /api/rents/

## Authentication and Permissions
- All endpoints require an authenticated admin user (IsAdminUser).
- Provide an Authorization header as configured for your project (e.g., Token or session cookie).
- Non-admins receive 403 Forbidden; unauthenticated users may receive 401 Unauthorized.

## Endpoints Summary

| Method | Path              | Description                 | Auth |
|-------:|-------------------|-----------------------------|------|
| GET    | /api/rents/       | List rents                  | Admin only |
| GET    | /api/rents/{id}/  | Retrieve a rent by ID       | Admin only |
| POST   | /api/rents/       | Create a rent               | Admin only |
| PUT    | /api/rents/{id}/  | Replace a rent              | Admin only |
| PATCH  | /api/rents/{id}/  | Update fields of a rent     | Admin only |
| DELETE | /api/rents/{id}/  | Delete a rent               | Admin only |

## Data Model Fields

Writeable fields (send in POST/PUT/PATCH):

| Field          | Type     | Required | Allowed Values / Format                                        | Default     | Notes |
|----------------|----------|----------|-----------------------------------------------------------------|-------------|-------|
| unit           | integer  | Yes      | Existing Unit ID                                                | —           | Foreign key to units.Unit |
| tenant         | integer  | Yes      | Existing Tenant ID                                              | —           | Foreign key to tenants.Tenant |
| rent_start     | date     | Yes      | YYYY-MM-DD                                                      | —           | Must be <= rent_end |
| rent_end       | date     | Yes      | YYYY-MM-DD                                                      | —           | Must be >= rent_start |
| total_amount   | decimal  | Yes      | String decimal, e.g., "1500.00"                                 | —           | max_digits=12, decimal_places=2 |
| payment_status | string   | Yes      | paid | pending | overdue                                        | —           | Choice field |
| payment_method | string   | Yes      | cash | bank_transfer | credit_card | online_payment                  | —           | Choice field |
| payment_date   | datetime | Yes      | ISO 8601 (e.g., 2025-10-06T09:00:00Z)                           | —           | Provide explicit timestamp |
| notes          | string   | No       | Any                                                            | null        | Optional text |
| attachment     | file     | No       | multipart/form-data file                                       | null        | Optional file upload |

Read-only computed fields (returned in responses):

| Field            | Type     | Description |
|------------------|----------|-------------|
| id               | integer  | Primary key |
| created_at       | datetime | Creation timestamp |
| status           | string   | Computed from payment_status and dates. One of: active, expired, pending, canceled |
| unit_name        | string   | Unit name |
| unit_type        | string   | Unit type label (display) |
| unit_type_value  | string   | Unit type value (raw choice) |
| tenant_name      | string   | Tenant full name |
| tenant_email     | string   | Tenant email |
| tenant_phone     | string   | Tenant phone |
| duration         | string   | Friendly span between rent_start and rent_end, e.g., "12 days", "1 month 6 days" |

## Validation Rules

- Required fields: unit, tenant, rent_start, rent_end, total_amount, payment_status, payment_method, payment_date.
- Date order: rent_end must be on or after rent_start.
- Choice validation:
  - payment_status must be one of: paid, pending, overdue.
  - payment_method must be one of: cash, bank_transfer, credit_card, online_payment.
- Foreign keys must exist:
  - unit must reference an existing Unit.
  - tenant must reference an existing Tenant.
- Status is auto-computed; do not send status in requests.
- Attachment uploads require multipart/form-data; otherwise use application/json.
- Permission: non-admin access is forbidden.

## Edge Cases and Behavior Notes

### A) Date and duration
- Rules
  - rent_end must be >= rent_start; otherwise 400 with a field error.
  - Duration shown is based on whole days between the two dates.
  - Months are displayed using a simple 30-day approximation for readability.
- Examples
  - 2025-01-01 → 2025-01-01 ⇒ 0 days (same day)
  - 2025-01-01 → 2025-01-31 ⇒ 30 days ⇒ "1 month"
  - 2025-01-01 → 2025-02-10 ⇒ 40 days ⇒ "1 month 10 days"

### B) Status decision rules (auto-computed)
| payment_status | Date relation (today vs rent_end) | Resulting status |
|----------------|-----------------------------------|------------------|
| paid           | today <= rent_end                 | active           |
| paid           | today > rent_end                  | expired          |
| pending        | any                               | pending          |
| overdue        | rent_end < today                  | expired          |
| overdue        | rent_end >= today                 | pending          |
| canceled       | (if set manually in DB)           | stays canceled   |

Notes
- Clients should not send status; it is computed on save.
- If a record has status=canceled (set manually), save() does not override it.

### C) Invalid input and error mapping
- Missing required fields ⇒ 400 with field errors.
- Invalid choice strings ⇒ 400 with field errors listing allowed values.
- Non-existent foreign keys (unit/tenant) ⇒ 400 with a clear PK error.
- Invalid date order (rent_end < rent_start) ⇒ 400 with a clear message.
- Unauthenticated ⇒ 401 with detail message.
- Authenticated but not admin ⇒ 403 with detail message.
- Non-existent rent ID on GET/PUT/PATCH/DELETE ⇒ 404 Not Found.

### D) Attachments and content types
- JSON requests: use Content-Type: application/json (no file upload).
- File uploads: use multipart/form-data; include attachment along with other fields.
- The attachment field value in responses is the file path/URL depending on your storage/MEDIA_URL configuration.

### E) Timestamps and timezones
- payment_date accepts ISO 8601; include timezone (e.g., trailing Z for UTC) to avoid ambiguity.
- If payment_date is omitted, it defaults to the server current time.

### F) Overlapping rents and availability (enforced)
- The API now prevents overlapping rents.
  - A unit cannot have two rents whose date ranges overlap.
  - A tenant cannot have overlapping rents across different units.
- The unit must be available when:
  - Creating a rent (current status must be Available).
  - The requested rent period includes today.
- Error examples (400 Bad Request):
```json
{ "unit": ["This unit already has a rent overlapping with the selected dates."] }
```
```json
{ "tenant": ["This tenant already has another rent overlapping with the selected dates."] }
```
```json
{ "unit": ["Unit is not currently available to create a rent."] }
```
```json
{ "unit": ["Unit is not available for the selected period including today."] }
```

## Requests and Responses

### 1) List Rents
- Method: GET
- URL: /api/rents/
- Query params:
  - unit (integer): Filter by Unit ID. Alias: unit_id.
  - tenant (integer): Filter by Tenant ID. Alias: tenant_id.
  - When both are provided, results match both (AND semantics).

Examples:
- /api/rents/?unit=7
- /api/rents/?tenant=3
- /api/rents/?unit_id=7&tenant_id=3

Success response (200 OK):
```json
[
  {
    "id": 42,
    "unit": 7,
    "tenant": 3,
    "rent_start": "2025-10-05",
    "rent_end": "2025-11-10",
    "total_amount": "1500.00",
    "payment_status": "pending",
    "payment_method": "cash",
    "payment_date": "2025-10-05T12:34:56Z",
    "status": "pending",
    "notes": "First-time renter",
    "attachment": null,
    "created_at": "2025-10-05T12:34:56Z",
    "unit_name": "Unit A-101",
    "unit_type": "Apartment",
    "unit_type_value": "apartment",
    "tenant_name": "John Doe",
    "tenant_email": "john@example.com",
    "tenant_phone": "+1234567890",
    "duration": "36 days"
  }
]
```

Possible errors:
- 401 Unauthorized / 403 Forbidden

### 2) Retrieve Rent
- Method: GET
- URL: /api/rents/{id}/

Success response (200 OK): same shape as list item above.

Possible errors:
- 401 Unauthorized / 403 Forbidden
- 404 Not Found (invalid id)

### 3) Create Rent
- Method: POST
- URL: /api/rents/
- Content-Type: application/json (or multipart/form-data when sending attachment)

Request body (JSON):
```json
{
  "unit": 7,
  "tenant": 3,
  "rent_start": "2025-10-05",
  "rent_end": "2025-11-10",
  "total_amount": "1500.00",
  "payment_status": "pending",
  "payment_method": "cash",
  "payment_date": "2025-10-05T12:34:56Z",
  "notes": "First-time renter"
}
```

Success response (201 Created):
```json
{
  "id": 43,
  "unit": 7,
  "tenant": 3,
  "rent_start": "2025-10-05",
  "rent_end": "2025-11-10",
  "total_amount": "1500.00",
  "payment_status": "pending",
  "payment_method": "cash",
  "payment_date": "2025-10-05T12:34:56Z",
  "status": "pending",
  "notes": "First-time renter",
  "attachment": null,
  "created_at": "2025-10-05T12:34:56Z",
  "unit_name": "Unit A-101",
  "unit_type": "Apartment",
  "unit_type_value": "apartment",
  "tenant_name": "John Doe",
  "tenant_email": "john@example.com",
  "tenant_phone": "+1234567890",
  "duration": "36 days"
}
```

Validation error response (400 Bad Request):
```json
{
  "payment_status": [
    "This field is required."
  ],
  "payment_method": [
    "This field is required."
  ],
  "payment_date": [
    "This field is required."
  ]
}
```
Other example errors (400):
```json
{
  "payment_status": [
    "\"done\" is not a valid choice."
  ]
}
```
```json
{
  "rent_end": [
    "Rent end date cannot be earlier than rent start date."
  ]
}
```
```json
{
  "unit": [
    "Invalid pk \"9999\" - object does not exist."
  ]
}
```

Auth/permission errors:
- 401 Unauthorized
```json
{ "detail": "Authentication credentials were not provided." }
```
- 403 Forbidden
```json
{ "detail": "You do not have permission to perform this action." }
```

### 4) Update Rent
- Method: PUT or PATCH
- URL: /api/rents/{id}/
- Content-Type: application/json (or multipart/form-data when updating attachment)

Partial update example (PATCH):
```json
{
  "payment_status": "paid",
  "payment_method": "bank_transfer",
  "payment_date": "2025-10-06T09:00:00Z",
  "notes": "Payment received via bank."
}
```

Success response (200 OK):
```json
{
  "id": 43,
  "unit": 7,
  "tenant": 3,
  "rent_start": "2025-10-05",
  "rent_end": "2025-11-10",
  "total_amount": "1500.00",
  "payment_status": "paid",
  "payment_method": "bank_transfer",
  "payment_date": "2025-10-06T09:00:00Z",
  "status": "active",
  "notes": "Payment received via bank.",
  "attachment": null,
  "created_at": "2025-10-05T12:34:56Z",
  "unit_name": "Unit A-101",
  "unit_type": "Apartment",
  "unit_type_value": "apartment",
  "tenant_name": "John Doe",
  "tenant_email": "john@example.com",
  "tenant_phone": "+1234567890",
  "duration": "36 days"
}
```

Possible errors:
- 400 Bad Request (invalid choices, invalid date order, invalid foreign keys, missing required fields)
- 401/403 Auth/permission errors
- 404 Not Found (invalid rent id)

### 5) Delete Rent
- Method: DELETE
- URL: /api/rents/{id}/

Success response:
- 204 No Content (empty body)

Possible errors:
- 401/403 Auth/permission errors
- 404 Not Found (invalid rent id)
