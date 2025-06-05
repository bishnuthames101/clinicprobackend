from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('receptionist', 'Receptionist'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return self.username

class Patient(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField()
    medical_history = models.TextField(null=True, blank=True)
    last_visit = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class Service(models.Model):
    CATEGORY_CHOICES = (
        ('Consultation', 'Consultation'),
        ('Laboratory', 'Laboratory'),
        ('Radiology', 'Radiology'),
        ('Cardiology', 'Cardiology'),
        ('Therapy', 'Therapy'),
        ('Vaccination', 'Vaccination'),
        ('Dental', 'Dental'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Bill(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('amount', 'Amount'),
    ]
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
    ]
    
    bill_number = models.CharField(max_length=20, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, blank=True, null=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.bill_number
    
    def save(self, *args, **kwargs):
        if not self.bill_number:
            last_bill = Bill.objects.order_by('-id').first()
            last_id = last_bill.id if last_bill else 0
            self.bill_number = f"BILL-{last_id + 1:03d}"
        super().save(*args, **kwargs)

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.service.name} x {self.quantity}"

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    date = models.DateTimeField(auto_now_add=True)
    doctor = models.CharField(max_length=100)
    diagnosis = models.CharField(max_length=200)
    treatment = models.TextField()
    notes = models.TextField(null=True, blank=True)
    
    def delete(self, *args, **kwargs):
        # Custom delete logic can be added here if needed in the future
        # For example, logging the deletion or other cleanup tasks
        super().delete(*args, **kwargs)
        
    def __str__(self):
        return f"{self.diagnosis} - {self.patient.name} ({self.date.strftime('%Y-%m-%d')})"

class MedicalReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_reports')
    title = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50, choices=[('image', 'Image'), ('document', 'Document')])
    file = models.FileField(upload_to='medical_reports/', null=True, blank=True)
    fileUrl = models.URLField(blank=True, null=True)  # Keep for compatibility
    uploadedBy = models.CharField(max_length=100)
    
    def delete(self, *args, **kwargs):
        # Delete the file from the filesystem when the model instance is deleted
        if self.file:
            # Get the storage backend
            storage = self.file.storage
            # Get the file name
            file_name = self.file.name
            # Delete the file if it exists
            if storage.exists(file_name):
                storage.delete(file_name)
        # Call the parent delete method
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.patient.name}"