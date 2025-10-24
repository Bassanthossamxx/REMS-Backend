# Real Estate Management System Server

A Django REST Framework-based backend API for managing real estate properties, owners, tenants, rentals, and inventory. This CRM system provides comprehensive property management capabilities with RESTful endpoints.
**postman Doc** : https://documenter.getpostman.com/view/37742819/2sB3Wjz3tt
**Frontend:** [https://crmbild.netlify.app/](https://crmbild.netlify.app/)

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Database Setup (Neon PostgreSQL)](#database-setup-neon-postgresql)
- [Running the Project](#running-the-project)
## Features

- **Property Management**: Manage units with details, images, and status tracking
- **Owner Management**: Track property owners and their associated units
- **Tenant Management**: Maintain tenant information with ratings and notes
- **Rent Tracking**: Monitor rental payments, status, and payment methods
- **Inventory System**: Track property-related inventory and equipment
- **Notifications**: Automated notification system for important events
- **API Documentation**: Interactive Swagger/ReDoc documentation
- **CORS Support**: Configured for frontend integration

##  Tech Stack

- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL (Neon DB recommended)
- **API Documentation**: drf-spectacular (OpenAPI 3.0)

## Project Structure

```
REMS-Backend/
├── config/                     # Project configuration
│   ├── __init__.py
│   ├── settings.py            # Main settings file
│   ├── urls.py                # Root URL configuration'
│   ├── choices.py              # all app choices
│   ├── validations.py          # validations syste
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
│
├── apps/                       # Django applications
│   ├── core/                  # Core functionality
│   ├── owners/                # Owner management
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── tenants/               # Tenant management
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── units/                 # Property units management
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── rents/                 # Rental & payment tracking
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── inventory/             # Inventory management
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── notifications/         # Notification system
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
│   └── Payments/         # any payments system
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
│
├── docs/                       # Documentation for API and project details
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.11 or higher** ([Download Python](https://www.python.org/downloads/))
- **PostgreSQL** or **Neon DB account** ([Neon DB](https://neon.tech/))
- **pip** (Python package manager)
- **virtualenv** (recommended for isolated environments)
- **Git** (for version control)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd REMS-Backend
```

### 2. Create a Virtual Environment

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory of the project with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-generate-a-strong-random-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database Configuration (Neon PostgreSQL)
DATABASE_URL=postgresql://username:password@hostname/database_name?sslmode=require

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://crmbild.netlify.app
```

### Generating a SECRET_KEY

You can generate a secure secret key using Python:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

##  Database Setup 

### option 1 : Create a Neon Database

1. Go to [Neon.tech](https://neon.tech/) and sign up/login
2. Create a new project
3. Create a new database
4. Copy the connection string

### Step 2: Configure DATABASE_URL

Your Neon connection string should look like this:

```
postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/database_name?sslmode=require
```

Paste this entire URL as the value for `DATABASE_URL` in your `.env` file.

### Alternative: Local PostgreSQL

If you prefer using a local PostgreSQL database:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/crm_real_state
```

## Running the Project

### 1. Apply Database Migrations

Run the following commands to create database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create a Superuser

Create an admin account to access the Django admin panel:

```bash
python manage.py createsuperuser
```

### 3. Run the Development Server

```bash
python manage.py runserver
```

The server will start

### 5. Access the Application

- **API Root**: `http://127.0.0.1:8000/api/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`
- **Swagger Documentation**: `http://127.0.0.1:8000/`

## API Documentation

The project uses **drf-spectacular** for automatic API documentation:

- **Swagger UI**: Interactive API documentation with request/response examples
  - URL: `baseurl`
. also there is an docs folder with docs for apis and overview and erd under development
---
### all rights back to @bassanthossamxx 

