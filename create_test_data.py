#!/usr/bin/env python
"""
PythonAnywhere için test verisi oluşturma scripti
Bu scripti PythonAnywhere console'da çalıştırın
"""

import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from school.models import School, Classroom, Student
from django.contrib.auth.models import User

def create_test_data():
    print("🏫 Test verisi oluşturuluyor...")
    
    # 1. Test okulu oluştur
    school, created = School.objects.get_or_create(
        name='Başkent Psikoloji Test Okulu',
        defaults={
            'address': 'Ankara, Türkiye',
            'phone_number': '+905551234567',
            'email': 'info@baskentpsikoloji.com'
        }
    )
    
    if created:
        print(f"✅ Okul oluşturuldu: {school.name}")
    else:
        print(f"ℹ️  Okul zaten mevcut: {school.name}")
    
    # 2. Test sınıfı oluştur
    classroom, created = Classroom.objects.get_or_create(
        school=school,
        name='A Sınıfı',
        defaults={'capacity': 30}
    )
    
    if created:
        print(f"✅ Sınıf oluşturuldu: {classroom}")
    else:
        print(f"ℹ️  Sınıf zaten mevcut: {classroom}")
    
    # 3. Test öğrencileri oluştur
    test_students = [
        {
            'id_number': '25666680908',
            'first_name': 'Ahmet',
            'last_name': 'Yılmaz',
            'parent_first_name': 'Mehmet',
            'parent_last_name': 'Yılmaz',
            'parent_phone_number': '+905551234567'
        },
        {
            'id_number': '12345678901',
            'first_name': 'Ayşe',
            'last_name': 'Demir',
            'parent_first_name': 'Fatma',
            'parent_last_name': 'Demir',
            'parent_phone_number': '+905559876543'
        },
        {
            'id_number': '98765432109',
            'first_name': 'Mehmet',
            'last_name': 'Kaya',
            'parent_first_name': 'Ali',
            'parent_last_name': 'Kaya',
            'parent_phone_number': '+905558765432'
        }
    ]
    
    for student_data in test_students:
        student, created = Student.objects.get_or_create(
            id_number=student_data['id_number'],
            defaults={
                'first_name': student_data['first_name'],
                'last_name': student_data['last_name'],
                'school': school,
                'classroom': classroom,
                'parent_first_name': student_data['parent_first_name'],
                'parent_last_name': student_data['parent_last_name'],
                'parent_phone_number': student_data['parent_phone_number']
            }
        )
        
        if created:
            print(f"✅ Öğrenci oluşturuldu: {student.full_name} ({student.id_number})")
        else:
            print(f"ℹ️  Öğrenci zaten mevcut: {student.full_name} ({student.id_number})")
    
    # 4. Admin kullanıcısı kontrol
    if not User.objects.filter(is_superuser=True).exists():
        print("👤 Admin kullanıcısı bulunamadı!")
        print("💡 Şu komutu çalıştırın: python manage.py createsuperuser")
    else:
        admin_user = User.objects.filter(is_superuser=True).first()
        print(f"✅ Admin kullanıcısı mevcut: {admin_user.username}")
    
    print("\n🎉 Test verisi hazır!")
    print(f"📊 Toplam okul: {School.objects.count()}")
    print(f"📊 Toplam sınıf: {Classroom.objects.count()}")
    print(f"📊 Toplam öğrenci: {Student.objects.count()}")
    
    print("\n🔗 Test URL'leri:")
    print("• Ana sayfa: https://baskentpsikoloji.pythonanywhere.com/")
    print("• Öğrenci giriş: https://baskentpsikoloji.pythonanywhere.com/student-checkin/")
    print("• Test API: https://baskentpsikoloji.pythonanywhere.com/student-status/25666680908/")
    print("• Admin panel: https://baskentpsikoloji.pythonanywhere.com/admin/")

if __name__ == '__main__':
    create_test_data()