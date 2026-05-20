# finance/admin.py
from django.contrib import admin
from .models import Teacher, ClassStream, Subject, Student, FeeInvoice, FeeReceipt, ExamRecord

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('tsc_number', 'first_name', 'last_name', 'email', 'phone_number', 'is_class_teacher')
    search_fields = ('tsc_number', 'first_name', 'last_name', 'email')
    list_filter = ('is_class_teacher',)

@admin.register(ClassStream)
class ClassStreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_teacher')
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    filter_horizontal = ('teachers',) # Provides a clean selection widget for multi-teacher assignment

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'first_name', 'last_name', 'class_stream', 'parent_phone', 'is_active')
    search_fields = ('admission_number', 'first_name', 'last_name', 'parent_phone')
    list_filter = ('class_stream', 'is_active')

@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'term', 'year', 'amount', 'created_at')
    search_fields = ('student__admission_number', 'student__first_name', 'student__last_name')
    list_filter = ('term', 'year', 'created_at')

@admin.register(FeeReceipt)
class FeeReceiptAdmin(admin.ModelAdmin):
    list_display = ('reference_code', 'student', 'amount_paid', 'payment_channel', 'status', 'created_at')
    search_fields = ('reference_code', 'student__admission_number', 'student__first_name', 'student__last_name')
    list_filter = ('payment_channel', 'status', 'created_at')

@admin.register(ExamRecord)
class ExamRecordAdmin(admin.ModelAdmin):
    # Fixed alignment list: refers exactly to attributes or model property methods present on the new schema
    list_display = ('student', 'subject', 'term', 'year', 'cat_1', 'cat_2', 'final_exam', 'get_total_marks')
    search_fields = ('student__admission_number', 'student__first_name', 'student__last_name', 'subject__name')
    list_filter = ('term', 'year', 'subject')

    def get_total_marks(self, obj):
        """Helper to expose model properties cleanly inside table rows listing grids"""
        return f"{obj.total_marks:.1f}%"
    
    get_total_marks.short_description = 'Aggregate Total Score'