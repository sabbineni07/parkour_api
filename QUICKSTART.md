# Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- Git (optional)

## Getting Started

1. **Copy environment file**
   ```bash
   cp env.example .env
   ```

2. **Start the application with Docker**
   ```bash
   # Development mode (with hot-reload)
   docker compose -f docker-compose.dev.yml up --build
   
   # Or use Makefile
   make build
   make up
   ```
   
   **Note:** Database tables are automatically created on startup. The startup process will:
   - Wait for the database to be ready
   - Create all tables (users, datasets, etc.)
   - Create the default admin user (username: `admin`, password: `admin123`)

3. **Database tables are automatically created on startup**
   
   The tables are automatically created when the containers start. If you need to manually initialize:
   ```bash
   # Using Docker
   docker compose -f docker-compose.dev.yml exec web flask init-db
   
   # Or use Makefile
   make init-db
   
   # Or run the init script directly
   docker compose -f docker-compose.dev.yml exec web python init_tables.py
   ```

4. **Test the API**
   ```bash
   # Health check
   curl http://localhost:5001/health
   
   # Register a user
   curl -X POST http://localhost:5001/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "password123",
       "first_name": "Test",
       "last_name": "User"
     }'
   
   # Login
   curl -X POST http://localhost:5001/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "password123"
     }'
   ```

## Default Admin User

After running `flask init-db`, you can login with:
- Username: `admin`
- Password: `admin123`

## Useful Commands

```bash
# View logs
make logs

# Run tests
make test

# Stop services
make down

# Clean everything (removes volumes)
make clean

# Create database migration
make migrate MESSAGE="Add new table"

# Apply migrations
make upgrade

# Open Python shell
make shell
```

## Access Points

- **API**: http://localhost:5001
- **Health Check**: http://localhost:5001/health
- **Database**: localhost:5432 (postgres/password)

## Troubleshooting

### Port already in use
If port 5000 or 5432 is already in use, you can modify the ports in `docker-compose.dev.yml`.

### Database connection errors
Make sure the database container is healthy before starting the web container. Check with:
```bash
docker compose -f docker-compose.dev.yml ps
```

### Tables missing after startup
If tables are missing, the automatic initialization may have failed. Try:
```bash
# Run the init script manually
docker compose -f docker-compose.dev.yml exec web python init_tables.py

# Or use the Flask command
make init-db
```

### Reset database
```bash
make clean
make build
make up
# Tables will be created automatically, but you can also run:
make init-db
```


