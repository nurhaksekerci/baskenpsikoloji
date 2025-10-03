#!/bin/bash

# PythonAnywhere Quick Fix Script
# Bu script yaygın deployment sorunlarını hızlıca çözer

echo "🔧 PythonAnywhere Quick Fix başlıyor..."

# 1. Environment dosyasını kopyala
if [ ! -f ".env" ]; then
    echo "📋 .env dosyası oluşturuluyor..."
    cp .env.production .env
    echo "✅ .env dosyası kopyalandı"
fi

# 2. Virtual environment kontrol
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment oluşturuluyor..."
    python3.10 -m venv venv
fi

# 3. Virtual environment aktif et
echo "🔄 Virtual environment aktif ediliyor..."
source venv/bin/activate

# 4. Django secret key oluştur
echo "🔐 Secret key oluşturuluyor..."
python -c "
from django.core.management.utils import get_random_secret_key
print('SECRET_KEY=' + get_random_secret_key())
" >> .env.local

# 5. Database migration
echo "🗄️ Database migration..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# 6. Static files toplama
echo "📁 Static files toplanıyor..."
python manage.py collectstatic --noinput

# 7. Test verisi oluştur
echo "👤 Test verisi oluşturuluyor..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from school.models import School, Classroom, Student

# Test okulu oluştur
school, created = School.objects.get_or_create(
    name='Test Okulu',
    defaults={
        'address': 'Test Adresi',
        'phone_number': '+905551234567',
        'email': 'test@test.com'
    }
)

# Test sınıfı oluştur
classroom, created = Classroom.objects.get_or_create(
    school=school,
    name='Test Sınıfı',
    defaults={'capacity': 30}
)

# Test öğrencisi oluştur
student, created = Student.objects.get_or_create(
    id_number='12345678901',
    defaults={
        'first_name': 'Test',
        'last_name': 'Öğrencisi',
        'school': school,
        'classroom': classroom,
        'parent_first_name': 'Test',
        'parent_last_name': 'Veli',
        'parent_phone_number': '+905551234567'
    }
)

print(f'Test verisi oluşturuldu: {student.full_name}')
"

# 8. Permissions kontrol
echo "🔒 Dosya izinleri kontrol ediliyor..."
chmod +x manage.py
chmod 644 db.sqlite3 2>/dev/null || echo "db.sqlite3 bulunamadı"

# 9. WSGI dosyası kopyala
echo "⚙️ WSGI template kopyalanıyor..."
cp pythonanywhere_wsgi.py wsgi_template.py

echo "✅ Quick fix tamamlandı!"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. PythonAnywhere web dashboard'a git"
echo "2. WSGI file path'i güncelle: /var/www/kullaniciadi_pythonanywhere_com_wsgi.py"
echo "3. wsgi_template.py içeriğini WSGI dosyasına kopyala"
echo "4. Static files mapping ekle: /static/ -> /home/kullaniciadi/baskentpsikoloji/staticfiles/"
echo "5. Reload web app"
echo ""
echo "🌐 Test URL: https://baskentpsikoloji.pythonanywhere.com/student-checkin/"