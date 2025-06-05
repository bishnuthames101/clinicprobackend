from rest_framework import serializers
from .models import Patient, Service, Bill, BillItem, Service, MedicalRecord, MedicalReport
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'username': self.user.username,
            'role': self.user.role,
        })
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'age', 'gender', 'phone', 'email',
            'address', 'medical_history', 'last_visit'
        ]
        read_only_fields = ['last_visit']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'description', 'category', 'is_active']

class BillItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = BillItem
        fields = ['id', 'service', 'service_name', 'quantity', 'price', 'total']

class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True)
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    
    class Meta:
        model = Bill
        fields = [
            'id', 'bill_number', 'date', 'patient', 'patient_name',
            'discount_type', 'discount_value',
            'discount_amount', 'grand_total', 'status', 'items', 'notes'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        bill = Bill.objects.create(**validated_data)
        
        for item_data in items_data:
            BillItem.objects.create(bill=bill, **item_data)
        
        return bill

class CreateBillRequestSerializer(serializers.Serializer):
    patientId = serializers.IntegerField()
    items = serializers.ListField(
        child=serializers.DictField()
    )
    discountType = serializers.ChoiceField(choices=['percentage', 'amount'])
    discountValue = serializers.DecimalField(max_digits=10, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id', 'date', 'doctor', 'diagnosis', 'treatment', 'notes']

class MedicalReportSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalReport
        fields = ['id', 'title', 'date', 'type', 'file_url', 'fileUrl', 'uploadedBy']
        read_only_fields = ['file_url']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.file.url)
        return obj.fileUrl