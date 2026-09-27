# Lab Components Management System — Backend

A production-quality Flask REST API for managing lab components, student requests, issue/return records, damage reports, and complaints.

## Architecture

```
React + Vite Frontend
        |
        | HTTP REST API
        ↓
Python Flask Backend (this)
        |
        | psycopg2
        ↓
PostgreSQL Database
```

## Requirements

- Python 3.10+
- PostgreSQL 13+
- pip

## Installation

### 1. Clone and navigate

```bash
cd backend
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. PostgreSQL Setup

Ensure PostgreSQL is installed and running. The seeder script will automatically create the database.

### 5. Configure environment variables

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lab_components_db
DB_USER=postgres
DB_PASSWORD=your_actual_password

JWT_SECRET_KEY=your_random_secret_key_here

FINE_PER_DAY=10
DEFAULT_ISSUE_DAYS=14

CORS_ORIGIN=http://localhost:5173
```

### 6. Seed the database

```bash
python seed_data.py
```

This will:
- Create the `lab_components_db` database
- Create all tables
- Insert dummy users with hashed passwords
- Insert sample components

### 7. Run the server

```bash
python app.py
```

The API will be available at: **http://localhost:5000**

## API Endpoints

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check with DB status |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | Login and get JWT token |
| GET | `/api/profile` | Get authenticated user profile |

### Components
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/components` | Any | List all components |
| GET | `/api/components/<id>` | Any | Get single component |
| GET | `/api/components/search?q=term` | Any | Search components |
| POST | `/api/components` | Faculty | Create component |
| PUT | `/api/components/<id>` | Faculty | Update component |
| PATCH | `/api/components/<id>/status` | Faculty | Change status |

### Requests
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/requests` | Student | Create component request |
| GET | `/api/requests` | Any | List requests |
| GET | `/api/requests/<id>` | Any | Get single request |
| PUT | `/api/requests/<id>/approve` | Faculty | Approve request |
| PUT | `/api/requests/<id>/reject` | Faculty | Reject request |

### Issues
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/issues` | Faculty | Issue component to student |
| GET | `/api/issues` | Any | List issue records |
| GET | `/api/issues/<id>` | Any | Get single issue |
| PUT | `/api/issues/<id>/return` | Any | Return component |

### Damages
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/damages` | Faculty | Create damage record |
| GET | `/api/damages` | Any | List damage records |
| GET | `/api/damages/<id>` | Any | Get single damage record |

### Complaints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/complaints` | Student | Create complaint |
| GET | `/api/complaints` | Any | List complaints |
| GET | `/api/complaints/<id>` | Any | Get single complaint |
| PUT | `/api/complaints/<id>` | Faculty | Update complaint status |

## Authentication

All endpoints except `/api/health` and `/api/login` require a JWT token.

### Login

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@college.edu", "password": "password123"}'
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOi...",
    "user": {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@college.edu",
      "role": "student"
    }
  }
}
```

### Using the token

Include the token in the `Authorization` header:

```bash
curl http://localhost:5000/api/components \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Default Accounts

| Email | Password | Role |
|-------|----------|------|
| alice@college.edu | password123 | student |
| bob@college.edu | password123 | student |
| charlie@college.edu | password123 | student |
| sarah.faculty@college.edu | password123 | faculty |
| james.faculty@college.edu | password123 | faculty |

## Example Requests

### Create a component request (Student)

```bash
curl -X POST http://localhost:5000/api/requests \
  -H "Authorization: Bearer STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"component_id": 1}'
```

### Approve a request (Faculty)

```bash
curl -X PUT http://localhost:5000/api/requests/1/approve \
  -H "Authorization: Bearer FACULTY_TOKEN"
```

### Issue a component (Faculty)

```bash
curl -X POST http://localhost:5000/api/issues \
  -H "Authorization: Bearer FACULTY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"request_id": 1}'
```

### Return a component

```bash
curl -X PUT http://localhost:5000/api/issues/1/return \
  -H "Authorization: Bearer STUDENT_TOKEN"
```

## Testing

Run the test suite:

```bash
# Ensure the database is seeded first
python seed_data.py

# Run tests
python -m pytest tests/ -v
```

## Common Errors

| Error | Solution |
|-------|----------|
| `psycopg2.OperationalError: connection refused` | Make sure PostgreSQL is running |
| `FATAL: password authentication failed` | Check DB_PASSWORD in .env |
| `FATAL: database "lab_components_db" does not exist` | Run `python seed_data.py` |
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install -r requirements.txt` |
| `401 Unauthorized` | Include valid JWT in Authorization header |
| `403 Forbidden` | Operation requires different role (student/faculty) |

## Project Structure

```
backend/
├── app.py                  # Flask app entry point
├── config.py               # Configuration from environment
├── requirements.txt        # Python dependencies
├── seed_data.py            # Database seeder
├── .env.example            # Environment template
├── .gitignore
├── README.md
├── models/                 # Database operations
│   ├── user.py
│   ├── component.py
│   ├── request.py
│   ├── issue.py
│   ├── damage.py
│   └── complaint.py
├── routes/                 # API route handlers
│   ├── auth_routes.py
│   ├── component_routes.py
│   ├── request_routes.py
│   ├── issue_routes.py
│   ├── damage_routes.py
│   └── complaint_routes.py
├── utils/                  # Shared utilities
│   ├── auth.py             # JWT helpers & decorators
│   ├── database.py         # PostgreSQL connection
│   ├── validators.py       # Input validation
│   └── responses.py        # Standardized responses
└── tests/                  # Automated test suite
    ├── conftest.py
    ├── test_auth.py
    ├── test_components.py
    ├── test_requests.py
    ├── test_issues.py
    ├── test_damage.py
    └── test_complaints.py
```

## Business Rules

- **Roles**: `student` and `faculty` — enforced server-side
- **Queue**: When `available_quantity = 0`, requests get queue positions (FCFS)
- **Fine**: Configurable via `FINE_PER_DAY` in `.env` (default ₹10/day)
- **Issue duration**: Configurable via `DEFAULT_ISSUE_DAYS` (default 14 days)
- **Borrowed quantity**: Computed as `total_quantity - available_quantity` (not stored)
- **Historical records**: Issue and damage records are never deleted
- **Passwords**: Hashed with Werkzeug's scrypt (never stored or returned as plaintext)
