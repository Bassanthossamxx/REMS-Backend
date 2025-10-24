# Payments API  — Frontend Integration Guide

This is a complete, self-contained guide for integrating the payments (occasional payments) module. It documents all routes, headers, request/response bodies, enums, pagination, and error shapes.

- Base URL prefix: `/api/`
- All paths below are relative to the base URL.
- Auth required: Yes (JWT). Caller must be admin (`is_staff=true`).
- Content type: `application/json`

---

## Authentication

- Header: `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- Non-admin or unauthenticated calls will be rejected.

---

## Enums

### PaymentMethod

| Value           | Label          |
|-----------------|----------------|
| cash            | Cash           |
| bank_transfer   | Bank Transfer  |
| credit_card     | Credit Card    |
| online_payment  | Online Payment |

### OccasionalPaymentCategory

| Value        | Label       |
|--------------|-------------|
| wifi         | WiFi        |
| water        | Water       |
| electricity  | Electricity |
| cleaning     | Cleaning    |
| maintenance  | Maintenance |
| repair       | Repair      |
| other        | Other       |

---

## Resource schema: OccasionalPayment

| Field          | Type    | Required | Read-only | Notes |
|----------------|---------|----------|-----------|-------|
| id             | integer | No       | Yes       | Primary key |
| unit           | integer | No       | Yes       | Taken from URL path `{unit_id}` when creating/listing. Included in responses. |
| category       | string  | Yes      | No        | One of OccasionalPaymentCategory |
| amount         | decimal | Yes      | No        | Send as string (recommended) or number; returned as string (e.g., `"150.00"`). |
| payment_method | string  | Yes      | No        | One of PaymentMethod |
| payment_date   | date    | No       | No        | `YYYY-MM-DD`; defaults to today if omitted; can be null. |
| notes          | string  | No       | No        | Optional; can be null. |
| created_at     | string  | No       | Yes       | ISO8601 datetime (UTC) |
| updated_at     | string  | No       | Yes       | ISO8601 datetime (UTC) |

---

## Pagination

List endpoints use page-number pagination.

| Param | Type    | Default | Notes |
|-------|---------|---------|-------|
| page  | integer | 1       | 1-based page index |

List response wrapper shape:

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [ /* OccasionalPayment[] */ ]
}
```

---

## Endpoints overview

| Method | Path                           | Description                                   | Auth | Pagination |
|--------|--------------------------------|-----------------------------------------------|------|------------|
| GET    | /payments/{unit_id}/           | List payments for a unit                      | Yes  | Yes        |
| POST   | /payments/{unit_id}/           | Create a payment for a unit                   | Yes  | No         |
| GET    | /payments/{unit_id}/{id}/      | Retrieve a specific payment                   | Yes  | No         |
| PUT    | /payments/{unit_id}/{id}/      | Full update a payment (replace)               | Yes  | No         |
| PATCH  | /payments/{unit_id}/{id}/      | Partial update of a payment                   | Yes  | No         |
| DELETE | /payments/{unit_id}/{id}/      | Delete a payment                              | Yes  | No         |

---

## Endpoint details

### 1) List unit payments
- Method and path: `GET /payments/{unit_id}/`
- Returns paginated occasional payments for a unit (ordered by `id` ASC).

Path params

| Name     | Type    | Required | Notes                |
|----------|---------|----------|----------------------|
| unit_id  | integer | Yes      | The target unit ID.  |

Query params

| Name | Type    | Required | Notes |
|------|---------|----------|-------|
| page | integer | No       | 1-based page index. |

Response 200 example

```json
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
```

Errors

- 401 Unauthorized (missing/invalid token)
- 403 Forbidden (authenticated but not admin)
- 404 Not Found (if `unit_id` does not exist)

---

### 2) Create a payment for a unit
- Method and path: `POST /payments/{unit_id}/`
- Creates an occasional payment attached to the given unit.

Path params

| Name     | Type    | Required | Notes               |
|----------|---------|----------|---------------------|
| unit_id  | integer | Yes      | Target unit ID.     |

Request body

