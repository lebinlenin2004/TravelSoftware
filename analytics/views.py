from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from bookings.models import Booking
from packages.models import Package
from payments.models import Payment
from accounts.models import User
from accounts.decorators import manager_required, accountant_required


@login_required
def dashboard(request):
    """Main dashboard with analytics."""
    user = request.user
    
    # Date range for analytics (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Total sales and revenue
    bookings_query = Booking.objects.filter(created_at__gte=start_date)
    
    # Sales agents can only see their own data
    if user.is_sales_agent() and not user.is_admin():
        bookings_query = bookings_query.filter(created_by=user)
    
    total_sales = bookings_query.count()
    total_revenue = bookings_query.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Pending validations (only for managers/admins)
    pending_validations = 0
    if user.can_validate_booking():
        pending_validations = Booking.objects.filter(status='pending').count()
    
    # Monthly sales data for chart
    monthly_sales = []
    for i in range(6):  # Last 6 months
        month_start = (end_date - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_bookings = bookings_query.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        )
        
        monthly_sales.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_bookings.count(),
            'revenue': month_bookings.aggregate(total=Sum('total_amount'))['total'] or 0
        })
    
    monthly_sales.reverse()
    
    # Recent bookings
    recent_bookings = bookings_query.select_related('package', 'created_by')[:10]
    
    # Top packages
    top_packages = Package.objects.annotate(
        booking_count=Count('booking')
    ).order_by('-booking_count')[:5]
    
    # Agent performance (for managers/admins)
    agent_performance = None
    if user.can_view_analytics():
        agent_performance = User.objects.filter(role='sales_agent').annotate(
            total_bookings=Count('created_bookings', filter=Q(created_bookings__created_at__gte=start_date)),
            total_revenue=Sum('created_bookings__total_amount', filter=Q(created_bookings__created_at__gte=start_date))
        ).order_by('-total_revenue')[:10]
    
    context = {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'pending_validations': pending_validations,
        'monthly_sales': monthly_sales,
        'recent_bookings': recent_bookings,
        'top_packages': top_packages,
        'agent_performance': agent_performance,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
@manager_required
def sales_report(request):
    """Detailed sales report."""
    # Date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = timezone.now() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = timezone.now()
    
    # Filter bookings
    bookings = Booking.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).select_related('package', 'created_by')
    
    # Filter by package
    package_id = request.GET.get('package')
    if package_id:
        bookings = bookings.filter(package_id=package_id)
    
    # Filter by destination
    destination = request.GET.get('destination')
    if destination:
        bookings = bookings.filter(package__destination__icontains=destination)
    
    # Summary statistics
    total_bookings = bookings.count()
    total_revenue = bookings.aggregate(total=Sum('total_amount'))['total'] or 0
    total_tax = bookings.aggregate(total=Sum('tax_amount'))['total'] or 0
    total_commission = bookings.aggregate(total=Sum('commission_amount'))['total'] or 0
    approved_bookings = bookings.filter(status='approved').count()
    rejected_bookings = bookings.filter(status='rejected').count()
    
    # Sales by package
    sales_by_package = bookings.values('package__name').annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('-revenue')
    
    # Sales by destination
    sales_by_destination = bookings.values('package__destination').annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('-revenue')
    
    # Get all packages for filter
    packages = Package.objects.all()
    
    context = {
        'bookings': bookings,
        'start_date': start_date,
        'end_date': end_date,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'total_tax': total_tax,
        'total_commission': total_commission,
        'approved_bookings': approved_bookings,
        'rejected_bookings': rejected_bookings,
        'sales_by_package': sales_by_package,
        'sales_by_destination': sales_by_destination,
        'packages': packages,
        'package_id': package_id,
        'destination': destination,
    }
    
    return render(request, 'analytics/sales_report.html', context)


@login_required
@accountant_required
def financial_report(request):
    """Financial and GST report."""
    # Date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = timezone.now().replace(day=1)  # Start of current month
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = timezone.now()
    
    # Filter bookings
    bookings = Booking.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date,
        status='approved'
    ).select_related('package')
    
    # Financial summary
    total_revenue = bookings.aggregate(total=Sum('total_amount'))['total'] or 0
    total_subtotal = bookings.aggregate(total=Sum('subtotal'))['total'] or 0
    total_tax = bookings.aggregate(total=Sum('tax_amount'))['total'] or 0
    total_commission = bookings.aggregate(total=Sum('commission_amount'))['total'] or 0
    total_discount = bookings.aggregate(total=Sum('discount_amount'))['total'] or 0
    
    # GST breakdown by rate
    gst_breakdown = bookings.values('package__tax_percentage').annotate(
        count=Count('id'),
        subtotal=Sum('subtotal'),
        tax_amount=Sum('tax_amount')
    ).order_by('package__tax_percentage')
    
    # Payment summary
    payments = Payment.objects.filter(
        booking__in=bookings
    )
    total_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    pending_payments = total_revenue - total_paid
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'total_subtotal': total_subtotal,
        'total_tax': total_tax,
        'total_commission': total_commission,
        'total_discount': total_discount,
        'gst_breakdown': gst_breakdown,
        'total_paid': total_paid,
        'pending_payments': pending_payments,
        'bookings': bookings[:50],  # Limit for display
    }
    
    return render(request, 'analytics/financial_report.html', context)


@login_required
@manager_required
def agent_performance(request):
    """Agent performance report."""
    # Date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = timezone.now() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = timezone.now()
    
    # Agent statistics
    agents = User.objects.filter(role='sales_agent').annotate(
        total_bookings=Count('created_bookings', filter=Q(
            created_bookings__created_at__gte=start_date,
            created_bookings__created_at__lte=end_date
        )),
        approved_bookings=Count('created_bookings', filter=Q(
            created_bookings__status='approved',
            created_bookings__created_at__gte=start_date,
            created_bookings__created_at__lte=end_date
        )),
        rejected_bookings=Count('created_bookings', filter=Q(
            created_bookings__status='rejected',
            created_bookings__created_at__gte=start_date,
            created_bookings__created_at__lte=end_date
        )),
        total_revenue=Sum('created_bookings__total_amount', filter=Q(
            created_bookings__created_at__gte=start_date,
            created_bookings__created_at__lte=end_date
        )),
        avg_booking_value=Avg('created_bookings__total_amount', filter=Q(
            created_bookings__created_at__gte=start_date,
            created_bookings__created_at__lte=end_date
        ))
    ).order_by('-total_revenue')
    
    context = {
        'agents': agents,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'analytics/agent_performance.html', context)

