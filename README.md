# Task Manager API

A production-grade REST API for managing tasks, built with **Django**, **Django REST Framework**, **PostgreSQL**, and **Docker**.

## Features

- **JWT Authentication**: Email-based registration & login with access/refresh tokens
- **Task Management**: Full CRUD operations on tasks
- **Authorization**: Users manage their own tasks; Admins manage all tasks
- **Role-Based Access**: Support for user roles (Admin, Regular User)
- **Pagination & Filtering**: Paginated responses with filter by completion status
- **Sorting**: Order tasks by creation date or completion status
- **API Documentation**: Auto-generated Swagger UI & ReDoc with OpenAPI schema
- **Comprehensive Testing**: pytest-based test suite with good coverage
- **Docker Support**: Containerized deployment with Docker Compose

## Tech Stack

- **Backend**: Python 3.11, Django 4.2, Django REST Framework
- **Authentication**: SimpleJWT with custom Email-based User Model
- **Database**: PostgreSQL (v15) / SQLite (development)
- **API Docs**: drf-spectacular (Swagger/ReDoc)
- **Testing**: pytest, pytest-django
- **Infrastructure**: Docker & Docker Compose

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional, for PostgreSQL)
- Git

### Installation & Setup

#### 1. Clone Repository & Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Setup Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (SQLite for dev, PostgreSQL for production)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# PostgreSQL (optional, uncomment to use)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=taskmanager
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432
```

#### 4. Apply Migrations
```bash
python manage.py migrate
```

#### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser --email admin@example.com
```

#### 6. Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`.

---

## API Documentation

### Access Points
- **Swagger UI**: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- **ReDoc**: [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/)
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

### Authentication Endpoints

#### 1. Register User
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "strongpassword123"
}

# Response (201 Created):
{
  "id": 1,
  "email": "user@example.com"
}
```

#### 2. Login User (Get JWT Tokens)
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "strongpassword123"
}

# Response (200 OK):
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 3. Refresh Access Token
```bash
POST /auth/refresh
Content-Type: application/json

{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Response (200 OK):
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### Task Endpoints

**All task endpoints require authentication**. Include the JWT token in the Authorization header:
```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

#### 1. List All Tasks (Paginated)
```bash
GET /tasks/?page=1&completed=false&ordering=-created_at
Authorization: Bearer YOUR_ACCESS_TOKEN

# Response (200 OK):
{
  "count": 15,
  "next": "http://localhost:8000/tasks/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-03-26T08:00:00Z",
      "updated_at": "2026-03-26T08:00:00Z"
    },
    ...
  ]
}
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `completed`: Filter by completion status (true/false)
- `ordering`: Sort by field (`created_at`, `-created_at`, `completed`, `-completed`)

#### 2. Get Specific Task
```bash
GET /tasks/1/
Authorization: Bearer YOUR_ACCESS_TOKEN

# Response (200 OK):
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-03-26T08:00:00Z",
  "updated_at": "2026-03-26T08:00:00Z"
}
```

#### 3. Create New Task
```bash
POST /tasks/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "title": "Complete project",
  "description": "Finish task manager API",
  "completed": false
}

# Response (201 Created):
{
  "id": 2,
  "title": "Complete project",
  "description": "Finish task manager API",
  "completed": false,
  "created_at": "2026-03-26T09:30:00Z",
  "updated_at": "2026-03-26T09:30:00Z"
}
```

#### 4. Update Task
```bash
PUT /tasks/1/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Updated list",
  "completed": true
}

# Response (200 OK):
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Updated list",
  "completed": true,
  "created_at": "2026-03-26T08:00:00Z",
  "updated_at": "2026-03-26T10:00:00Z"
}
```

#### 5. Delete Task
```bash
DELETE /tasks/1/
Authorization: Bearer YOUR_ACCESS_TOKEN

# Response (204 No Content)
```

---

## Testing

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage Report
```bash
pytest --cov=apps --cov-report=html
```

### Run Specific Test File
```bash
pytest apps/tasks/tests.py
pytest apps/accounts/tests.py
```

