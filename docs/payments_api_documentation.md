# Payments API  — Frontend Integration Guide

This is a complete, self-contained guide for integrating the payments (occasional payments + analytics) module. It documents all routes, headers, request/response bodies, enums, pagination, field meanings, and error shapes.

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

## Key terms (analytics)
- this_month: From the 1st day of the current calendar month until now (server timezone).
- all_time: Cumulative from the beginning of data until now.
- total: Total rent before any deductions.
- total_occasional: Sum of occasional (deductions/expenses) entries.
- total_after_occasional: Net after deductions = total − total_occasional.
- owner_total: The owner's share after deductions, using each unit's owner_percentage (as a fraction, e.g., 0.60 for 60%).
- company_total: What remains for the company after paying the owner = total_after_occasional − owner_total.

Decimals are returned as strings (e.g., "150.00").

---

## Resource schema: OccasionalPayment

| Field          | Type    | Required | Read-only | Notes |
|----------------|---------|----------|-----------|-------|
| id             | integer | No       | Yes       | Primary key |
| unit           | integer | No       | Yes       | Taken from URL path `{unit_id}` when creating/listing. Included in responses. |
| category       | string  | Yes      | No        | One of OccasionalPaymentCategory |
| amount         | decimal | Yes      | No        | Send as string (recommended) or number; returned as string (e.g., "150.00"). |
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
  "results": [],
  "totals": {}
}
```

---

## Endpoints overview

| Method | Path                                  | Description                                       | Auth | Pagination |
|--------|---------------------------------------|---------------------------------------------------|------|------------|
| GET    | /payments/{unit_id}/                  | List occasional payments for a unit               | Yes  | Yes        |
| POST   | /payments/{unit_id}/                  | Create an occasional payment for a unit           | Yes  | No         |
| GET    | /payments/{unit_id}/{id}/             | Retrieve a specific occasional payment            | Yes  | No         |
| PUT    | /payments/{unit_id}/{id}/             | Full update an occasional payment                 | Yes  | No         |
| PATCH  | /payments/{unit_id}/{id}/             | Partial update an occasional payment              | Yes  | No         |
| DELETE | /payments/{unit_id}/{id}/             | Delete an occasional payment                      | Yes  | No         |
| GET    | /payments/all/owner/{owner_id}/       | Owner analytics summary (this month + all time)   | Yes  | No         |
| POST   | /payments/owner/{owner_id}/pay/       | Record a payout to owner                          | Yes  | No         |
| GET    | /payments/all/unit/{unit_id}/         | Unit analytics summary (this month + all time)    | Yes  | No         |
| GET    | /payments/all/payments/me/            | Company summary (this month + all time)           | Yes  | No         |
| GET    | /payments/all/payments/me/{unit_id}/  | Company summary for a specific unit               | Yes  | No         |

---

## Endpoint details

### 1) List unit payments
- Method and path: `GET /payments/{unit_id}/`
- Returns paginated occasional payments for a unit (ordered by `id` ASC).
- Each item includes summary fields for the unit (calculated in serializer):
  - `total_occasional_payment`: sum of all payments for this unit (string)
  - `total_occasional_payment_last_month`: sum within the previous calendar month (string)

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
      "updated_at": "2025-10-24T10:20:30.000000Z",
      "total_occasional_payment": "195.50",
      "total_occasional_payment_last_month": "0.00"
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
      "updated_at": "2025-10-24T10:21:10.000000Z",
      "total_occasional_payment": "195.50",
      "total_occasional_payment_last_month": "0.00"
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

Errors: 400, 401, 403, 404

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

Errors: 400, 401, 403, 404

---

## Analytics & payouts endpoints

### 7) Owner analytics summary
- Method and path: `GET /payments/all/owner/{owner_id}/`
- Returns totals for a specific owner, including per-unit breakdown.

Path params

| Name     | Type    | Required | Notes                  |
|----------|---------|----------|------------------------|
| owner_id | integer | Yes      | The target owner ID.   |

Response body (fields)

| Field                         | Type    | Notes |
|-------------------------------|---------|-------|
| owner_id                      | integer | Owner ID |
| owner_name                    | string  | Owner full name |
| total_this_month              | decimal | Rent total from 1st of this month until now (no deductions) |
| total                         | decimal | Rent total all time (no deductions) |
| total_occasional_this_month   | decimal | Occasional deductions this month |
| total_occasional              | decimal | Occasional deductions all time |
| total_after_occasional_this_month | decimal | Net this month = total − total_occasional |
| total_after_occasional        | decimal | Net all time = total − total_occasional |
| owner_total_this_month        | decimal | Owner share this month after deductions |
| owner_total                   | decimal | Owner share all time after deductions |
| paid_to_owner_total           | decimal | Sum of all payouts already made to this owner |
| still_need_to_pay             | decimal | owner_total − paid_to_owner_total |
| units                         | array   | Per-unit breakdown (see below) |

Per-unit breakdown item

| Field                            | Type    | Notes |
|----------------------------------|---------|-------|
| unit_id                          | integer | Unit ID |
| unit_name                        | string  | Unit name |
| owner_percentage                 | decimal | Fraction, e.g., 0.60 for 60% |
| total                            | decimal | Rent total all time (no deductions) |
| total_this_month                 | decimal | Rent this month (no deductions) |
| total_occasional                 | decimal | Deductions total all time |
| total_occasional_this_month      | decimal | Deductions this month |
| total_after_occasional           | decimal | Net all time = total − total_occasional |
| total_after_occasional_this_month| decimal | Net this month |
| owner_total                      | decimal | Owner share all time after deductions |
| owner_total_this_month           | decimal | Owner share this month |

Response 200 example

```json
{
  "owner_id": 3,
  "owner_name": "Ahmed Ali",
  "total_this_month": "25000.00",
  "total": "180000.00",
  "total_occasional_this_month": "2000.00",
  "total_occasional": "4000.00",
  "total_after_occasional_this_month": "23000.00",
  "total_after_occasional": "176000.00",
  "owner_total_this_month": "13800.00",
  "owner_total": "105600.00",
  "paid_to_owner_total": "90000.00",
  "still_need_to_pay": "15600.00",
  "units": [
    {
      "unit_id": 12,
      "unit_name": "A-101",
      "owner_percentage": "0.6000",
      "total": "100000.00",
      "total_this_month": "10000.00",
      "total_occasional": "2000.00",
      "total_occasional_this_month": "1000.00",
      "total_after_occasional": "98000.00",
      "total_after_occasional_this_month": "9000.00",
      "owner_total": "58800.00",
      "owner_total_this_month": "5400.00"
    }
  ]
}
```

Errors
- 401 Unauthorized, 403 Forbidden, 404 Not Found (owner not found)

---

### 8) Record a payout to owner
- Method and path: `POST /payments/owner/{owner_id}/pay/`
- Records a manual payout to the owner.

Path params

| Name     | Type    | Required | Notes                |
|----------|---------|----------|----------------------|
| owner_id | integer | Yes      | Target owner ID.     |

Request body

| Field       | Type    | Required | Notes |
|-------------|---------|----------|-------|
| amount_paid | decimal | Yes      | Amount being paid to the owner |
| notes       | string  | No       | Optional notes |

Request example

```json
{
  "amount_paid": "5000.00",
  "notes": "Monthly payout for October"
}
```

Response 201 example

```json
{
  "id": 45,
  "owner": 3,
  "date": "2025-10-25T12:30:15.000000Z",
  "notes": "Monthly payout for October"
}
```

Notes
- `amount_paid` is write-only in the request; the stored amount equals `amount_paid` but is not echoed back.
- Future owner summary calls will reflect the updated `paid_to_owner_total` and `still_need_to_pay`.

Errors
- 400 Bad Request (invalid or missing `amount_paid`)
- 401 Unauthorized, 403 Forbidden, 404 Not Found (owner not found)

---

### 9) Unit analytics summary
- Method and path: `GET /payments/all/unit/{unit_id}/`
- Returns rent and deduction breakdown for a specific unit.

Path params

| Name    | Type    | Required | Notes              |
|---------|---------|----------|--------------------|
| unit_id | integer | Yes      | The target unit ID |

Response body (fields)

| Field                         | Type    | Notes |
|-------------------------------|---------|-------|
| unit_id                       | integer | Unit ID |
| unit_name                     | string  | Unit name |
| owner_id                      | integer | Owner ID |
| owner_name                    | string  | Owner name |
| owner_percentage              | decimal | Fraction, e.g., 0.60 for 60% |
| total_this_month              | decimal | Rent this month (no deductions) |
| total                         | decimal | Rent all time (no deductions) |
| total_occasional_this_month   | decimal | Deductions this month |
| total_occasional              | decimal | Deductions all time |
| total_after_occasional_this_month | decimal | Net this month |
| total_after_occasional        | decimal | Net all time |
| company_total_this_month      | decimal | Company share this month = net − owner |
| company_total                 | decimal | Company share all time = net − owner |

Response 200 example

```json
{
  "unit_id": 12,
  "unit_name": "A-101",
  "owner_id": 3,
  "owner_name": "Ahmed Ali",
  "owner_percentage": "0.6000",
  "total_this_month": "10000.00",
  "total": "100000.00",
  "total_occasional_this_month": "1000.00",
  "total_occasional": "2000.00",
  "total_after_occasional_this_month": "9000.00",
  "total_after_occasional": "98000.00",
  "owner_total_this_month": "5400.00",
  "company_total_this_month": "3600.00",
  "company_total": "39200.00"
}
```

Errors
- 401 Unauthorized, 403 Forbidden, 404 Not Found (unit not found)

---

### 10) Company summary ("me")
- Method and path: `GET /payments/all/payments/me/`
- Returns company totals across all units (after occasional and after paying owners).

Response 200 example

```json
{
  "total_this_month": "25000.00",
  "total": "180000.00",
  "total_occasional_this_month": "2000.00",
  "total_occasional": "4000.00",
  "total_after_occasional_this_month": "23000.00",
  "total_after_occasional": "176000.00",
  "owner_total_this_month": "13800.00",
  "owner_total": "105600.00",
  "company_total_this_month": "9200.00",
  "company_total": "70400.00"
}
```

Errors: 401 Unauthorized, 403 Forbidden

---

### 11) Company summary for a specific unit ("me")
- Method and path: `GET /payments/all/payments/me/{unit_id}/`
- Same as company summary but scoped to a single unit.

Path params

| Name    | Type    | Required | Notes              |
|---------|---------|----------|--------------------|
| unit_id | integer | Yes      | The target unit ID |

Response 200 example

```json
{
  "unit_id": 12,
  "total_this_month": "10000.00",
  "total": "100000.00",
  "total_occasional_this_month": "1000.00",
  "total_occasional": "2000.00",
  "total_after_occasional_this_month": "9000.00",
  "total_after_occasional": "98000.00",
  "owner_total_this_month": "5400.00",
  "owner_total": "58800.00",
  "company_total_this_month": "3600.00",
  "company_total": "39200.00"
}
```

Errors
- 401 Unauthorized, 403 Forbidden, 404 Not Found (unit not found)

---

## Error responses

| Status | Example body |
|--------|--------------|
| 400    | `{ "amount_paid": ["This field is required."] }` |
| 401    | `{ "detail": "Authentication credentials were not provided." }` |
| 403    | `{ "detail": "You do not have permission to perform this action." }` |
| 404    | `{ "detail": "Not found." }` |

---

## Notes & tips

- "this_month" always means from the 1st of the current calendar month until now.
- Decimals are rendered as strings with two decimals.
- `owner_percentage` in analytics is a fraction (0.0..1.0) with four decimals.
- After calling an owner payout (pay endpoint), the next owner summary reflects the new totals.
- OpenAPI schema is available at `/api/schema/`.
- Occasional payments CRUD is ordered by `id` ascending; no extra filters are exposed.

---
#### **all rights back to bassanthossamxx**
