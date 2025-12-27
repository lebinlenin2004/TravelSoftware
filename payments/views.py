from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from .models import Payment, Invoice
from .forms import PaymentForm
from bookings.models import Booking, AuditLog
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os


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
def payment_list(request):
    """List all payments."""
    payments = Payment.objects.select_related('booking', 'created_by').all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        payments = payments.filter(payment_status=status)
    
    # Search
    search = request.GET.get('search')
    if search:
        payments = payments.filter(
            Q(booking__booking_number__icontains=search) |
            Q(transaction_id__icontains=search) |
            Q(booking__customer_name__icontains=search)
        )
    
    from django.core.paginator import Paginator
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'payments/list.html', {
        'page_obj': page_obj,
        'status': status,
        'search': search
    })


@login_required
def payment_create(request, booking_id):
    """Create payment for a booking."""
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Check if payment already exists
    if hasattr(booking, 'payment'):
        messages.info(request, 'Payment already exists for this booking.')
        return redirect('payments:detail', pk=booking.payment.pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.total_amount = booking.total_amount
            payment.created_by = request.user
            
            if payment.payment_date is None:
                payment.payment_date = timezone.now()
            
            payment.save()
            payment.update_status()
            
            # Create audit log
            create_audit_log(
                'Payment',
                payment.id,
                'create',
                request.user,
                {'booking_id': booking.id, 'amount_paid': str(payment.amount_paid)},
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Payment recorded successfully.')
            return redirect('payments:detail', pk=payment.pk)
    else:
        form = PaymentForm()
    
    return render(request, 'payments/form.html', {
        'form': form,
        'booking': booking,
        'title': 'Record Payment'
    })


@login_required
def payment_update(request, pk):
    """Update payment."""
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save()
            payment.update_status()
            
            # Create audit log
            create_audit_log(
                'Payment',
                payment.id,
                'update',
                request.user,
                {'amount_paid': str(payment.amount_paid)},
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Payment updated successfully.')
            return redirect('payments:detail', pk=payment.pk)
    else:
        form = PaymentForm(instance=payment)
    
    return render(request, 'payments/form.html', {
        'form': form,
        'payment': payment,
        'title': 'Update Payment'
    })


@login_required
def payment_detail(request, pk):
    """View payment details."""
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'payments/detail.html', {'payment': payment})


@login_required
def generate_invoice(request, booking_id):
    """Generate invoice PDF for a booking."""
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Check if invoice already exists
    if hasattr(booking, 'invoice'):
        invoice = booking.invoice
        if invoice.pdf_file:
            messages.info(request, 'Invoice already generated.')
            return redirect('payments:view_invoice', pk=invoice.pk)
    
    # Create invoice
    invoice_number = f"INV{timezone.now().strftime('%Y%m%d')}{booking.id:06d}"
    invoice = Invoice.objects.create(
        invoice_number=invoice_number,
        booking=booking
    )
    
    # Generate PDF to buffer first
    from io import BytesIO
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"<b>INVOICE #{invoice_number}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Invoice details
    invoice_data = [
        ['Invoice Date:', invoice.invoice_date.strftime('%Y-%m-%d')],
        ['Booking Number:', booking.booking_number],
        ['Travel Date:', booking.travel_date.strftime('%Y-%m-%d')],
    ]
    
    invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Customer details
    customer_title = Paragraph("<b>Customer Details</b>", styles['Heading2'])
    elements.append(customer_title)
    
    customer_data = [
        ['Name:', booking.customer_name],
        ['Email:', booking.customer_email],
        ['Phone:', booking.customer_phone],
        ['Address:', booking.customer_address or 'N/A'],
    ]
    
    customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Package details
    package_title = Paragraph("<b>Package Details</b>", styles['Heading2'])
    elements.append(package_title)
    
    package_data = [
        ['Package:', booking.package.name],
        ['Destination:', booking.package.destination],
        ['Duration:', f"{booking.package.duration_days} days"],
        ['Travelers:', str(booking.number_of_travelers)],
    ]
    
    package_table = Table(package_data, colWidths=[2*inch, 4*inch])
    package_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(package_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Pricing details
    pricing_title = Paragraph("<b>Pricing Details</b>", styles['Heading2'])
    elements.append(pricing_title)
    
    pricing_data = [
        ['Description', 'Amount'],
        ['Package Price', f"₹{booking.package_price:.2f}"],
        ['Discount', f"-₹{booking.discount_amount:.2f}"],
        ['Subtotal', f"₹{booking.subtotal:.2f}"],
        [f'GST ({booking.package.tax_percentage}%)', f"₹{booking.tax_amount:.2f}"],
        ['<b>TOTAL</b>', f"<b>₹{booking.total_amount:.2f}</b>"],
    ]
    
    pricing_table = Table(pricing_data, colWidths=[4*inch, 2*inch])
    pricing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(pricing_table)
    
    # Build PDF
    doc.build(elements)
    
    # Save PDF to invoice
    from django.core.files.base import ContentFile
    buffer.seek(0)
    invoice.pdf_file.save(f'invoice_{invoice_number}.pdf', ContentFile(buffer.getvalue()))
    invoice.save()
    
    # Create response for download
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_number}.pdf"'
    
    # Create audit log
    create_audit_log(
        'Invoice',
        invoice.id,
        'create',
        request.user,
        {'invoice_number': invoice_number},
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, 'Invoice generated successfully.')
    return response


@login_required
def view_invoice(request, pk):
    """View invoice PDF."""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if invoice.pdf_file:
        from django.http import FileResponse
        return FileResponse(open(invoice.pdf_file.path, 'rb'), content_type='application/pdf')
    else:
        messages.error(request, 'Invoice PDF not found.')
        return redirect('bookings:detail', pk=invoice.booking.pk)

