from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import Booking, AuditLog
from .forms import BookingForm, BookingValidationForm
from accounts.decorators import sales_agent_required, manager_required
import uuid


def create_audit_log(model_name, object_id, action, user, changes=None, notes='', ip_address=None):
    """Helper function to create audit logs."""
    AuditLog.objects.create(
        model_name=model_name,
        object_id=object_id,
        action=action,
        user=user,
        changes=changes or {},
        notes=notes,
        ip_address=ip_address
    )


@login_required
@sales_agent_required
def booking_create(request):
    """Create a new booking."""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.created_by = request.user
            booking.booking_number = f"BK{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
            
            # Calculate totals
            booking.calculate_totals()
            
            # Validate pricing and check for duplicates
            pricing_errors = booking.validate_pricing()
            booking.check_duplicate()
            
            booking.save()
            
            # Create audit log
            create_audit_log(
                'Booking',
                booking.id,
                'create',
                request.user,
                {'booking_number': booking.booking_number},
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            if pricing_errors or booking.duplicate_booking_flag:
                messages.warning(
                    request, 
                    f'Booking created but flagged for review: {"; ".join(pricing_errors)}'
                )
            else:
                messages.success(request, f'Booking #{booking.booking_number} created successfully.')
            
            return redirect('bookings:list')
    else:
        form = BookingForm()
    
    return render(request, 'bookings/form.html', {'form': form, 'title': 'Create Booking'})


@login_required
def booking_list(request):
    """List all bookings."""
    bookings = Booking.objects.select_related('package', 'created_by', 'validated_by').all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    # Sales agents can only see their own bookings
    if request.user.is_sales_agent() and not request.user.is_admin():
        bookings = bookings.filter(created_by=request.user)
    
    # Search
    search = request.GET.get('search')
    if search:
        bookings = bookings.filter(
            Q(booking_number__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(customer_email__icontains=search)
        )
    
    # Filter by flags
    flagged = request.GET.get('flagged')
    if flagged == 'true':
        bookings = bookings.filter(
            Q(price_mismatch_flag=True) |
            Q(excess_discount_flag=True) |
            Q(duplicate_booking_flag=True)
        )
    
    paginator = Paginator(bookings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'bookings/list.html', {
        'page_obj': page_obj,
        'status': status,
        'search': search,
        'flagged': flagged
    })


@login_required
def booking_detail(request, pk):
    """View booking details."""
    booking = get_object_or_404(Booking, pk=pk)
    
    # Sales agents can only view their own bookings
    if request.user.is_sales_agent() and not request.user.is_admin():
        if booking.created_by != request.user:
            messages.error(request, 'You do not have permission to view this booking.')
            return redirect('bookings:list')
    
    return render(request, 'bookings/detail.html', {'booking': booking})


@login_required
@manager_required
def booking_validate(request, pk):
    """Validate (approve/reject) a booking."""
    booking = get_object_or_404(Booking, pk=pk)
    
    if booking.status != 'pending':
        messages.warning(request, 'This booking has already been validated.')
        return redirect('bookings:detail', pk=pk)
    
    if request.method == 'POST':
        form = BookingValidationForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            notes = form.cleaned_data['validation_notes']
            
            if action == 'approve':
                booking.approve(request.user, notes)
                create_audit_log(
                    'Booking',
                    booking.id,
                    'approve',
                    request.user,
                    {'status': 'approved'},
                    notes=notes,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f'Booking #{booking.booking_number} approved successfully.')
            else:
                booking.reject(request.user, notes)
                create_audit_log(
                    'Booking',
                    booking.id,
                    'reject',
                    request.user,
                    {'status': 'rejected'},
                    notes=notes,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f'Booking #{booking.booking_number} rejected.')
            
            return redirect('bookings:detail', pk=pk)
    else:
        form = BookingValidationForm()
    
    return render(request, 'bookings/validate.html', {
        'booking': booking,
        'form': form
    })


@login_required
@manager_required
def pending_validations(request):
    """List all pending validations."""
    bookings = Booking.objects.filter(status='pending').select_related(
        'package', 'created_by'
    ).order_by('created_at')
    
    # Filter by flags
    flagged = request.GET.get('flagged')
    if flagged == 'true':
        bookings = bookings.filter(
            Q(price_mismatch_flag=True) |
            Q(excess_discount_flag=True) |
            Q(duplicate_booking_flag=True)
        )
    
    paginator = Paginator(bookings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'bookings/pending.html', {
        'page_obj': page_obj,
        'flagged': flagged
    })

