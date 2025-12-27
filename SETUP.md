# Setup Instructions

## Prerequisites

1. Python 3.8 or higher
2. PostgreSQL 12 or higher
3. pip (Python package manager)

## Step-by-Step Setup

### 1. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE travel_sales_db;
CREATE USER travel_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE travel_sales_db TO travel_user;
```

### 2. Update Database Settings

Edit `travel_sales/settings.py` and update the database configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'travel_sales_db',
        'USER': 'travel_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### 6. Create Initial User Roles

After creating the superuser, you can create users with different roles through the Django admin panel or by using the following Python shell:

```bash
python manage.py shell
```

```python
from accounts.models import User

# Create a Manager
manager = User.objects.create_user(
    username='manager1',
    email='manager@example.com',
    password='password123',
    role='manager'
)

# Create a Sales Agent
agent = User.objects.create_user(
    username='agent1',
    email='agent@example.com',
    password='password123',
    role='sales_agent'
)

# Create an Accountant
accountant = User.objects.create_user(
    username='accountant1',
    email='accountant@example.com',
    password='password123',
    role='accountant'
)

# Create an Auditor
auditor = User.objects.create_user(
    username='auditor1',
    email='auditor@example.com',
    password='password123',
    role='auditor'
)
```

### 7. Create Static and Media Directories

```bash
mkdir static
mkdir media
mkdir media/invoices
```

### 8. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 9. Run Development Server

```bash
python manage.py runserver
```

### 10. Access the Application

- Open browser: http://127.0.0.1:8000
- Login with superuser credentials
- Access admin panel: http://127.0.0.1:8000/admin

## Initial Data Setup

### Create Sample Packages

1. Login as admin
2. Navigate to Packages section
3. Create tour packages with:
   - Package name
   - Destination
   - Base price
   - Tax percentage (GST)
   - Commission percentage
   - Maximum discount percentage

## Testing the System

1. **As Sales Agent:**
   - Create a booking
   - View your bookings

2. **As Manager:**
   - View pending validations
   - Approve/reject bookings

3. **As Accountant:**
   - View financial reports
   - Generate invoices

4. **As Auditor:**
   - View all data (read-only)
   - Access audit logs

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check database credentials in settings.py
- Ensure database exists

### Static Files Not Loading

- Run `python manage.py collectstatic`
- Check STATIC_URL and STATIC_ROOT in settings.py

### Permission Errors

- Check file permissions for media/ directory
- Ensure Django has write access

### Migration Errors

- Delete migration files (except __init__.py) and run makemigrations again
- Or reset database and run migrations fresh

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Update `SECRET_KEY` with a secure random key
3. Configure proper ALLOWED_HOSTS
4. Use a production WSGI server (gunicorn, uWSGI)
5. Set up proper static file serving
6. Configure database backups
7. Enable HTTPS
8. Set up proper logging

