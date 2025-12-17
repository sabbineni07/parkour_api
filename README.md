# Parkour API

A Flask-based REST API built with PostgreSQL database and containerized with Docker. This API provides authentication and user management capabilities with JWT tokens.

## 🚀 Features

- **🔐 JWT Authentication**: Complete authentication system with login, registration, and profile management
- **👥 User Management**: User registration, profile updates, and user management
- **🗄️ PostgreSQL Database**: Robust data storage with proper relationships and migrations
- **🐳 Docker Support**: Full containerization with development and production environments
- **🌐 CORS Configuration**: Properly configured for frontend integration
- **🔒 Security**: Password hashing, input validation, and secure authentication
- **📈 Database Migrations**: Flask-Migrate integration for schema management

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Docker Setup](#-docker-setup)
- [Development](#-development)
- [Testing](#-testing)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (if running locally)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd parkour_api
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run with Docker Compose (Recommended)**
   ```bash
   # For development
   docker-compose -f docker-compose.dev.yml up --build
   
   # For production
   docker-compose up --build
   ```

5. **Initialize the database**
   ```bash
   # Using Docker
   docker-compose -f docker-compose.dev.yml exec web flask init-db
   
   # Or locally
   flask init-db
   ```

6. **Access the application**
   - **API**: http://localhost:5000
   - **Health Check**: http://localhost:5000/health

## 🔌 API Endpoints

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer <access_token>
```

#### Update Profile
```http
PUT /api/auth/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com"
}
```

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "parkour-api"
}
```

## 🐳 Docker Setup

### Development Environment

```bash
docker-compose -f docker-compose.dev.yml up --build
```

This will:
- Start PostgreSQL database on port 5432
- Start Flask API in development mode with hot-reload on port 5000
- Automatically create database tables on startup

### Production Environment

```bash
docker-compose up --build
```

This will:
- Start PostgreSQL database
- Start Flask API with Gunicorn on port 5000
- Use production settings

### Database Migrations

```bash
# Create a new migration
docker-compose -f docker-compose.dev.yml exec web flask db migrate -m "Description"

# Apply migrations
docker-compose -f docker-compose.dev.yml exec web flask db upgrade
```

## 💻 Development

### Running Locally (without Docker)

1. **Install PostgreSQL** and create a database:
   ```bash
   createdb parkour_db
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

5. **Initialize database**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   flask init-db
   ```

6. **Run the application**:
   ```bash
   flask run
   # Or
   python app.py
   ```

### Project Structure

```
parkour_api/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── services/            # Business logic
│   │   └── __init__.py
│   ├── utils/               # Utility functions
│   │   └── __init__.py
│   └── tests/               # Tests
│       └── __init__.py
├── app.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Production Docker Compose
├── docker-compose.dev.yml  # Development Docker Compose
├── init.sql                # Database initialization
├── pytest.ini             # Pytest configuration
└── README.md               # This file
```

## 🧪 Testing

### Run Tests

```bash
# Using Docker
docker-compose -f docker-compose.dev.yml exec web pytest

# Locally
pytest
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_APP` | Flask application entry point | `app.py` |
| `FLASK_ENV` | Flask environment (development/production) | `development` |
| `SECRET_KEY` | Flask secret key | Required |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET_KEY` | JWT token secret key | Required |
| `JWT_ACCESS_TOKEN_EXPIRES` | JWT token expiration in seconds | `3600` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:4200,...` |

## 🔒 Security Notes

- Always change default secrets in production
- Use strong passwords for database
- Enable HTTPS in production
- Regularly update dependencies
- Review and configure CORS origins appropriately

## 📄 License

This project is licensed under the MIT License.