| Field          | Type    | Required | Notes |
|----------------|---------|----------|-------|
| category       | string  | Yes      | One of OccasionalPaymentCategory |
| amount         | decimal | Yes      | Send as string (recommended) or number |
| payment_method | string  | Yes      | One of PaymentMethod |
| payment_date   | date    | No       | `YYYY-MM-DD`; defaults to today; can be null |
| notes          | string  | No       | Optional; can be null |

Note: Do not include `unit` in the body; it is taken from the path and is read-only.

Request example

```json
{
  "category": "electricity",
  "amount": "150.00",
  "payment_method": "credit_card",
  "payment_date": "2025-10-24",
  "notes": "Paid via portal"
}
```

Response 201 example

```json
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
```

Errors

- 400 Bad Request (validation errors, e.g., invalid enum value)
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found (unit not found)

---

### 3) Retrieve a specific payment
- Method and path: `GET /payments/{unit_id}/{id}/`
- Returns a single payment record for the given unit.

Path params

| Name     | Type    | Required | Notes               |
|----------|---------|----------|---------------------|
| unit_id  | integer | Yes      | Target unit ID.     |
| id       | integer | Yes      | Payment ID.         |

Response 200 example

```json
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
```

Errors: 401, 403, 404

---

### 4) Update a payment (full replace)
- Method and path: `PUT /payments/{unit_id}/{id}/`
- Replaces mutable fields of the payment.

Path params

| Name     | Type    | Required | Notes               |
|----------|---------|----------|---------------------|
| unit_id  | integer | Yes      | Target unit ID.     |
| id       | integer | Yes      | Payment ID.         |

Request body (all fields required for PUT)

| Field          | Type    | Required | Notes |
|----------------|---------|----------|-------|
| category       | string  | Yes      | One of OccasionalPaymentCategory |
| amount         | decimal | Yes      | Send as string or number |
| payment_method | string  | Yes      | One of PaymentMethod |
| payment_date   | date    | Yes      | `YYYY-MM-DD` or null |
| notes          | string  | Yes      | Can be null |

Request example

```json
{
  "category": "maintenance",
  "amount": "125.00",
  "payment_method": "bank_transfer",
  "payment_date": "2025-10-23",
  "notes": "Adjusted"
}
```

Response 200: Same shape as "Retrieve" above.

Errors: 400, 401, 403, 404

---

### 5) Partial update a payment
- Method and path: `PATCH /payments/{unit_id}/{id}/`
- Updates only the provided fields.

Path params

| Name     | Type    | Required | Notes               |
|----------|---------|----------|---------------------|
| unit_id  | integer | Yes      | Target unit ID.     |
| id       | integer | Yes      | Payment ID.         |

Request body (any subset)

| Field          | Type    | Notes |
|----------------|---------|-------|
| category       | string  | One of OccasionalPaymentCategory |
| amount         | decimal | Send as string or number |
| payment_method | string  | One of PaymentMethod |
| payment_date   | date    | `YYYY-MM-DD` or null |
| notes          | string  | Can be null |

Request example

```json
{
  "notes": "Paid at front desk"
}
```

Response 200: Same shape as "Retrieve".

Errors: 400, 401, 403, 404

---

### 6) Delete a payment
- Method and path: `DELETE /payments/{unit_id}/{id}/`
- Deletes the payment.

Path params

| Name     | Type    | Required | Notes               |
|----------|---------|----------|---------------------|
| unit_id  | integer | Yes      | Target unit ID.     |
| id       | integer | Yes      | Payment ID.         |

Success: 204 No Content (empty body)

Errors: 401, 403, 404

---

## Error responses

| Status | Example body |
|--------|--------------|
| 400    | `{ "category": ["\"invalid_value\" is not a valid choice."] }` |
| 401    | `{ "detail": "Authentication credentials were not provided." }` |
| 403    | `{ "detail": "You do not have permission to perform this action." }` |
| 404    | `{ "detail": "Not found." }` |

---
## Notes & tips

- Ordering is by `id` ascending; no search or ordering params are exposed on these endpoints.
- Timestamps are ISO8601 UTC. Parse on the frontend as needed.
- `unit` is read-only via the API surface and inferred from the path.
- OpenAPI schema is also available at `/api/schema/`, but this guide is sufficient for payments integration.
