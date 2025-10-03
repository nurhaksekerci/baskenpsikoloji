"""
NETGSM SMS API Entegrasyonu
Öğrenci giriş-çıkış bilgilendirme sistemi
"""

import requests
import logging
from datetime import datetime
from django.conf import settings
import urllib.parse

logger = logging.getLogger(__name__)

class NetGSMService:
    """NETGSM API servisi"""
    
    def __init__(self):
        self.api_url = "https://api.netgsm.com.tr/sms/send/get"
        self.username = settings.NETGSM_USERNAME
        self.password = settings.NETGSM_PASSWORD
        self.header = settings.NETGSM_HEADER
        
    def send_sms(self, phone_number, message):
        """
        SMS gönderme fonksiyonu
        
        Args:
            phone_number (str): Telefon numarası (5055551234 formatında)
            message (str): Gönderilecek mesaj
            
        Returns:
            dict: Gönderim sonucu
        """
        try:
            # Telefon numarasını temizle
            clean_phone = self._clean_phone_number(phone_number)
            
            if not self._validate_phone_number(clean_phone):
                return {
                    'success': False,
                    'error': 'Geçersiz telefon numarası formatı'
                }
            
            # API parametreleri
            params = {
                'usercode': self.username,
                'password': self.password,
                'gsmno': clean_phone,
                'message': message,
                'msgheader': self.header,
                'filter': '0',  # Türkçe karakter filtresi kapalı
                'startdate': '',
                'stopdate': ''
            }
            
            # API isteği gönder
            response = requests.get(self.api_url, params=params, timeout=30)
            
            # Yanıtı kontrol et
            result = self._parse_response(response.text)
            
            if result['success']:
                logger.info(f"SMS başarıyla gönderildi: {clean_phone}")
            else:
                logger.error(f"SMS gönderim hatası: {result['error']}")
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"NETGSM API bağlantı hatası: {str(e)}")
            return {
                'success': False,
                'error': f'API bağlantı hatası: {str(e)}'
            }
        except Exception as e:
            logger.error(f"SMS gönderim genel hatası: {str(e)}")
            return {
                'success': False,
                'error': f'Beklenmeyen hata: {str(e)}'
            }
    
    def _clean_phone_number(self, phone_number):
        """Telefon numarasını temizle ve formatla"""
        if not phone_number:
            return ""
        
        # Tüm özel karakterleri kaldır
        clean = ''.join(filter(str.isdigit, phone_number))
        
        # Türkiye ülke kodu kontrolü
        if clean.startswith('90'):
            clean = clean[2:]  # 90 ülke kodunu kaldır
        elif clean.startswith('+90'):
            clean = clean[3:]  # +90 ülke kodunu kaldır
        
        # 0 ile başlıyorsa kaldır
        if clean.startswith('0'):
            clean = clean[1:]
        
        return clean
    
    def _validate_phone_number(self, phone_number):
        """Telefon numarası formatını kontrol et"""
        if not phone_number:
            return False
        
        # Türk cep telefonu formatı: 5XXXXXXXXX (10 hane)
        if len(phone_number) != 10:
            return False
        
        # 5 ile başlamalı
        if not phone_number.startswith('5'):
            return False
        
        return True
    
    def _parse_response(self, response_text):
        """NETGSM API yanıtını parse et"""
        response_text = response_text.strip()
        
        # Başarılı gönderim - İşlem ID döner
        if response_text.isdigit() and len(response_text) > 5:
            return {
                'success': True,
                'message_id': response_text,
                'error': None
            }
        
        # Hata kodları
        error_codes = {
            '20': 'Mesaj metninde ki problemden dolayı gönderilemediği gönderim sayısı',
            '30': 'Geçersiz kullanıcı adı, şifre veya kullanıcınızın API erişim izninin olmadığı',
            '40': 'Mesaj başlığınızın (gönderici adınızın) sistemde tanımlı olmadığı',
            '50': 'Abone olmadığınız hesabınıza ait şifrenizin hatalı olduğu',
            '51': 'Bakiye yetersiz',
            '60': 'Gönderim sırasında alınan numara hatasının miktarı',
            '70': 'Hatalı sorgulama. Gönderdiğiniz parametrelerden birisi hatalı veya zorunlu alanlardan birinin eksik olduğu',
            '80': 'Gönderim sırasında sistemde meydana gelen hatayı',
            '85': 'Gönderilecek mesajda harf, rakam ve Türkçe karakterler dışında karakter bulunduğu'
        }
        
        error_message = error_codes.get(response_text, f'Bilinmeyen hata kodu: {response_text}')
        
        return {
            'success': False,
            'message_id': None,
            'error': error_message
        }
    
    def get_balance(self):
        """Bakiye sorgulama"""
        try:
            balance_url = "https://api.netgsm.com.tr/balance/list/get"
            
            params = {
                'usercode': self.username,
                'password': self.password
            }
            
            response = requests.get(balance_url, params=params, timeout=30)
            
            if response.text.replace('.', '').isdigit():
                return {
                    'success': True,
                    'balance': float(response.text),
                    'currency': 'TL'
                }
            else:
                return {
                    'success': False,
                    'error': f'Bakiye sorgulanamadı: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Bakiye sorgulama hatası: {str(e)}'
            }


class AttendanceSMSService:
    """Yoklama SMS bildirimi servisi"""
    
    def __init__(self):
        self.netgsm = NetGSMService()
    
    def send_attendance_notification(self, student, attendance):
        """
        Öğrenci giriş/çıkış bildirimi gönder
        
        Args:
            student: Student model instance
            attendance: Attendance model instance
        """
        try:
            # SMS metnini oluştur
            message = self._create_message(student, attendance)
            
            # Veli telefon numarasını al
            parent_phone = student.parent_phone_number
            
            if not parent_phone:
                logger.warning(f"Öğrenci {student.full_name} için veli telefon numarası bulunamadı")
                return {
                    'success': False,
                    'error': 'Veli telefon numarası bulunamadı'
                }
            
            # SMS gönder
            result = self.netgsm.send_sms(parent_phone, message)
            
            # Log kaydet
            if result['success']:
                logger.info(f"Yoklama SMS'i gönderildi: {student.full_name} -> {parent_phone}")
            else:
                logger.error(f"Yoklama SMS gönderim hatası: {student.full_name} -> {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Attendance SMS service hatası: {str(e)}")
            return {
                'success': False,
                'error': f'SMS servisi hatası: {str(e)}'
            }
    
    def _create_message(self, student, attendance):
        """SMS mesaj metnini oluştur"""
        
        # Türkçe tarih formatı
        date_str = attendance.timestamp.strftime('%d.%m.%Y')
        time_str = attendance.timestamp.strftime('%H:%M')
        
        # Giriş/çıkış durumu
        action = "GİRİŞ" if attendance.entry_type == 'entry' else "ÇIKIŞ"
        
        # Mesaj şablonu
        message = f"""Başkent Psikoloji
{student.first_name} {student.last_name}
{action}: {date_str} {time_str}
{student.school.name}
{student.classroom.name}"""
        
        return message
    
    def send_test_sms(self, phone_number):
        """Test SMS gönder"""
        test_message = f"""Başkent Psikoloji Test SMS
Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}
SMS sistemi aktif!"""
        
        return self.netgsm.send_sms(phone_number, test_message)


# Global service instance
sms_service = AttendanceSMSService()