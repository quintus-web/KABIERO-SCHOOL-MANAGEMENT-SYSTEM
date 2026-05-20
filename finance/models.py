# finance/models.py
from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    """Stores professional and contact parameters for Kabiero Academy Faculty"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', null=True, blank=True)
    tsc_number = models.CharField(max_length=20, unique=True, verbose_name="TSC Number")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    is_class_teacher = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Tr. {self.first_name} {self.last_name} ({self.tsc_number})"


class ClassStream(models.Model):
    """Defines classroom streams and links them to their master Class Teacher"""
    name = models.CharField(max_length=50)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_class')

    def __str__(self):
        return self.name


class Subject(models.Model):
    """Tracks curriculum subject metadata codes and handles faculty distribution maps"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    teachers = models.ManyToManyField(Teacher, blank=True, related_name='subjects_taught')

    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    """Keeps records of active students, class assignments, and parental details"""
    admission_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    class_stream = models.ForeignKey(ClassStream, on_delete=models.PROTECT, related_name='students')
    parent_phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.admission_number} - {self.first_name} {self.last_name}"

    @property
    def current_balance(self):
        """Calculates total outstanding arrears by netting sum invoices against completed receipts"""
        total_invoiced = sum(inv.amount for inv in self.fee_invoices.all())
        total_paid = sum(rcpt.amount_paid for rcpt in self.fee_receipts.filter(status='COMPLETED'))
        return total_invoiced - total_paid


class FeeInvoice(models.Model):
    """Logs fee debit requirements billed out to students at start of semester terms"""
    TERM_CHOICES = [('TERM_1', 'Term 1'), ('TERM_2', 'Term 2'), ('TERM_3', 'Term 3')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_invoices')
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    year = models.IntegerField(default=2026)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"INV-{self.id} ({self.student.admission_number}) - KES {self.amount}"


class FeeReceipt(models.Model):
    """Tracks financial credit transactions processed over cash or mobile banking channels"""
    CHANNEL_CHOICES = [('MPESA', 'M-Pesa'), ('BANK', 'Bank Deposit'), ('CASH', 'Hard Cash')]
    STATUS_CHOICES = [('PENDING', 'Pending Validation'), ('COMPLETED', 'Completed Transaction'), ('FAILED', 'Failed/Reversed')]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_receipts')
    reference_code = models.CharField(max_length=50, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='MPESA')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='COMPLETED')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RCPT-{self.reference_code} - KES {self.amount_paid}"


class ExamRecord(models.Model):
    """Stores academic performance results grades across tests terms"""
    TERM_CHOICES = [('TERM_1', 'Term 1'), ('TERM_2', 'Term 2'), ('TERM_3', 'Term 3')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_records')
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    year = models.IntegerField(default=2026)
    cat_1 = models.FloatField(default=0.0) # Out of 15
    cat_2 = models.FloatField(default=0.0) # Out of 15
    final_exam = models.FloatField(default=0.0) # Out of 70
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'term', 'year')

    @property
    def total_marks(self):
        """Returns computed aggregate standard out of 100%"""
        return self.cat_1 + self.cat_2 + self.final_exam

    def __str__(self):
        return f"{self.student.admission_number} - {self.subject.code} ({self.term})"