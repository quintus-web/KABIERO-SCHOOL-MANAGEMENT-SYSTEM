"""
WSGI config for sms_core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import logging

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_core.settings')

application = get_wsgi_application()

if os.environ.get('RENDER'):
    try:
        from finance.models import Student, StaffProfile
        from django.contrib.auth.models import User
        admin_username = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'sms_pass2026')
        user, _ = User.objects.get_or_create(
            username=admin_username,
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.set_password(admin_password)
        user.save()
        logger.info("Render startup: admin user ensured")
        if Student.objects.count() == 0:
            logger.info("Render startup: DB empty, running seed_data...")
            call_command('seed_data', verbosity=1)
            logger.info(f"Render startup: seed complete. Student count = {Student.objects.count()}")
    except Exception as exc:
        logger.error(f"Render startup seeding failed: {exc}")
