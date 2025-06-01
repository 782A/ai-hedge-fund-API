# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# The DJANGO_SETTINGS_MODULE will typically be set by the environment (e.g., in docker-compose.yml or Kubernetes)
# ENV DJANGO_SETTINGS_MODULE=webapp.settings

# Set work directory within the container
WORKDIR /app/my_django_project

# Install system dependencies (example for PostgreSQL client, uncomment if needed)
# RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container
COPY . .

# Collect static files (this can also be part of a startup script/entrypoint.sh)
# Ensure STATIC_ROOT is defined in settings.py for this to work
# RUN python manage.py collectstatic --noinput --clear

# Expose port Gunicorn will run on
EXPOSE 8000

# Command to run the application (example using Gunicorn)
# This assumes your Django project's WSGI application is at webapp.wsgi:application
# The actual command might be in an entrypoint.sh script for more complex startup logic
# (e.g., running migrations, then starting Gunicorn).
# CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "webapp.wsgi:application"]

# For a startup script:
# COPY ./entrypoint.sh /app/my_django_project/entrypoint.sh
# RUN chmod +x /app/my_django_project/entrypoint.sh
# CMD ["/app/my_django_project/entrypoint.sh"]
# An example entrypoint.sh might look like:
# #!/bin/sh
# python manage.py makemigrations --noinput
# python manage.py migrate --noinput
# python manage.py collectstatic --noinput --clear
# gunicorn --workers 3 --bind 0.0.0.0:8000 webapp.wsgi:application
