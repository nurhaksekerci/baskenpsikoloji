#!/bin/bash

# PythonAnywhere deployment script

echo "🚀 PythonAnywhere deployment başlıyor..."

# Virtual environment oluştur
echo "📦 Virtual environment oluşturuluyor..."
python3.10 -m venv venv
source venv/bin/activate

# Requirements yükle
echo "📋 Paketler yükleniyor..."
pip install -r requirements.txt

# Environment dosyasını kopyala
echo "⚙️ Environment ayarları yapılıyor..."
cp .env.example .env

# Database migrate
echo "🗄️ Database migration yapılıyor..."
python manage.py makemigrations
python manage.py migrate

# Static files topla
echo "📁 Static files toplanıyor..."
python manage.py collectstatic --noinput

# Superuser oluştur (opsiyonel)
echo "👤 Admin kullanıcısı oluşturmak ister misiniz? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

echo "✅ Deployment tamamlandı!"
echo "🌐 Site URL: https://baskentpsikoloji.pythonanywhere.com"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. PythonAnywhere web dashboard'da WSGI dosyasını güncelle"
echo "2. Static files mapping'i ayarla"
echo "3. Environment variables'ları ayarla"