# Zippee Assignment - Task Manager API

A RESTful Task Manager API built with Django, Django REST Framework, JWT authentication, and PostgreSQL.

## Overview

This project provides:
- User registration and login using JWT
- Task CRUD operations
- Owner-based permissions with admin override
- Filtering, ordering, and pagination
- Swagger and ReDoc API documentation
- Automated tests with pytest

## Tech Stack

- Python 3.11+
- Django 4.2
- Django REST Framework
- SimpleJWT
- PostgreSQL 15 (Docker)
- drf-spectacular (Swagger/ReDoc)
- pytest, pytest-django

## Features

### Authentication
- POST /auth/register
- POST /auth/login
- POST /auth/refresh

### Tasks
- GET /tasks/
- GET /tasks/{id}/
- POST /tasks/
- PUT /tasks/{id}/
- DELETE /tasks/{id}/

### Access Control
- Auth required for all task endpoints
- Regular users can manage only their own tasks
- Admin users can manage all tasks

### Extra
- Pagination enabled
- Filter tasks by completed status
- Ordering by created_at and completed

## Project Structure

```text
apps/
  accounts/
  tasks/
config/
  settings/
manage.py
requirements.txt
docker-compose.yml
README.md
```

## Quick Start (Recommended: PostgreSQL with Docker)

### 1) Clone and open the project

```bash
git clone <your-repo-url>
cd zippee-assignment
```

### 2) Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment

Copy .env.example to .env and update values if needed:

```bash
cp .env.example .env
```

For local Django process connecting to Docker PostgreSQL, use:

```env
SECRET_KEY=dev-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=django.db.backends.postgresql
DB_NAME=taskmanager
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 5) Start PostgreSQL

```bash
docker compose up -d
```

### 6) Run migrations

```bash
python manage.py migrate
```

### 7) Create superuser (optional)

```bash
python manage.py createsuperuser --email admin@example.com
```

### 8) Run server

```bash
python manage.py runserver
```

API runs at:
- http://127.0.0.1:8000

## API Documentation

- Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/
- ReDoc: http://127.0.0.1:8000/api/schema/redoc/
- OpenAPI schema: http://127.0.0.1:8000/api/schema/

## Example API Flow

### Register

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPass123"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPass123"
}
```

Use returned access token in Authorization header:

```text
Authorization: Bearer <access_token>
```

### Create Task

```http
POST /tasks/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Complete assignment",
  "description": "Finish and submit project",
  "completed": false
}
```

## Testing

Run full test suite:

```bash
pytest
```

Run specific test files:

```bash
pytest apps/accounts/tests.py
pytest apps/tasks/tests.py
```

