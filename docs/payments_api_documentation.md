# Payments API (Occasional Payments) — Frontend Integration Guide

This document fully covers the payments endpoints for occasional/unit-related payments. It includes all routes, request/response bodies, auth, enums, pagination, and example payloads. No other docs are required to integrate.

Base URL prefix: /api
All endpoints below are relative to the base URL.

Security and access
- Authentication: JWT (Authorization: Bearer <accessToken>)
- Required role: Admin (IsAdminUser). The calling user must be authenticated and have is_staff=true.
- Content type: application/json

Entities and field reference
OccasionalPayment object (returned by the API):
- id: integer, primary key
- unit: integer, unit ID this payment belongs to (read-only in API; it’s taken from the URL path)
- category: string, enum (see OccasionalPaymentCategory)
- amount: string (decimal), e.g. "150.00". Returned as a string; you may send as a JSON string or number. No minimum/maximum is enforced by the backend.
- payment_method: string, enum (see PaymentMethod)
- payment_date: string (YYYY-MM-DD) or null. Optional; defaults to today if omitted.
- notes: string or null. Optional.
- created_at: string (ISO8601 datetime, UTC), read-only
- updated_at: string (ISO8601 datetime, UTC), read-only

Enums
PaymentMethod
- cash
- bank_transfer
- credit_card
- online_payment

OccasionalPaymentCategory
- wifi
- water
- electricity
- cleaning
- maintenance
- repair
- other

Pagination
List endpoints use DRF page-number pagination with page size 20.
Response wrapper for list endpoints:
- count: integer
- next: string URL or null
- previous: string URL or null
- results: array of OccasionalPayment objects

Headers
- Authorization: Bearer <JWT_ACCESS_TOKEN>
- Content-Type: application/json

Endpoints
1) List unit payments
- Method and path: GET /payments/{unit_id}/
- Description: Returns paginated occasional payments for a unit (ordered by id ASC)
- Query params:
  - page: integer, optional (1-based)
- Success 200 response body example:
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "unit": 10,
        "category": "water",
        "amount": "75.50",
        "payment_method": "cash",
        "payment_date": "2025-10-24",
        "notes": "October bill",
        "created_at": "2025-10-24T10:20:30.000000Z",
        "updated_at": "2025-10-24T10:20:30.000000Z"
      },
      {
        "id": 2,
        "unit": 10,
        "category": "maintenance",
        "amount": "120.00",
        "payment_method": "bank_transfer",
        "payment_date": "2025-10-20",
        "notes": null,
        "created_at": "2025-10-24T10:21:10.000000Z",
        "updated_at": "2025-10-24T10:21:10.000000Z"
      }
    ]
  }
- Errors:
  - 401 Unauthorized (missing/invalid token)
  - 403 Forbidden (authenticated but not admin)
  - 404 Not Found (if unit_id does not exist)

2) Create a payment for a unit
- Method and path: POST /payments/{unit_id}/
- Description: Creates an occasional payment attached to the given unit
- Request body fields:
  - category: string, required (enum)
  - amount: string or number, required (decimal as string recommended)
  - payment_method: string, required (enum)
  - payment_date: string (YYYY-MM-DD) or null, optional (defaults to today if omitted)
  - notes: string or null, optional
- Notes:
  - Do not include unit in the body. It is read-only and taken from the URL.
- Request body example:
  {
    "category": "electricity",
    "amount": "150.00",
    "payment_method": "credit_card",
    "payment_date": "2025-10-24",
    "notes": "Paid via portal"
  }
- Success 201 response body example:
  {
    "id": 3,
    "unit": 10,
    "category": "electricity",
    "amount": "150.00",
    "payment_method": "credit_card",
    "payment_date": "2025-10-24",
    "notes": "Paid via portal",
    "created_at": "2025-10-24T10:25:00.000000Z",
    "updated_at": "2025-10-24T10:25:00.000000Z"
  }
- Errors:
  - 400 Bad Request (validation errors, e.g., invalid enum value)
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found (unit_id not found)

