from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Bill, Patient, BillItem, Service, MedicalRecord, MedicalReport
from .serializers import (
    BillSerializer, PatientSerializer, 
    CreateBillRequestSerializer, ServiceSerializer,
    MedicalRecordSerializer, MedicalReportSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
import logging

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

from rest_framework.decorators import permission_classes
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'phone': user.phone,
    })
    
class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all().order_by('-date')
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patientId')
        date = self.request.query_params.get('date')
        
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if date:
            # Filter bills by date (YYYY-MM-DD format)
            queryset = queryset.filter(date__date=date)
            
        return queryset

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        bill = self.get_object()
        # In production, generate PDF here
        serializer = self.get_serializer(bill)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        date = request.query_params.get('date')
        if not date:
            return Response(
                {"error": "Date parameter is required (YYYY-MM-DD format)"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Filter bills by date
        bills = self.get_queryset().filter(date__date=date)
        
        # Calculate summary data
        total_amount = sum(bill.grand_total for bill in bills)
        bill_count = bills.count()
        average_amount = total_amount / bill_count if bill_count > 0 else 0
        highest_amount = max([bill.grand_total for bill in bills]) if bill_count > 0 else 0
        
        # Serialize the bills
        serializer = self.get_serializer(bills, many=True)
        
        return Response({
            'date': date,
            'bills': serializer.data,
            'summary': {
                'total_amount': total_amount,
                'bill_count': bill_count,
                'average_amount': average_amount,
                'highest_amount': highest_amount
            }
        })



class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['name', 'phone', 'gender']
    
    def destroy(self, request, *args, **kwargs):
        try:
            # With CASCADE set on the foreign keys, this will delete all related records
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error deleting patient: {str(e)}")
            return Response(
                {"error": f"Failed to delete patient: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def add_medical_report(self, request, pk=None):
        patient = self.get_object()
        
        try:
            # Check if file is in the request
            if 'file' not in request.FILES:
                return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            uploaded_file = request.FILES['file']
            title = request.data.get('title', uploaded_file.name)
            report_type = request.data.get('type', 'document')
            if not report_type:
                # Determine type based on file extension
                if uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    report_type = 'image'
                else:
                    report_type = 'document'
                    
            uploaded_by = request.data.get('uploadedBy', request.user.username)
            
            # Create the medical report with the actual file
            report = MedicalReport.objects.create(
                patient=patient,
                title=title,
                type=report_type,
                file=uploaded_file,
                uploadedBy=uploaded_by
            )
            
            # Set the fileUrl to the file's URL for frontend compatibility
            report.fileUrl = request.build_absolute_uri(report.file.url)
            report.save()
        
            # Return updated patient data
            medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-date')
            bills = Bill.objects.filter(patient=patient).order_by('-date')
            reports = MedicalReport.objects.filter(patient=patient).order_by('-date')
        
            return Response({
                'patient': PatientSerializer(patient).data,
                'medicalRecords': MedicalRecordSerializer(medical_records, many=True).data,
                'billingHistory': BillSerializer(bills, many=True).data,
                'medicalReports': MedicalReportSerializer(reports, many=True).data,
            })
        
        except Exception as e:
            logger.error(f"Error adding medical report: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def add_medical_record(self, request, pk=None):
        patient = self.get_object()
        
        try:
            # Extract data from request
            diagnosis = request.data.get('diagnosis')
            treatment = request.data.get('treatment')
            notes = request.data.get('notes')
            doctor = request.data.get('doctor')
            
            if not diagnosis or not treatment or not doctor:
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the medical record
            record = MedicalRecord.objects.create(
                patient=patient,
                diagnosis=diagnosis,
                treatment=treatment,
                notes=notes,
                doctor=doctor
            )
            
            # Return updated patient data
            medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-date')
            bills = Bill.objects.filter(patient=patient).order_by('-date')
            reports = MedicalReport.objects.filter(patient=patient).order_by('-date')
            
            return Response({
                'patient': PatientSerializer(patient).data,
                'medicalRecords': MedicalRecordSerializer(medical_records, many=True).data,
                'billingHistory': BillSerializer(bills, many=True).data,
                'medicalReports': MedicalReportSerializer(reports, many=True).data,
            })
            
        except Exception as e:
            logger.error(f"Error adding medical record: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        logger.info(f"Received patient creation request: {request.data}")
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Patient created successfully: {response.data}")
            return response
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            raise

    @action(detail=True, methods=['get'])
    def billing_history(self, request, pk=None):
        patient = self.get_object()
        bills = Bill.objects.filter(patient=patient).order_by('-date')
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        patient = self.get_object()
        medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-date')
        bills = Bill.objects.filter(patient=patient).order_by('-date')
        reports = MedicalReport.objects.filter(patient=patient).order_by('-date')
        
        return Response({
            'patient': PatientSerializer(patient).data,
            'medicalRecords': MedicalRecordSerializer(medical_records, many=True).data,
            'billingHistory': BillSerializer(bills, many=True).data,
            'medicalReports': MedicalReportSerializer(reports, many=True).data,
        })
        
    @action(detail=True, methods=['delete'], url_path='delete-medical-report/(?P<report_id>[^/.]+)')
    def delete_medical_report(self, request, pk=None, report_id=None):
        patient = self.get_object()
        
        try:
            report = MedicalReport.objects.get(id=report_id, patient=patient)
            report.delete()
            
            # Return updated patient data
            medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-date')
            bills = Bill.objects.filter(patient=patient).order_by('-date')
            reports = MedicalReport.objects.filter(patient=patient).order_by('-date')
            
            return Response({
                'patient': PatientSerializer(patient).data,
                'medicalRecords': MedicalRecordSerializer(medical_records, many=True).data,
                'billingHistory': BillSerializer(bills, many=True).data,
                'medicalReports': MedicalReportSerializer(reports, many=True).data,
            })
            
        except MedicalReport.DoesNotExist:
            return Response({"error": "Medical report not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting medical report: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=True, methods=['delete'], url_path='delete-medical-record/(?P<record_id>[^/.]+)')
    def delete_medical_record(self, request, pk=None, record_id=None):
        patient = self.get_object()
        
        try:
            record = MedicalRecord.objects.get(id=record_id, patient=patient)
            record.delete()
            
            # Return updated patient data
            medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-date')
            bills = Bill.objects.filter(patient=patient).order_by('-date')
            reports = MedicalReport.objects.filter(patient=patient).order_by('-date')
            
            return Response({
                'patient': PatientSerializer(patient).data,
                'medicalRecords': MedicalRecordSerializer(medical_records, many=True).data,
                'billingHistory': BillSerializer(bills, many=True).data,
                'medicalReports': MedicalReportSerializer(reports, many=True).data,
            })
            
        except MedicalRecord.DoesNotExist:
            return Response({"error": "Medical record not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting medical record: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.filter(is_active=True).order_by('name')
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_data(request):
    logger.info("Dashboard API called")
    try:
        # Get today's date
        today = timezone.now().date()
        
        # Get bills from today
        logger.info(f"Getting bills for today: {today}")
        today_bills = Bill.objects.filter(date__date=today)
        logger.info(f"Found {today_bills.count()} bills for today")
        
        today_revenue = 0
        for bill in today_bills:
            try:
                logger.info(f"Processing bill {bill.id}, grand_total: {bill.grand_total}, type: {type(bill.grand_total)}")
                if isinstance(bill.grand_total, (int, float)):
                    today_revenue += bill.grand_total
                else:
                    today_revenue += float(bill.grand_total)
            except (ValueError, TypeError) as e:
                logger.error(f"Error processing bill {bill.id}: {str(e)}")
                # Skip bills with invalid grand_total
                pass
        
        # Get unique patients from today's bills
        today_patient_ids = set(today_bills.values_list('patient_id', flat=True))
        today_patient_count = len(today_patient_ids)
        
        # Get total counts
        total_patients = Patient.objects.count()
        total_bills = Bill.objects.count()
        
        # Calculate total revenue safely
        logger.info("Calculating total revenue")
        all_bills = Bill.objects.all()
        logger.info(f"Total bills in database: {all_bills.count()}")
        
        total_revenue = 0
        for bill in all_bills:
            try:
                if isinstance(bill.grand_total, (int, float)):
                    total_revenue += bill.grand_total
                else:
                    total_revenue += float(bill.grand_total)
            except (ValueError, TypeError) as e:
                logger.error(f"Error calculating total revenue for bill {bill.id}: {str(e)}")
                # Skip bills with invalid grand_total
                pass
        
        # Get recent bills (last 5)
        recent_bills = Bill.objects.order_by('-date')[:5]
        
        # Get recent patients (last 5)
        recent_patients = Patient.objects.order_by('-last_visit')[:5]
        
        # Get daily stats for the last 7 days
        daily_stats = []
        for i in range(7):
            date = today - timedelta(days=i)
            day_bills = Bill.objects.filter(date__date=date)
            day_patient_ids = set(day_bills.values_list('patient_id', flat=True))
            
            # Calculate daily revenue safely
            day_revenue = 0
            for bill in day_bills:
                try:
                    if isinstance(bill.grand_total, (int, float)):
                        day_revenue += bill.grand_total
                    else:
                        day_revenue += float(bill.grand_total)
                except (ValueError, TypeError):
                    # Skip bills with invalid grand_total
                    pass
            
            daily_stats.append({
                'date': date.isoformat(),
                'patients': len(day_patient_ids),
                'revenue': day_revenue
            })
        
        # Prepare response data
        data = {
            'totalPatients': total_patients,
            'totalBills': total_bills,
            'totalRevenue': total_revenue,
            'todayPatients': today_patient_count,
            'todayBills': today_bills.count(),
            'todayRevenue': today_revenue,
            'recentBills': BillSerializer(recent_bills, many=True).data,
            'recentPatients': PatientSerializer(recent_patients, many=True).data,
            'dailyStats': daily_stats
        }
        
        return Response(data)
    except Exception as e:
        logger.error(f"Error in dashboard API: {str(e)}")
        return Response(
            {"error": f"Failed to load dashboard data: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class CreateBillView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateBillRequestSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f"Received bill creation request: {request.data}")
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Bill validation error: {str(e)}")
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(
                {'error': str(e), 'details': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        patient_id = data['patientId']
        items_data = data['items']
        discount_type = data['discountType']
        discount_value = data['discountValue']
        
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Patient not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate bill totals
        subtotal = 0
        bill_items = []
        
        for item in items_data:
            try:
                service = Service.objects.get(id=item['serviceId'])
            except Service.DoesNotExist:
                return Response(
                    {'error': f'Service with ID {item["serviceId"]} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            quantity = item.get('quantity', 1)
            item_total = service.price * quantity
            subtotal += item_total
            
            bill_items.append({
                'service': service,
                'quantity': quantity,
                'price': service.price,
                'total': item_total
            })
        
        if discount_type == 'percentage':
            discount_amount = (subtotal * discount_value) / 100
        else:
            discount_amount = discount_value
        
        grand_total = subtotal - discount_amount
        
        # Create the bill
        bill = Bill.objects.create(
            patient=patient,
            discount_type=discount_type,
            discount_value=discount_value,
            discount_amount=discount_amount,
            grand_total=grand_total,
            created_by=request.user,
            notes=data.get('notes', '')
        )
        
        # Create bill items
        for item in bill_items:
            BillItem.objects.create(bill=bill, **item)
        
        return Response(
            BillSerializer(bill, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

