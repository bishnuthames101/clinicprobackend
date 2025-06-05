from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Patient, Service, Bill, BillItem, MedicalRecord, MedicalReport

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('role', 'phone')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'role', 'phone')

class MedicalRecordInline(admin.TabularInline):
    model = MedicalRecord
    extra = 0
    readonly_fields = ('date',)

class MedicalReportInline(admin.TabularInline):
    model = MedicalReport
    extra = 0
    readonly_fields = ('date', 'file_preview')
    fields = ('title', 'date', 'type', 'file', 'file_preview', 'uploadedBy')
    
    def file_preview(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            if obj.type == 'image':
                return format_html('<a href="{}" target="_blank"><img src="{}" width="100" /></a>', obj.file.url, obj.file.url)
            else:
                return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)
        return "No file"
    file_preview.short_description = 'Preview'

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender', 'phone', 'email', 'last_visit')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('gender', 'created_at')
    readonly_fields = ('last_visit', 'created_at', 'updated_at')
    inlines = [MedicalRecordInline, MedicalReportInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'age', 'gender', 'phone', 'email')
        }),
        ('Additional Information', {
            'fields': ('address', 'medical_history')
        }),
        ('System Fields', {
            'fields': ('last_visit', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)

class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'patient', 'grand_total', 'status', 'date', 'created_by')
    list_filter = ('status', 'date')
    search_fields = ('bill_number', 'patient__name')
    readonly_fields = ('bill_number', 'date', 'grand_total')
    inlines = [BillItemInline]
    fieldsets = (
        ('Bill Information', {
            'fields': ('bill_number', 'date', 'patient', 'status')
        }),
        ('Financial Details', {
            'fields': ('discount_type', 'discount_value', 'discount_amount', 'grand_total')
        }),
        ('Additional Information', {
            'fields': ('created_by', 'notes')
        })
    )

@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ('bill', 'service', 'quantity', 'price', 'total')
    search_fields = ('bill__bill_number', 'service__name')
    list_filter = ('bill__status',)
    readonly_fields = ('total',)

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'diagnosis', 'doctor', 'date')
    list_filter = ('date', 'doctor')
    search_fields = ('patient__name', 'diagnosis', 'doctor')
    readonly_fields = ('date',)
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'date', 'doctor')
        }),
        ('Medical Details', {
            'fields': ('diagnosis', 'treatment', 'notes')
        })
    )

@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('patient', 'title', 'type', 'date', 'uploadedBy', 'file_preview')
    list_filter = ('type', 'date', 'uploadedBy')
    search_fields = ('patient__name', 'title')
    readonly_fields = ('date', 'file_preview')
    
    def file_preview(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            if obj.type == 'image':
                return format_html('<a href="{}" target="_blank"><img src="{}" width="100" /></a>', obj.file.url, obj.file.url)
            else:
                return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)
        return "No file"
    file_preview.short_description = 'Preview'
