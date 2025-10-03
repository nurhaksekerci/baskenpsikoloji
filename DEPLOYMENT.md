# PythonAnywhere Deployment Rehberi

## 1. Dosyaları Yükleme
```bash
# Projeyi PythonAnywhere'e yükle
git clone https://github.com/nurhaksekerci/baskentpsikoloji.git
cd baskentpsikoloji
```

## 2. Virtual Environment ve Paketler
```bash
# Virtual environment oluştur
python3.10 -m venv venv
source venv/bin/activate

# Paketleri yükle
pip install -r requirements.txt
```

## 3. Environment Ayarları
```bash
# .env dosyasını oluştur
cp .env.example .env

# .env dosyasını düzenle:
DEBUG=False
ALLOWED_HOSTS=baskentpsikoloji.pythonanywhere.com
```

## 4. Database Setup
```bash
# Migration yap
python manage.py makemigrations
python manage.py migrate

# Admin kullanıcısı oluştur
python manage.py createsuperuser
```

## 5. Static Files
```bash
# Static files topla
python manage.py collectstatic --noinput
```

## 6. WSGI Configuration
PythonAnywhere Web Dashboard'da:

**Source code:** `/home/nurhaksekerci/baskentpsikoloji`
**Working directory:** `/home/nurhaksekerci/baskentpsikoloji`
**WSGI file:** `/var/www/nurhaksekerci_pythonanywhere_com_wsgi.py`

WSGI dosyası içeriği:
```python
import os
import sys

path = '/home/nurhaksekerci/baskentpsikoloji'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 7. Static Files Mapping
PythonAnywhere Web Dashboard → Static files:
- **URL:** `/static/`
- **Directory:** `/home/nurhaksekerci/baskentpsikoloji/staticfiles/`

## 8. URL Configuration
Ana URL: `https://baskentpsikoloji.pythonanywhere.com/`

## 9. Test Etme
- Ana sayfa: `https://baskentpsikoloji.pythonanywhere.com/`
- QR Panel: `https://baskentpsikoloji.pythonanywhere.com/`
- Öğrenci Giriş: `https://baskentpsikoloji.pythonanywhere.com/student-checkin/`
- Admin Panel: `https://baskentpsikoloji.pythonanywhere.com/admin/`

## 10. Hata Ayıklama
Logları kontrol et:
```bash
# Error log
tail -f /var/log/nurhaksekerci.pythonanywhere.com.error.log

# Server log  
tail -f /var/log/nurhaksekerci.pythonanywhere.com.server.log
```

## Yaygın Sorunlar ve Çözümleri

### 1. ModuleNotFoundError
- Virtual environment'ın doğru kurulduğundan emin ol
- Requirements.txt'den paketleri yükle
- WSGI dosyasında path ayarlarını kontrol et

### 2. Static Files Görünmüyor
- `python manage.py collectstatic` çalıştır
- Static files mapping'i doğru ayarla
- STATIC_ROOT doğru olmalı

### 3. Database Hatası
- Migration'ları çalıştır
- SQLite dosya yolunu kontrol et
- Database dosyasına yazma izni ver

### 4. CSRF Error
- ALLOWED_HOSTS'a domain ekle
- CSRF_TRUSTED_ORIGINS ayarla

### 5. 500 Internal Server Error
- DEBUG=True yap (geçici)
- Error loglarını kontrol et
- Print debugs ekle