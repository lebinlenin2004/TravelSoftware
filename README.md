# Travel & Tourism Sales Analysis and Validation Software

A comprehensive Django-based system for managing tour package sales, bookings, validations, and analytics.

## Features

### Core Functionality
- **User Management**: Role-based access control (Admin, Sales Agent, Manager, Accountant, Auditor)
- **Package Management**: Create and manage tour packages with pricing, tax, and commission settings
- **Booking System**: Create bookings with automatic price calculation, discount validation, and GST calculation
- **Sales Validation**: Manager approval/rejection workflow with automatic flagging of suspicious activities
- **Payment Tracking**: Record payments, track payment status, and manage invoices
- **Analytics & Reports**: Dashboard with sales trends, agent performance, and financial reports
- **Audit Logging**: Complete audit trail of all system activities

### Key Features
- Automatic price calculation based on package and number of travelers
- Discount limit validation
- GST (Tax) auto-calculation
- Duplicate booking detection
- Price mismatch detection
- Invoice PDF generation
- Role-based dashboard views
- Monthly sales charts
- Agent performance tracking

## Tech Stack

- **Backend**: Python Django 4.2.7
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: PostgreSQL
- **PDF Generation**: ReportLab

## Installation

1. **Clone the repository**
   ```bash
   cd D:\TravelSoftware
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   - Create a database named `travel_sales_db`
   - Update database credentials in `travel_sales/settings.py` if needed

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open browser: http://127.0.0.1:8000
   - Login with superuser credentials

## User Roles

### Admin
- Full access to all features
- Can manage packages, users, and all bookings
- Can validate bookings
- Access to all reports

### Sales Agent
- Can create bookings
- Can view own bookings only
- Limited dashboard access

### Manager
- Can validate bookings (approve/reject)
- Can view all bookings
- Access to analytics and reports
- Can view pending validations

### Accountant
- Access to financial reports
- GST reports
- Payment tracking
- Read-only access to bookings

### Auditor
- Read-only access to all data
- Can view audit logs
- No modification permissions

## Project Structure

```
TravelSoftware/
├── accounts/          # User management and authentication
├── packages/         # Tour package management
├── bookings/         # Booking and sales entry
├── payments/         # Payment and invoice management
├── analytics/        # Reports and analytics
├── travel_sales/     # Main project settings
├── templates/        # HTML templates
├── static/           # Static files (CSS, JS, images)
└── media/            # User uploaded files (invoices)
```

## Key Models

- **User**: Custom user model with role-based permissions
- **Package**: Tour packages with pricing and tax settings
- **Booking**: Sales entries with validation flags
- **Payment**: Payment tracking and status
- **Invoice**: Invoice generation and storage
- **AuditLog**: Complete audit trail

## Usage

1. **Create Packages**: Admin creates tour packages with pricing
2. **Create Bookings**: Sales agents create bookings for customers
3. **Validate Bookings**: Managers review and approve/reject bookings
4. **Record Payments**: Track payments for approved bookings
5. **Generate Invoices**: Create PDF invoices for bookings
6. **View Reports**: Access analytics and financial reports

## Development Notes

- All monetary values use Decimal fields for precision
- Server-side validation enforced for all critical operations
- Role-based permissions checked at view level
- Audit logs created for all data modifications
- PostgreSQL indexes added for performance

## Security

- CSRF protection enabled
- Password validation enforced
- Role-based access control
- Server-side validation for all inputs
- Audit logging for compliance

## License

This project is proprietary software.

