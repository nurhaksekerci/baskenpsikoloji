from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from .models import Student, Attendance
from .sms_service import sms_service
import json
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    return render(request, 'school/index.html')

def login(request):
    return render(request, 'auth/login.html')

def qr_generator(request):
    """QR kod oluşturucu sayfası - Öğretmenler için"""
    return render(request, 'auth/qr.html')

def student_checkin(request):
    """Öğrenci giriş-çıkış sayfası - QR kod okutunca açılan sayfa"""
    return render(request, 'auth/student_checkin.html')

@csrf_exempt
@require_http_methods(["POST"])
def attendance_toggle(request):
    """QR kod ile öğrenci giriş/çıkış toggle endpoint'i"""
    try:
        # POST verilerini al
        data = json.loads(request.body) if request.body else {}
        id_number = data.get('id_number')
        
        if not id_number:
            return JsonResponse({
                'status': 'error',
                'message': 'TC kimlik numarası gerekli'
            }, status=400)
        
        # TC kimlik numarası formatını kontrol et
        if not id_number.isdigit() or len(id_number) != 11:
            return JsonResponse({
                'status': 'error',
                'message': 'Geçersiz TC kimlik numarası formatı'
            }, status=400)
        
        # Öğrenciyi TC kimlik numarasından bul
        try:
            student = Student.objects.get(id_number=id_number, is_active=True)
        except Student.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Bu TC kimlik numarasına ait aktif öğrenci bulunamadı',
                'id_number': id_number
            }, status=404)
        
        # Giriş/çıkış toggle işlemi
        attendance = Attendance.toggle_attendance(student)
        
        # SMS bildirimi gönder (eğer aktifse)
        sms_result = None
        if getattr(settings, 'SMS_ENABLED', True):
            try:
                sms_result = sms_service.send_attendance_notification(student, attendance)
                if sms_result['success']:
                    logger.info(f"SMS başarıyla gönderildi: {student.full_name}")
                else:
                    logger.warning(f"SMS gönderim hatası: {sms_result['error']}")
            except Exception as e:
                logger.error(f"SMS gönderim exception: {str(e)}")
                sms_result = {'success': False, 'error': str(e)}
        
        # Son durumu kontrol et
        last_entry = Attendance.get_last_entry(student)
        current_status = 'içeride' if last_entry and last_entry.entry_type == 'entry' else 'dışarıda'
        
        # Başarılı yanıt
        response_data = {
            'status': 'success',
            'message': f'İşlem başarılı! {attendance.get_entry_type_display()} kaydedildi.',
            'student': {
                'id_number': student.id_number,
                'full_name': student.full_name,
                'school': student.school.name,
                'classroom': str(student.classroom),
            },
            'attendance': {
                'entry_type': attendance.entry_type,
                'entry_type_display': attendance.get_entry_type_display(),
                'timestamp': attendance.timestamp.isoformat(),
                'date': attendance.date.isoformat(),
                'current_status': current_status
            },
            'sms_notification': {
                'sent': sms_result['success'] if sms_result else False,
                'error': sms_result['error'] if sms_result and not sms_result['success'] else None
            },
            'processed_at': timezone.now().isoformat()
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Geçersiz JSON formatı'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Sunucu hatası: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def student_status(request, id_number):
    """Öğrencinin mevcut durumunu getir"""
    try:
        # TC kimlik numarası formatını kontrol et
        if not id_number.isdigit() or len(id_number) != 11:
            return JsonResponse({
                'status': 'error',
                'message': 'Geçersiz TC kimlik numarası formatı'
            }, status=400)
        
        # Öğrenciyi bul
        try:
            student = Student.objects.get(id_number=id_number, is_active=True)
        except Student.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Öğrenci bulunamadı',
                'id_number': id_number
            }, status=404)
        
        # Son giriş/çıkış kaydını bul
        last_entry = Attendance.get_last_entry(student)
        
        if last_entry:
            current_status = 'içeride' if last_entry.entry_type == 'entry' else 'dışarıda'
            last_action = last_entry.get_entry_type_display()
            last_time = last_entry.timestamp.isoformat()
        else:
            current_status = 'dışarıda'
            last_action = 'Henüz giriş yapılmamış'
            last_time = None
        
        # Bugünün giriş/çıkış geçmişi
        today = timezone.now().date()
        today_entries = Attendance.objects.filter(
            student=student, 
            date=today
        ).order_by('-timestamp')
        
        entries_today = [
            {
                'entry_type': entry.entry_type,
                'entry_type_display': entry.get_entry_type_display(),
                'timestamp': entry.timestamp.isoformat(),
            }
            for entry in today_entries
        ]
        
        response_data = {
            'status': 'success',
            'student': {
                'id_number': student.id_number,
                'full_name': student.full_name,
                'school': student.school.name,
                'classroom': str(student.classroom),
            },
            'current_status': current_status,
            'last_action': last_action,
            'last_time': last_time,
            'entries_today': entries_today,
            'entries_count_today': len(entries_today)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Sunucu hatası: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def test_sms(request):
    """SMS testi endpoint'i"""
    try:
        data = json.loads(request.body) if request.body else {}
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return JsonResponse({
                'status': 'error',
                'message': 'Telefon numarası gerekli'
            }, status=400)
        
        # Test SMS gönder
        result = sms_service.send_test_sms(phone_number)
        
        return JsonResponse({
            'status': 'success' if result['success'] else 'error',
            'message': 'Test SMS gönderildi' if result['success'] else result['error'],
            'details': result
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'SMS test hatası: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def sms_balance(request):
    """SMS bakiye sorgulama"""
    try:
        result = sms_service.netgsm.get_balance()
        
        return JsonResponse({
            'status': 'success' if result['success'] else 'error',
            'balance': result.get('balance', 0),
            'currency': result.get('currency', 'TL'),
            'message': result.get('error', 'Bakiye başarıyla sorgulandı')
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Bakiye sorgulama hatası: {str(e)}'
        }, status=500)

def logout(request):
    pass

def sms_test_page(request):
    """SMS test sayfası"""
    context = {
        'netgsm_username': getattr(settings, 'NETGSM_USERNAME', 'Tanımlı değil'),
        'netgsm_header': getattr(settings, 'NETGSM_HEADER', 'Tanımlı değil'),
    }
    return render(request, 'auth/sms_test.html', context)
