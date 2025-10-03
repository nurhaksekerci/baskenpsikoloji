from django.urls import path
from . import views

urlpatterns = [
    # Ana sayfalar
    path('login/', views.login, name='login'),
    
    # QR kod sayfaları
    path('', views.qr_generator, name='teacher_qr'),  # Öğretmen QR paneli
    path('student-checkin/', views.student_checkin, name='student_checkin'),  # Öğrenci giriş-çıkış sayfası
    
    # API endpoints
    path('attendance-toggle/', views.attendance_toggle, name='attendance_toggle'),  # Giriş/çıkış toggle
    path('student-status/<str:id_number>/', views.student_status, name='student_status'),  # Öğrenci durumu
]