#!/bin/bash

# PythonAnywhere Migration ve Setup Script
# Bu scripti PythonAnywhere console'da çalıştırın

echo "🚀 PythonAnywhere Database Setup başlıyor..."

# Project dizinine git
cd /home/nurhaksekerci/baskentpsikoloji

# Virtual environment aktif et
echo "📦 Virtual environment aktif ediliyor..."
source venv/bin/activate

# Python version kontrol
echo "🐍 Python version:"
python --version

# Django kontrol
echo "🔧 Django kontrol ediliyor..."
python -c "import django; print(f'Django version: {django.get_version()}')"

# Mevcut migration'ları listele
echo "📋 Mevcut migration'lar:"
python manage.py showmigrations

# Yeni migration'lar oluştur
echo "🔄 Migration'lar oluşturuluyor..."
python manage.py makemigrations school
python manage.py makemigrations

# Migration'ları uygula
echo "⚡ Migration'lar uygulanıyor..."
python manage.py migrate

# Superuser oluştur (eğer yoksa)
echo "👤 Superuser kontrol ediliyor..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser oluşturuldu: admin/admin123')
else:
    print('ℹ️  Superuser zaten mevcut')
"

# Test verisi oluştur
echo "📊 Test verisi oluşturuluyor..."
python create_test_data.py

# Static files toplama
echo "📁 Static files toplanıyor..."
python manage.py collectstatic --noinput

# Database kontrol
echo "🔍 Database tabloları kontrol ediliyor..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table';\")
tables = cursor.fetchall()

print('📋 Database tabloları:')
for table in tables:
    print(f'  - {table[0]}')

# Model kontrol
from school.models import Student, School, Classroom, Attendance
print(f'✅ Okul sayısı: {School.objects.count()}')
print(f'✅ Sınıf sayısı: {Classroom.objects.count()}')
print(f'✅ Öğrenci sayısı: {Student.objects.count()}')
print(f'✅ Yoklama sayısı: {Attendance.objects.count()}')
"

# Test API endpoint
echo "🔗 API endpoint testi..."
python -c "
import django
import os
from django.test import Client
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

client = Client()
response = client.get('/student-status/25666680908/')
print(f'API Response Status: {response.status_code}')
if response.status_code == 200:
    print('✅ API çalışıyor!')
else:
    print(f'❌ API hatası: {response.content.decode()}')
"

echo "🎉 Setup tamamlandı!"
echo ""
echo "📋 Önemli bilgiler:"
echo "• Admin kullanıcısı: admin / admin123"
echo "• Test öğrenci TC: 25666680908"
echo "• Database yolu: /home/nurhaksekerci/baskentpsikoloji/db.sqlite3"
echo ""
echo "🌐 Test URL'leri:"
echo "• https://baskentpsikoloji.pythonanywhere.com/"
echo "• https://baskentpsikoloji.pythonanywhere.com/student-status/25666680908/"
echo ""
echo "💡 Son adım: PythonAnywhere web dashboard'da 'Reload' butonuna basın!"