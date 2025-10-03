from django.contrib import admin
from .models import School, Classroom, Student, Attendance


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'address')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('Okul Bilgileri', {
            'fields': ('name', 'address', 'is_active')
        }),
        ('Sistem Bilgileri', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yeni kayıt ise
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'is_active', 'created_by', 'created_at')
    list_filter = ('school', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'school__name')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('Sınıf Bilgileri', {
            'fields': ('name', 'school', 'is_active')
        }),
        ('Sistem Bilgileri', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yeni kayıt ise
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'id_number', 'school', 'classroom', 
        'parent_full_name', 'is_active', 'created_at'
    )
    list_filter = ('school', 'classroom', 'is_active', 'created_at', 'updated_at')
    search_fields = (
        'first_name', 'last_name', 'id_number', 
        'parent_first_name', 'parent_last_name', 'parent_phone_number'
    )
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('Öğrenci Bilgileri', {
            'fields': ('first_name', 'last_name', 'id_number', 'phone_number')
        }),
        ('Okul Bilgileri', {
            'fields': ('school', 'classroom', 'is_active')
        }),
        ('Veli Bilgileri', {
            'fields': ('parent_first_name', 'parent_last_name', 'parent_phone_number')
        }),
        ('Sistem Bilgileri', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yeni kayıt ise
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Ad Soyad'
    
    def parent_full_name(self, obj):
        return obj.parent_full_name
    parent_full_name.short_description = 'Veli Ad Soyad'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student_full_name', 'student_id_number', 'entry_type', 
        'date', 'timestamp', 'student_school', 'student_classroom'
    )
    list_filter = ('entry_type', 'date', 'student__school', 'student__classroom')
    search_fields = (
        'student__first_name', 'student__last_name', 'student__id_number'
    )
    readonly_fields = ('timestamp', 'date')
    list_per_page = 25
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Yoklama Bilgileri', {
            'fields': ('student', 'entry_type')
        }),
        ('Zaman Bilgileri', {
            'fields': ('timestamp', 'date'),
            'classes': ('collapse',)
        }),
    )
    
    def student_full_name(self, obj):
        return obj.student.full_name
    student_full_name.short_description = 'Öğrenci Adı'
    student_full_name.admin_order_field = 'student__first_name'
    
    def student_id_number(self, obj):
        return obj.student.id_number
    student_id_number.short_description = 'TC Kimlik No'
    student_id_number.admin_order_field = 'student__id_number'
    
    def student_school(self, obj):
        return obj.student.school.name
    student_school.short_description = 'Okul'
    student_school.admin_order_field = 'student__school__name'
    
    def student_classroom(self, obj):
        return str(obj.student.classroom)
    student_classroom.short_description = 'Sınıf'
    student_classroom.admin_order_field = 'student__classroom__name'
