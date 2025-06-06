"""
WSGI config for patientrecords project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'patientrecords.settings')

application = get_wsgi_application()

from django.contrib.auth import get_user_model
from django.core.management import call_command

if os.environ.get("AUTO_CREATE_SUPERUSER", "False") == "True":
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        print("Creating default superuser...")
        User.objects.create_superuser("admin", "admin@example.com", "adminpassword")
    else:
        print("Superuser already exists.")
