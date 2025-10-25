# Authentication (Login, Refresh & Logout)

This guide explains how to log in and log out using JWT, refresh access tokens, create a superuser, and test from frontend or tools. It’s self-contained and production-friendly.

## At a glance

| Topic | Details                                                                       |
|---|-------------------------------------------------------------------------------|
| Base auth endpoints | Not under /api; root paths: `/auth/login/`, `/auth/refresh/`, `/auth/logout/` |
| Auth scheme | Bearer JWT (`Authorization: Bearer <access_token>`)                           |
| Token lifetimes | Access: 1 hour, Refresh: 7 days                                               |
| User model | Custom user "email , password" ; only superusers can log in here              |

## Quick start

1) Create a superuser (see Create a superuser) or ensure one exists (`is_superuser=True` and `is_staff=True`).
2) POST `/auth/login/` with email and password to get access and refresh tokens.
3) Use the access token on protected endpoints: `Authorization: Bearer <access>`.
4) When access expires, POST `/auth/refresh/` with your refresh token to get a new access token.
5) To log out, POST `/auth/logout/` with the refresh token to blacklist it.

---

## Endpoint overview

| Operation | Method | URL | Auth required | Purpose |
|---|---|---|---|---|
| Login | POST | `/auth/login/` | No | Authenticate a superuser and obtain JWT access/refresh tokens |
| Refresh access | POST | `/auth/refresh/` | No (body contains refresh) | Obtain a new access token using a valid refresh token |
| Logout | POST | `/auth/logout/` | No (body contains refresh) | Blacklist the refresh token so it can’t be used anymore |

---

## 1) Login

| Key | Value |
|---|---|
| Method | POST |
| URL | `/auth/login/` |
| Purpose | Authenticate a superuser and obtain JWT tokens |
| Required headers | `Content-Type: application/json` |
| Body fields | `email` (string, required), `password` (string, required) |

Request body
```json
{
  "email": "admin@example.com",
  "password": "your-password"
}
```

Successful response (200)
```json
{
  "message": "Logged in successfully",
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

Notes
- Only superusers can log in here. The account must have `is_superuser=True`.
- The project uses a custom user model with email as the username field (no `username` field).

Error responses

| Status | When | Example payload |
|---|---|---|
| 400 | Validation error (e.g., missing fields) | — |
| 401/403 | Invalid credentials or not a superuser | `{ "detail": "Invalid credentials or not a superuser" }` |

---

## 2) Refresh access token

Use your refresh token to obtain a new access token when the old one expires.

| Key | Value |
|---|---|
| Method | POST |
| URL | `/auth/refresh/` |
| Purpose | Obtain a new access token using a valid refresh token |
| Required headers | `Content-Type: application/json` |
| Body fields | `refresh` (string, required) |

Request body
```json
{
  "refresh": "<refresh_token>"
}
```

Successful response (200)
```json
{
  "access": "<new_access_token>"
}
```

Notes
- Tokens are not rotated by default; you’ll only receive a new `access` token (the same `refresh` remains valid until it expires or is blacklisted).
- If you enable rotation in the future, the response may also include a new `refresh` token.

Error responses

| Status | When | Example payload |
|---|---|---|
| 401 | Invalid, expired, or blacklisted refresh token | `{ "detail": "Token is blacklisted" }` or `{ "detail": "Token is invalid or expired" }` |

---

## 3) Logout

| Key | Value |
|---|---|
| Method | POST |
| URL | `/auth/logout/` |
| Purpose | Blacklist the refresh token so it can’t be used anymore |
| Required headers | `Content-Type: application/json` |
| Body fields | `refresh` (string, required) |

Request body
```json
{
  "refresh": "<refresh_token>"
}
```

Successful response (200)
```json
{
  "message": "Logged out successfully"
}
```

Error responses

| Status | When | Example payload |
|---|---|---|
| 400 | Missing/invalid refresh token or already blacklisted | `{ "error": "Refresh token required" }`, `{ "error": "Token is blacklisted" }`, `{ "error": "Invalid token" }` |

Implementation notes
- Logout calls blacklist on the provided refresh token. If the token was already blacklisted, the API returns an error explaining it.

## 4) integration guide

Typical flow
- On login, store `access` (in memory) and `refresh` (in httpOnly cookie or secure storage as per your policy). Avoid localStorage for long-term secrets if possible.
- For each API call, send `Authorization: Bearer <access>`.
- If a request fails with 401 due to an expired access token, call `/auth/refresh/` with your `refresh` to obtain a new `access`, then retry the original request.
- On explicit logout, call `/auth/logout/` with the `refresh` in body and access in header, then clear stored tokens.
---

## 5) Create a superuser

Option A: Using the CLI (Windows cmd.exe)
```cmd
python manage.py createsuperuser
```
Follow the prompts to enter email and password.

Option B: Using Django Admin (web)
1) Start the server:
```cmd
python manage.py runserver
```
2) Visit http://127.0.0.1:8000/admin/
3) Log in with an existing superuser.
4) Add a new User (from `apps.core.User`) with:
   - Email set
   - `is_staff = True`
   - `is_superuser = True`
   - Set a password

---

#### **all rights back to bassanthossamxx**