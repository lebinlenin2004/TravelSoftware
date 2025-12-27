from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.http import JsonResponse
from .models import Package
from .forms import PackageForm
from accounts.decorators import admin_required


@login_required
def package_list(request):
    """List all packages."""
    packages = Package.objects.all()
    
    # Filter by active status
    is_active = request.GET.get('is_active')
    if is_active is not None:
        packages = packages.filter(is_active=is_active == 'true')
    
    # Search
    search = request.GET.get('search')
    if search:
        packages = packages.filter(
            models.Q(name__icontains=search) |
            models.Q(destination__icontains=search)
        )
    
    paginator = Paginator(packages, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'packages/list.html', {
        'page_obj': page_obj,
        'is_active': is_active,
        'search': search
    })


@login_required
@admin_required
def package_create(request):
    """Create a new package."""
    if request.method == 'POST':
        form = PackageForm(request.POST)
        if form.is_valid():
            package = form.save(commit=False)
            package.created_by = request.user
            package.save()
            messages.success(request, f'Package "{package.name}" created successfully.')
            return redirect('packages:list')
    else:
        form = PackageForm()
    
    return render(request, 'packages/form.html', {'form': form, 'title': 'Create Package'})


@login_required
@admin_required
def package_edit(request, pk):
    """Edit an existing package."""
    package = get_object_or_404(Package, pk=pk)
    
    if request.method == 'POST':
        form = PackageForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, f'Package "{package.name}" updated successfully.')
            return redirect('packages:list')
    else:
        form = PackageForm(instance=package)
    
    return render(request, 'packages/form.html', {
        'form': form, 
        'package': package,
        'title': 'Edit Package'
    })


@login_required
@admin_required
def package_detail(request, pk):
    """View package details."""
    package = get_object_or_404(Package, pk=pk)
    return render(request, 'packages/detail.html', {'package': package})


@login_required
def package_api(request, pk):
    """API endpoint to get package data for booking form."""
    package = get_object_or_404(Package, pk=pk)
    return JsonResponse({
        'current_price': str(package.get_current_price()),
        'base_price': str(package.base_price),
        'seasonal_price': str(package.seasonal_price) if package.seasonal_price else None,
        'tax_percentage': str(package.tax_percentage),
        'max_discount_percentage': str(package.max_discount_percentage),
    })
