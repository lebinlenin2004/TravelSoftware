"""
ASGI config for travel_sales project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_sales.settings')

application = get_asgi_application()

