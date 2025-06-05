import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'patientrecords.settings')
django.setup()

from kistrecords.models import CustomUser

# Create receptionist user
receptionist = CustomUser.objects.create_user(
    username='receptionist',
    password='receptionist123',
    role='receptionist',
    email='receptionist@example.com',
    phone='1234567890'
)

print("Receptionist user created successfully!") 