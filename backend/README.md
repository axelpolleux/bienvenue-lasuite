# Bienvenue à La Suite — Django REST Framework BFF

Backend API service for the "Bienvenue à La Suite" onboarding application.

## Quick Start

```bash
# Apply database migrations
python manage.py migrate

# Seed demonstration data (templates, tasks, demo agents)
python manage.py seed_demo_data

# Run local development server
python manage.py runserver 0.0.0.0:8000
```

## Running Tests

```bash
python manage.py test src.onboarding
```