3) Retrieve a specific payment
- Method and path: GET /payments/{unit_id}/{id}/
- Description: Returns a single payment record for the given unit
- Success 200 response body example:
  {
    "id": 3,
    "unit": 10,
    "category": "electricity",
    "amount": "150.00",
    "payment_method": "credit_card",
    "payment_date": "2025-10-24",
    "notes": "Paid via portal",
    "created_at": "2025-10-24T10:25:00.000000Z",
    "updated_at": "2025-10-24T10:26:40.000000Z"
  }
- Errors:
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found (payment not found for this unit or id)

4) Update a payment (full replace)
- Method and path: PUT /payments/{unit_id}/{id}/
- Description: Replaces mutable fields of the payment
- Request body fields (all required for PUT):
  - category: string (enum)
  - amount: string or number
  - payment_method: string (enum)
  - payment_date: string (YYYY-MM-DD) or null
  - notes: string or null
- Body example:
  {
    "category": "maintenance",
    "amount": "125.00",
    "payment_method": "bank_transfer",
    "payment_date": "2025-10-23",
    "notes": "Adjusted"
  }
- Success 200 response body: same shape as "Retrieve" above.
- Errors: 400, 401, 403, 404

5) Partial update a payment
- Method and path: PATCH /payments/{unit_id}/{id}/
- Description: Updates only the provided fields
- Request body fields (any subset of below):
  - category: string (enum)
  - amount: string or number
  - payment_method: string (enum)
  - payment_date: string (YYYY-MM-DD) or null
  - notes: string or null
- Body example:
  {
    "notes": "Paid at front desk"
  }
- Success 200 response body: same shape as "Retrieve" above.
- Errors: 400, 401, 403, 404

6) Delete a payment
- Method and path: DELETE /payments/{unit_id}/{id}/
- Description: Deletes the payment
- Success 204 response body: empty
- Errors: 401, 403, 404

Validation rules and behavior
- category: must be one of the listed enum values; otherwise a 400 error is returned.
- payment_method: must be one of the listed enum values; otherwise a 400 error is returned.
- amount: decimal. The backend accepts numeric or string JSON. It returns a string (e.g., "150.00"). No minimum/maximum is enforced server-side.
- payment_date: ISO date (YYYY-MM-DD). Optional; defaults to current date when omitted. Can be null.
- unit: read-only via API; determined from the path parameter {unit_id}.

Examples (Windows cmd.exe friendly curl)
1) List payments for unit 10
curl -X GET "http://localhost:8000/api/payments/10/?page=1" ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

2) Create payment for unit 10
curl -X POST "http://localhost:8000/api/payments/10/" ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"category\":\"electricity\",\"amount\":\"150.00\",\"payment_method\":\"credit_card\",\"payment_date\":\"2025-10-24\",\"notes\":\"Paid via portal\"}"

3) Get payment id 3 for unit 10
curl -X GET "http://localhost:8000/api/payments/10/3/" ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

4) Update payment id 3 (PUT)
curl -X PUT "http://localhost:8000/api/payments/10/3/" ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"category\":\"maintenance\",\"amount\":\"125.00\",\"payment_method\":\"bank_transfer\",\"payment_date\":\"2025-10-23\",\"notes\":\"Adjusted\"}"

5) Partial update notes (PATCH)
curl -X PATCH "http://localhost:8000/api/payments/10/3/" ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"notes\":\"Paid at front desk\"}"

6) Delete payment id 3
curl -X DELETE "http://localhost:8000/api/payments/10/3/" ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

Error responses
- 400 Bad Request:
  {
    "category": ["\"invalid_value\" is not a valid choice."]
  }
- 401 Unauthorized:
  { "detail": "Authentication credentials were not provided." }
- 403 Forbidden:
  { "detail": "You do not have permission to perform this action." }
- 404 Not Found:
  { "detail": "Not found." }

Additional notes
- Ordering is by id ascending by default; no search or explicit ordering parameters are configured on these endpoints.
- Timestamps are in UTC (ISO8601). Parse them accordingly on the frontend.
- The /api/schema/ endpoint is available if you want an OpenAPI schema, but this guide is self-sufficient for payments integration.

