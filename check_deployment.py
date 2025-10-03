#!/usr/bin/env python
"""
PythonAnywhere deployment checker
Bu script deployment sorunlarını tespit eder ve çözüm önerir.
"""

import os
import sys
import django

def check_environment():
    """Environment ayarlarını kontrol et"""
    print("🔍 Environment kontrol ediliyor...")
    
    if not os.path.exists('.env'):
        print("❌ .env dosyası bulunamadı!")
        print("💡 .env.production'ı .env olarak kopyalayın")
        return False
    
    print("✅ .env dosyası mevcut")
    return True

def check_python_path():
    """Python path kontrol"""
    print("🔍 Python path kontrol ediliyor...")
    current_path = os.getcwd()
    print(f"📂 Mevcut dizin: {current_path}")
    
    if 'baskentpsikoloji' not in current_path:
        print("❌ Proje dizininde değilsiniz!")
        return False
    
    print("✅ Proje dizini doğru")
    return True

def check_django_setup():
    """Django setup kontrol"""
    print("🔍 Django setup kontrol ediliyor...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        print("✅ Django setup başarılı")
        return True
    except Exception as e:
        print(f"❌ Django setup hatası: {e}")
        return False

def check_database():
    """Database kontrol"""
    print("🔍 Database kontrol ediliyor...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database bağlantısı başarılı")
        
        # Tablolar kontrol
        from school.models import Student, Attendance
        student_count = Student.objects.count()
        attendance_count = Attendance.objects.count()
        print(f"📊 Öğrenci sayısı: {student_count}")
        print(f"📊 Yoklama kayıt sayısı: {attendance_count}")
        
        return True
    except Exception as e:
        print(f"❌ Database hatası: {e}")
        print("💡 python manage.py migrate çalıştırın")
        return False

def check_static_files():
    """Static files kontrol"""
    print("🔍 Static files kontrol ediliyor...")
    
    from django.conf import settings
    static_root = settings.STATIC_ROOT
    
    if not os.path.exists(static_root):
        print(f"❌ Static root bulunamadı: {static_root}")
        print("💡 python manage.py collectstatic çalıştırın")
        return False
    
    print(f"✅ Static root mevcut: {static_root}")
    return True

def check_urls():
    """URL patterns kontrol"""
    print("🔍 URL patterns kontrol ediliyor...")
    
    try:
        from django.urls import reverse
        
        urls_to_check = [
            'teacher_qr',
            'student_checkin', 
            'attendance_toggle',
            'student_status'
        ]
        
        for url_name in urls_to_check:
            try:
                if url_name == 'student_status':
                    reverse(url_name, args=['12345678901'])
                else:
                    reverse(url_name)
                print(f"✅ URL '{url_name}' OK")
            except Exception as e:
                print(f"❌ URL '{url_name}' hatası: {e}")
                
        return True
    except Exception as e:
        print(f"❌ URL kontrol hatası: {e}")
        return False

def main():
    """Ana kontrol fonksiyonu"""
    print("🚀 PythonAnywhere Deployment Checker")
    print("=" * 40)
    
    checks = [
        check_python_path,
        check_environment,
        check_django_setup,
        check_database,
        check_static_files,
        check_urls
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Kontrol hatası: {e}")
            results.append(False)
            print()
    
    print("📋 SONUÇ")
    print("=" * 40)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 Tüm kontroller başarılı!")
        print("🌐 Site hazır: https://baskentpsikoloji.pythonanywhere.com")
    else:
        print(f"⚠️  {total - passed} sorun tespit edildi")
        print("💡 Yukarıdaki önerileri takip edin")

if __name__ == '__main__':
    main()