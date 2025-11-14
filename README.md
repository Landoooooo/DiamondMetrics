# Baseball App

A full-stack application built with Django (backend), React (frontend), and PostgreSQL (database), all running in Docker containers.

## Project Structure

```
baseball/
├── backend/                 # Django backend
│   ├── baseball_app/       # Django project settings
│   ├── api/                # Django app for API endpoints
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml      # Docker orchestration
```

## Prerequisites

- Docker
- Docker Compose

## Getting Started

### 1. Clone and navigate to the project

```bash
cd baseball
```

### 2. Build and start the containers

```bash
docker-compose up --build
```

This command will:
- Build the Docker images for the backend and frontend
- Start the PostgreSQL database
- Run Django migrations
- Start the Django development server on http://localhost:8000
- Start the React development server on http://localhost:3000

### 3. Access the application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/

## Available Services

### Backend (Django)
- Runs on port 8000
- API endpoint: http://localhost:8000/api/health/
- Admin interface: http://localhost:8000/admin/

### Frontend (React)
- Runs on port 3000
- Automatically proxies API requests to the backend

### Database (PostgreSQL)
- Runs on port 5432
- Database name: baseball
- Username: postgres
- Password: postgres

## Development

### Making changes

The application is configured with hot-reload for both frontend and backend:

- **Backend**: Changes to Python files will automatically restart the Django server
- **Frontend**: Changes to React files will automatically refresh the browser

### Running commands in containers

**Django commands:**
```bash
# Create a superuser
docker-compose exec backend python manage.py createsuperuser

# Make migrations
docker-compose exec backend python manage.py makemigrations

# Run migrations
docker-compose exec backend python manage.py migrate

# Django shell
docker-compose exec backend python manage.py shell
```

**Frontend commands:**
```bash
# Install new npm packages
docker-compose exec frontend npm install <package-name>

# Run tests
docker-compose exec frontend npm test
```

**Database commands:**
```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d baseball
```

## Stopping the application

```bash
# Stop containers
docker-compose down

# Stop containers and remove volumes (this will delete the database data)
docker-compose down -v
```

## Production Considerations

This setup is for development purposes. For production:

1. Update the `SECRET_KEY` in backend settings
2. Set `DEBUG=False` in Django settings
3. Configure proper CORS origins
4. Use environment variables for sensitive data
5. Use a production-grade WSGI server (already configured with Gunicorn)
6. Build the React app for production
7. Set up proper static file serving
8. Configure HTTPS
9. Use production-grade database credentials

## API Endpoints

### Health Check
- **URL**: `/api/health/`
- **Method**: GET
- **Response**: `{"status": "ok", "message": "Baseball API is running!"}`

## Next Steps

- Add your models in `backend/api/models.py`
- Create API views in `backend/api/views.py`
- Add URL patterns in `backend/api/urls.py`
- Build React components in `frontend/src/`
- Connect frontend to your API endpoints

## Troubleshooting

**Port already in use:**
```bash
# Check what's using the port
lsof -i :3000  # or :8000, :5432
# Kill the process or change the port in docker-compose.yml
```

**Database connection issues:**
```bash
# Restart the database container
docker-compose restart db
```

**Fresh start:**
```bash
# Remove all containers, volumes, and images
docker-compose down -v
docker-compose up --build
```
# baseball
