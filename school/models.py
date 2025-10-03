from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone


class School(models.Model):
    """Okul modeli"""
    name = models.CharField(max_length=200, verbose_name="Okul Adı")
    address = models.TextField(verbose_name="Adres")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_schools',
        verbose_name="Oluşturan Kullanıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Okul"
        verbose_name_plural = "Okullar"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Classroom(models.Model):
    """Sınıf modeli"""
    name = models.CharField(max_length=100, verbose_name="Sınıf Adı")
    school = models.ForeignKey(
        School, 
        on_delete=models.CASCADE, 
        related_name='classrooms',
        verbose_name="Okul"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_classrooms',
        verbose_name="Oluşturan Kullanıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Sınıf"
        verbose_name_plural = "Sınıflar"
        ordering = ['school', 'name']
        unique_together = ['school', 'name']  # Aynı okulda aynı isimde sınıf olamaz
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Student(models.Model):
    """Öğrenci modeli"""
    # Telefon numarası için validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Telefon numarası '+999999999' formatında olmalıdır. 15 haneye kadar rakam girebilirsiniz."
    )
    
    # TC Kimlik numarası için validator
    tc_regex = RegexValidator(
        regex=r'^\d{11}$',
        message="TC Kimlik numarası 11 haneli olmalıdır."
    )
    
    # Öğrenci bilgileri
    first_name = models.CharField(max_length=50, verbose_name="Ad")
    last_name = models.CharField(max_length=50, verbose_name="Soyad")
    id_number = models.CharField(
        max_length=11, 
        unique=True, 
        validators=[tc_regex],
        verbose_name="TC Kimlik No"
    )
    phone_number = models.CharField(
        max_length=17, 
        validators=[phone_regex], 
        blank=True,
        verbose_name="Telefon Numarası"
    )
    
    # İlişkiler
    school = models.ForeignKey(
        School, 
        on_delete=models.CASCADE, 
        related_name='students',
        verbose_name="Okul"
    )
    classroom = models.ForeignKey(
        Classroom, 
        on_delete=models.CASCADE, 
        related_name='students',
        verbose_name="Sınıf"
    )
    
    # Veli bilgileri
    parent_first_name = models.CharField(max_length=50, verbose_name="Veli Adı")
    parent_last_name = models.CharField(max_length=50, verbose_name="Veli Soyadı")
    parent_phone_number = models.CharField(
        max_length=17, 
        validators=[phone_regex],
        verbose_name="Veli Telefon Numarası"
    )
    
    # Sistem alanları
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_students',
        verbose_name="Oluşturan Kullanıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Öğrenci"
        verbose_name_plural = "Öğrenciler"
        ordering = ['school', 'classroom', 'last_name', 'first_name']
        unique_together = ['school', 'classroom', 'id_number']  # Aynı sınıfta aynı TC'li öğrenci olamaz
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.classroom}"
    
    @property
    def full_name(self):
        """Öğrencinin tam adı"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def parent_full_name(self):
        """Velinin tam adı"""
        return f"{self.parent_first_name} {self.parent_last_name}"
    
    def clean(self):
        """Model validasyonu"""
        from django.core.exceptions import ValidationError
        
        # Sınıfın okulla uyumlu olup olmadığını kontrol et
        if self.classroom and self.school:
            if self.classroom.school != self.school:
                raise ValidationError("Seçilen sınıf, seçilen okula ait değil.")
    
    def save(self, *args, **kwargs):
        """Kaydetmeden önce validasyonu çalıştır"""
        self.clean()
        super().save(*args, **kwargs)


class Attendance(models.Model):
    """Yoklama/Giriş-Çıkış modeli"""
    ENTRY_TYPE_CHOICES = [
        ('entry', 'Giriş'),
        ('exit', 'Çıkış'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Öğrenci"
    )
    entry_type = models.CharField(
        max_length=10,
        choices=ENTRY_TYPE_CHOICES,
        verbose_name="Giriş Tipi"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Zaman"
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name="Tarih"
    )
    
    class Meta:
        verbose_name = "Yoklama"
        verbose_name_plural = "Yoklamalar"
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.student.full_name} - {self.get_entry_type_display()} - {self.timestamp.strftime('%d.%m.%Y %H:%M')}"
    
    @classmethod
    def get_last_entry(cls, student):
        """Öğrencinin son giriş/çıkış kaydını getir"""
        return cls.objects.filter(student=student).first()
    
    @classmethod
    def toggle_attendance(cls, student):
        """Öğrencinin durumunu toggle et (giriş <-> çıkış)"""
        last_entry = cls.get_last_entry(student)
        
        # Eğer bugün hiç kayıt yoksa veya son kayıt çıkış ise -> giriş yap
        today = timezone.now().date()
        if not last_entry or last_entry.date != today or last_entry.entry_type == 'exit':
            new_entry_type = 'entry'
        else:
            # Son kayıt bugünden ve giriş ise -> çıkış yap
            new_entry_type = 'exit'
        
        # Yeni kayıt oluştur
        attendance = cls.objects.create(
            student=student,
            entry_type=new_entry_type
        )
        
        return attendance
