# SyncSphere Backend

A production-ready backend for SyncSphere built with FastAPI, PostgreSQL, SQLAlchemy, and Alembic.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Powerful relational database
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **JWT Authentication** - Secure token-based authentication
- **Role-based Access Control** - Multi-level permission system
- **Soft Delete** - Data preservation with soft delete functionality
- **Comprehensive Models** - Users, Events, Leave Requests, Notifications, and more
- **Production-ready** - Structured for scalability and maintainability

## Project Structure

```
SyncSphere_db/
├── app/
│   ├── api/                    # API endpoints
│   │   └── api_v1/
│   │       ├── endpoints/      # Route handlers
│   │       └── api.py          # API router
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Configuration settings
│   │   ├── security.py         # JWT and password handling
│   │   └── deps.py             # Dependencies
│   ├── db/                     # Database configuration
│   │   ├── session.py          # Database session management
│   │   └── base.py             # Base model classes
│   ├── models/                 # Database models
│   │   ├── user.py             # User model
│   │   ├── event.py            # Event model
│   │   ├── holiday.py          # Holiday model
│   │   ├── leave_request.py    # Leave request model
│   │   ├── notification.py     # Notification model
│   │   ├── sms_log.py          # SMS log model
│   │   ├── email_log.py        # Email log model
│   │   ├── reminder_job.py     # Reminder job model
│   │   └── permission.py       # Permission model
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py             # Authentication schemas
│   │   ├── user.py             # User schemas
│   │   ├── event.py            # Event schemas
│   │   ├── leave_request.py    # Leave request schemas
│   │   └── notification.py     # Notification schemas
│   ├── services/               # Business logic
│   ├── repositories/           # Data access layer
│   ├── middleware/              # Custom middleware
│   ├── workers/                # Background workers
│   ├── notifications/          # Notification handlers
│   └── main.py                 # FastAPI application
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   ├── env.py                 # Alembic environment
│   └── script.py.mako         # Migration template
├── tests/                      # Test files
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── alembic.ini                # Alembic configuration
└── README.md                   # This file
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SyncSphere_db
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env` file and update the database connection string
   - Update `SECRET_KEY` for production
   - Configure other settings as needed

5. **Set up PostgreSQL database**
   ```sql
   CREATE DATABASE syncsphere_db;
   CREATE USER syncsphere_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE syncsphere_db TO syncsphere_user;
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

## Usage

### Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade migrations
alembic downgrade -1
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

### Users
- `GET /api/v1/users/` - Get all users (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

### Events
- `GET /api/v1/events/` - Get events
- `POST /api/v1/events/` - Create event
- `GET /api/v1/events/{event_id}` - Get event by ID
- `PUT /api/v1/events/{event_id}` - Update event
- `DELETE /api/v1/events/{event_id}` - Delete event

### Leave Requests
- `GET /api/v1/leave-requests/` - Get leave requests
- `POST /api/v1/leave-requests/` - Create leave request
- `GET /api/v1/leave-requests/{id}` - Get leave request by ID
- `PUT /api/v1/leave-requests/{id}` - Update leave request
- `POST /api/v1/leave-requests/{id}/approve` - Approve leave request
- `POST /api/v1/leave-requests/{id}/reject` - Reject leave request

### Notifications
- `GET /api/v1/notifications/` - Get notifications
- `POST /api/v1/notifications/` - Create notification
- `POST /api/v1/notifications/{id}/mark-read` - Mark notification as read
- `POST /api/v1/notifications/mark-all-read` - Mark all notifications as read
- `DELETE /api/v1/notifications/{id}` - Delete notification

## User Roles

- **SUPER_ADMIN** - Full system access
- **ADMIN** - Administrative access
- **HR_MANAGER** - HR and leave management
- **EVENT_MANAGER** - Event management
- **EMPLOYEE** - Basic user access

## Database Models

### Core Features
- **Soft Delete** - All models support soft delete with `is_deleted` flag
- **Timestamps** - Automatic `created_at` and `updated_at` fields
- **UUID** - Unique identifier for each record
- **Audit Trail** - Track changes and deletions

### Models
- **User** - User management with roles and authentication
- **Event** - Event scheduling and management
- **Holiday** - Holiday management
- **LeaveRequest** - Leave request workflow
- **Notification** - User notifications
- **SmsLog** - SMS communication tracking
- **EmailLog** - Email communication tracking
- **ReminderJob** - Scheduled reminders
- **Permission** - Role-based permissions

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/syncsphere_db

# JWT
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=SyncSphere
DEBUG=True
ENVIRONMENT=development

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS (optional)
SMS_API_KEY=your-sms-api-key
```

## Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - bcrypt for password security
- **Role-based Access Control** - Multi-level permission system
- **CORS Protection** - Cross-origin resource sharing configuration
- **Input Validation** - Pydantic schemas for data validation
- **SQL Injection Protection** - SQLAlchemy ORM protection

## Development

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

## Production Deployment

### Environment Setup
1. Set `ENVIRONMENT=production`
2. Use strong `SECRET_KEY`
3. Configure proper database connection
4. Set up SSL certificates
5. Configure reverse proxy (nginx)
6. Set up monitoring and logging

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run tests and ensure they pass
6. Submit a pull request

## License

This project is licensed under the MIT License.
