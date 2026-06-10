"""
WSGI config for sms_core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_core.settings')

application = get_wsgi_application()

if os.environ.get('RENDER'):
    try:
        from finance.models import Student
        if Student.objects.count() == 0:
            call_command('seed_data', verbosity=0)
    except Exception:
        pass
