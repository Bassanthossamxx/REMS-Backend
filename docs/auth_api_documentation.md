# Authentication (Login & Logout)

This guide explains how to log in and log out using JWT, create a superuser, and test from frontend or tools. It’s self-contained and production-friendly.

## At a glance

| Topic | Details |
|---|---|
| Base auth endpoints | Not under /api; root paths: `/auth/login/`, `/auth/logout/` |
| Auth scheme | Bearer JWT (`Authorization: Bearer <access_token>`) |
| Token lifetimes (default) | Access: 6 hours, Refresh: 7 days |
| User model | Custom user (email is the username); only superusers can log in here |

## Quick start

1) Create a superuser (see Create a superuser) or ensure one exists (`is_superuser=True` and `is_staff=True`).
2) POST `/auth/login/` with email and password to get access and refresh tokens.
3) Use the access token on protected endpoints: `Authorization: Bearer <access>`.
4) To log out, POST `/auth/logout/` with the refresh token to blacklist it.

---

## Endpoint overview

| Operation | Method | URL | Auth required | Purpose |
|---|---|---|---|---|
| Login | POST | `/auth/login/` | No | Authenticate a superuser and obtain JWT access/refresh tokens |
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

## 2) Logout

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
| 400 | Missing/invalid refresh token | `{ "error": "Refresh token required" }` or `{ "error": "Invalid token" }` |

### Important: Enable token blacklist

To actually blacklist tokens on logout, ensure the blacklist app is enabled.

1) In `config/settings.py`, add to `INSTALLED_APPS`:
```python
'rest_framework_simplejwt.token_blacklist',
```
2) Run migrations:
```cmd
python manage.py migrate
```

If the blacklist app is not enabled, logout may error or won’t revoke the token.

---

## 3) Create a superuser

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

Option C: From Django shell
```cmd
python manage.py shell
```
```python
from apps.core.models import User
User.objects.create_superuser(email="admin@example.com", password="StrongPass123!")
exit()
```

Notes about the User model

| Setting | Value |
|---|---|
| `AUTH_USER_MODEL` | `apps.core.User` |
| Username | Disabled; login is with email |
| Email | Unique and required |

---