### Run Specific Test Class/Method
```bash
pytest apps/tasks/tests.py::TestTasks::test_create_task
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Test Coverage
The test suite covers:
- User registration and authentication
- JWT token generation and refresh
- Task CRUD operations (Create, Read, Update, Delete)
- Permission validation (users can only access their own tasks)
- Admin privileges (admins can access all tasks)
- Pagination
- Filtering by completion status
- Unauthenticated access rejection
- Invalid input handling

---

## Docker Setup (PostgreSQL)

### Start Services with Docker Compose
```bash
docker compose up -d
```

This will:
- Start PostgreSQL container on port 5432
- Create the `taskmanager` database

### Update .env for Docker
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=taskmanager
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### Run Migrations with Docker
```bash
docker compose exec web python manage.py migrate
```

### Stop Services
```bash
docker compose down
```

---

## Project Structure

```
├── apps/                    # Django Applications
│   ├── accounts/           # User Authentication
│   │   ├── models.py       # Custom User model
│   │   ├── serializers.py  # User registration serializer
│   │   ├── views.py        # Registration view
│   │   ├── urls.py         # Auth routes
│   │   ├── managers.py     # Custom user manager
│   │   └── tests.py        # Auth tests
│   ├── tasks/              # Task Management
│   │   ├── models.py       # Task model
│   │   ├── serializers.py  # Task serializer
│   │   ├── views.py        # Task viewset
│   │   ├── permissions.py  # Custom permissions
│   │   ├── urls.py         # Task routes
│   │   └── tests.py        # Task tests
│   └── __init__.py
├── config/                 # Project Configuration
│   ├── settings/
│   │   ├── base.py        # Base settings
│   │   ├── dev.py         # Development settings
│   │   └── prod.py        # Production settings
│   ├── urls.py            # Main URL routing
│   ├── wsgi.py            # WSGI config
│   └── asgi.py            # ASGI config
├── .env                   # Environment variables
├── .env.example           # Environment template
├── docker-compose.yml     # Docker services config
├── Dockerfile             # Python container config
├── manage.py              # Django CLI
├── pytest.ini             # pytest configuration
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## Authentication & Authorization

### Authentication Flow
1. User registers via `/auth/register` with email and password
2. User logs in via `/auth/login` and receives access & refresh tokens
3. Access token is included in the `Authorization: Bearer` header for protected endpoints
4. When access token expires, refresh token is used to get a new access token

### Permissions
- **Public Endpoints**: `/auth/register`, `/auth/login`, `/auth/refresh`, `/api/schema/`
- **Protected Endpoints**: All `/tasks/` endpoints require JWT authentication
- **User Isolation**: Regular users can only see/modify their own tasks
- **Admin Access**: Users with `is_staff=True` can access all tasks

### User Roles
- **Regular User**: Can create, read, update, delete only their own tasks
- **Admin User**: Can access and manage all tasks; can use Django admin

---

## Development Tips

### Create a Test User
```bash
# Using the API
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Get JWT Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Make Authenticated Request
```bash
curl -X GET http://localhost:8000/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Access Django Admin
```bash
# Create superuser
python manage.py createsuperuser --email admin@example.com

# Visit http://localhost:8000/admin/
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key (keep secret in production) | `django-insecure-...` |
| `DEBUG` | Debug mode (set to False in production) | `True` / `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `127.0.0.1,localhost` |
| `DB_ENGINE` | Database engine | `django.db.backends.sqlite3` or `django.db.backends.postgresql` |
| `DB_NAME` | Database name | `db.sqlite3` or `taskmanager` |
| `DB_USER` | Database user (PostgreSQL) | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_HOST` | Database host | `localhost` or `db` (Docker) |
| `DB_PORT` | Database port | `5432` |

---

## Production Deployment

### Before Deployment
1. Set `DEBUG=False` in `.env`
2. Generate a secure `SECRET_KEY`
3. Update `ALLOWED_HOSTS` with your domain
4. Use PostgreSQL instead of SQLite
5. Use environment-specific settings (`config/settings/prod.py`)
6. Set up SSL/HTTPS
7. Configure proper logging and monitoring

### Deployment Options
- **Traditional Server**: Use Gunicorn + Nginx + PostgreSQL
- **Docker**: Deploy Docker containers to cloud (AWS, GCP, Azure, Heroku)
- **PaaS**: Deploy to Heroku, PythonAnywhere, or similar platforms

### Example Gunicorn Command
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 📝 API Response Codes

| Code | Meaning |
|------|---------|
| `200` | OK - Request successful |
| `201` | Created - Resource created successfully |
| `204` | No Content - Resource deleted successfully |
| `400` | Bad Request - Invalid input |
| `401` | Unauthorized - Missing or invalid authentication |
| `403` | Forbidden - User lacks permission |
| `404` | Not Found - Resource doesn't exist |
| `500` | Server Error - Internal server error |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is open source and available under the MIT License.

---

## Support

For issues, questions, or suggestions:
1. Open an issue on GitHub
2. Send an email to support@example.com
3. Check the API documentation at `/api/schema/swagger-ui/`

---

**Note**: Ensure to change `SECRET_KEY` and database passwords before using this application in production.
#   Z i p p e e - A s s i g n m e n t  
 