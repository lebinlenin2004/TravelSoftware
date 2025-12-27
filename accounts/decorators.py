from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorator to require admin role."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('analytics:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def manager_required(view_func):
    """Decorator to require manager or admin role."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_admin() or request.user.is_manager()):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('analytics:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def sales_agent_required(view_func):
    """Decorator to require sales agent, manager, or admin role."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_admin() or request.user.is_sales_agent() or request.user.is_manager()):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('analytics:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def accountant_required(view_func):
    """Decorator to require accountant or admin role."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_admin() or request.user.is_accountant()):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('analytics:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

