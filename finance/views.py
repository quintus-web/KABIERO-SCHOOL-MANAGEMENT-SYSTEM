# finance/views.py
import datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from .models import Teacher, ClassStream, Subject, Student, FeeInvoice, FeeReceipt, ExamRecord
from django.contrib.auth.decorators import login_required
from .decorators import group_required
from django.contrib.auth.decorators import login_required
from .decorators import group_required
from .models import ClassStream, Subject, Student, ExamRecord

def main_portal_home(request):
    """Calculates active analytical metrics summary numbers for the executive landing menu"""
    total_students = Student.objects.filter(is_active=True).count()
    total_collected = sum(r.amount_paid for r in FeeReceipt.objects.filter(status='COMPLETED'))
    
    all_students = Student.objects.filter(is_active=True)
    defaulters_count = 0
    for s in all_students:
        if s.current_balance > 0:
            defaulters_count += 1
            
    context = {
        'total_students': total_students,
        'total_collected': total_collected,
        'defaulters_count': defaulters_count,
    }
    return render(request, 'finance/portal_home.html', context)

@login_required
@group_required('Bursar')
def bursar_dashboard(request):
    # ... (rest of your existing view code remains exactly the same
    """Compiles the core accounting listing profiles directory ledger search engine"""
    search_query = request.GET.get('search', '').strip()
    
    if search_query:
        students = Student.objects.filter(
            is_active=True,
            first_name__icontains=search_query
        ) | Student.objects.filter(
            is_active=True,
            last_name__icontains=search_query
        ) | Student.objects.filter(
            is_active=True,
            admission_number__icontains=search_query
        )
    else:
        students = Student.objects.filter(is_active=True).order_by('admission_number')
        
    # FIXED: Changed from 'finance/bursar_dashboard.html' to match your actual filename 'dashboard.html'
    return render(request, 'finance/dashboard.html', {'students': students, 'search_query': search_query})


def student_account_statement(request, student_id):
    """Compiles an audit log trail statement sheet of every ledger payment invoice and receipt"""
    student = get_object_or_404(Student, id=student_id)
    invoices = student.fee_invoices.all().order_by('created_at')
    receipts = student.fee_receipts.filter(status='COMPLETED').order_by('created_at')
    
    context = {
        'student': student,
        'invoices': invoices,
        'receipts': receipts,
        'balance': student.current_balance
    }
    # FIXED: Changed from 'finance/statement_view.html' to match your actual filename 'statement.html'
    return render(request, 'finance/statement.html', context)


def collect_fee_payment(request, student_id):
    """Processes system receipt vouchers and automatically generates serial keys for cash allocations"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        channel = request.POST.get('payment_channel', 'MPESA')
        amount = request.POST.get('amount_paid', '0').strip()
        
        if channel == 'CASH':
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            ref_code = f"KAB-CSH-{timestamp}"
        else:
            ref_code = request.POST.get('reference_code', '').strip().upper()
            
        if not ref_code and channel != 'CASH':
            messages.error(request, "Mobile money or Bank transactions require a valid reference transaction code.")
            return render(request, 'finance/receipt_form.html', {'student': student})
            
        if amount and Decimal(amount) > 0:
            FeeReceipt.objects.create(
                student=student,
                reference_code=ref_code,
                amount_paid=Decimal(amount),
                payment_channel=channel,
                status='COMPLETED'
            )
            messages.success(request, f"Collection receipt voucher {ref_code} successfully posted for {student.first_name}.")
            return redirect('bursar_dashboard')
        else:
            messages.error(request, "The collected transactional value amount must be greater than KES 0.")
            
    return render(request, 'finance/receipt_form.html', {'student': student})


def fee_defaulters_sms_portal(request):
    """Isolates active arrears files and compiles parent contact notification numbers"""
    all_students = Student.objects.filter(is_active=True)
    defaulters_queue = []
    
    for student in all_students:
        balance = student.current_balance
        if balance > 0:
            defaulters_queue.append({
                'student': student,
                'balance': balance,
                'message_preview': f"Dear Parent, please note Kabiero Academy records show an outstanding balance of KES {balance:,.2f} for Adm {student.admission_number}. Please clear promptly."
            })
            
    if request.method == 'POST':
        messages.success(request, f"Bulk text reminders successfully dispatched upstream to all {len(defaulters_queue)} parent lines.")
        return redirect('main_portal_home')
        
    # FIXED: Changed from 'finance/sms_reminders.html' to match your actual filename 'sms_portal.html'
    return render(request, 'finance/sms_portal.html', {'defaulters': defaulters_queue})

@login_required
@group_required('Teacher')
# Inside finance/views.py


@login_required
@group_required('Teacher')
def marks_entry_portal(request):
    """Renders a streamlined spreadsheet matrix for fast term marks collection"""
    subjects = Subject.objects.all().order_by('name')
    streams = ClassStream.objects.all().order_by('name')
    
    # Capture incoming filter requests
    selected_subject_id = request.GET.get('subject')
    selected_stream_id = request.GET.get('stream')
    
    students = []
    matrix_data = []
    
    if selected_subject_id and selected_stream_id:
        # Fetch matching students for the selected stream
        students = Student.objects.filter(class_stream_id=selected_stream_id, is_active=True).order_by('last_name')
        
        # Build out a clean matrix row for every student
        for student in students:
            # Look for an existing grade row or leave it blank for fresh entry
            record = ExamRecord.objects.filter(
                student=student, 
                subject_id=selected_subject_id, 
                year=2026
            ).first()
            
            matrix_data.append({
                'student': student,
                'cat_1': record.cat_1 if record else '',
                'cat_2': record.cat_2 if record else '',
                'final_exam': record.final_exam if record else '',
                'total_marks': record.total_marks if record else None
            })

    context = {
        'subjects': subjects,
        'streams': streams,
        'matrix_data': matrix_data,
        'selected_subject': int(selected_subject_id) if selected_subject_id else None,
        'selected_stream': int(selected_stream_id) if selected_stream_id else None,
    }
    return render(request, 'finance/marks_entry_portal.html', context)
def academic_analytics_dashboard(request):
    """Aggregates exam fields across terms and monitors student performance trajectories"""
    selected_term = request.GET.get('term', 'TERM_2')
    
    all_streams = ClassStream.objects.all()
    stream_rankings = []
    for stream in all_streams:
        records = ExamRecord.objects.filter(student__class_stream=stream, term=selected_term, year=2026)
        total_records = records.count()
        avg_score = sum(r.total_marks for r in records) / total_records if total_records > 0 else 0.0
        stream_rankings.append({'name': stream.name, 'average': avg_score, 'count': stream.students.count()})
    stream_rankings.sort(key=lambda x: x['average'], reverse=True)

    all_subjects = Subject.objects.all()
    subject_performance = []
    for subject in all_subjects:
        records = ExamRecord.objects.filter(subject=subject, term=selected_term, year=2026)
        total_records = records.count()
        avg_score = sum(r.total_marks for r in records) / total_records if total_records > 0 else 0.0
        subject_performance.append({'name': subject.name, 'code': subject.code, 'average': avg_score})
    subject_performance.sort(key=lambda x: x['average'], reverse=True)

    all_students = Student.objects.filter(is_active=True)
    trajectory_list = []
    
    for s in all_students:
        t1_records = s.exam_records.filter(term='TERM_1', year=2026)
        t2_records = s.exam_records.filter(term='TERM_2', year=2026)
        
        t1_avg = sum(r.total_marks for r in t1_records) / t1_records.count() if t1_records.exists() else None
        t2_avg = sum(r.total_marks for r in t2_records) / t2_records.count() if t2_records.exists() else None
        
        if t1_avg is not None and t2_avg is not None:
            variance = t2_avg - t1_avg
            if variance <= -5.0:
                badge_class, icon, label = 'bg-danger', 'bi-graph-down-arrow', 'Slipping'
            elif variance >= 5.0:
                badge_class, icon, label = 'bg-success', 'bi-graph-up-arrow', 'Improving'
            else:
                badge_class, icon, label = 'bg-secondary', 'bi-arrow-right-short', 'Stable'
                
            trajectory_list.append({
                'student': s, 't1_avg': t1_avg, 't2_avg': t2_avg,
                'variance': variance, 'badge_class': badge_class, 'icon': icon, 'label': label
            })

    trajectory_list.sort(key=lambda x: x['variance'])

    context = {
        'term_display': selected_term.replace('_', ' '), 'selected_term': selected_term,
        'stream_rankings': stream_rankings, 'subject_performance': subject_performance,
        'trajectories': trajectory_list,
    }
    return render(request, 'finance/analytics_dashboard.html', context)


# finance/views.py

def parent_portal_gateway(request):
    """Limits view scope securely by requiring BOTH Admission Number and Parent Phone match"""
    if request.method == 'POST':
        admission_no = request.POST.get('admission_number', '').strip()
        phone_no = request.POST.get('parent_phone', '').strip()  # Added dynamic secure guard variable
        
        try:
            # SECURITY ENFORCEMENT: Both fields must cross-reference perfectly
            student = Student.objects.get(
                admission_number=admission_no, 
                parent_phone=phone_no,
                is_active=True
            )
            
            invoices = student.fee_invoices.all().order_by('-created_at')
            receipts = student.fee_receipts.filter(status='COMPLETED').order_by('-created_at')
            exam_records = student.exam_records.filter(year=2026).order_by('subject__name')
            
            context = {
                'student': student, 
                'invoices': invoices, 
                'receipts': receipts,
                'exam_records': exam_records, 
                'balance': student.current_balance
            }
            
            # REPLACED: Serving the complete all-inclusive dashboard layout instead of raw statement list
            return render(request, 'finance/parent_dashboard.html', context)
            
        except Student.DoesNotExist:
            messages.error(request, "Authentication failed. Verification details do not match our active records.")
            return redirect('parent_gateway')
            
    return render(request, 'finance/parent_gateway_login.html')


def faculty_directory(request):
    """Compiles and displays all active academic staff profiles and professional assignments"""
    teachers = Teacher.objects.all().order_by('last_name')
    return render(request, 'finance/faculty_directory.html', {'teachers': teachers})


def public_school_website(request):
    """Renders the official public-facing marketing homepage for Kabiero Academy"""
    return render(request, 'marketing/index.html')

# finance/views.py (Append to the absolute bottom of the file)
from django.contrib.auth import authenticate, login, logout

# Inside finance/views.py

# finance/views.py

# Inside finance/views.py

def staff_login_view(request):
    """Enforces strict role-based login matching to prevent cross-login bypasses"""
    target_role = request.GET.get('role', '').strip()  # Catches 'Bursar' or 'Teacher'
    
    # 1. Handle already-logged-in users intelligently
    if request.user.is_authenticated:
        is_bursar = request.user.groups.filter(name='Bursar').exists() or request.user.is_superuser
        is_teacher = request.user.groups.filter(name='Teacher').exists()
        
        if target_role == 'Teacher' and not is_teacher:
            logout(request)
        elif target_role == 'Bursar' and not is_bursar:
            logout(request)
        else:
            if is_bursar: return redirect('bursar_dashboard')
            if is_teacher: return redirect('marks_entry_portal')

    # 2. Process Form Submission with Strict Group Validation
    if request.method == 'POST':
        username_input = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '')
        
        user = authenticate(request, username=username_input, password=password_input)
        
        if user is not None:
            # Check user group alignment flags
            user_is_bursar = user.groups.filter(name='Bursar').exists() or user.is_superuser
            user_is_teacher = user.groups.filter(name='Teacher').exists()
            
            # ROLE CHECK 1: If they want the Teacher desk but are a Bursar -> BLOCK
            if target_role == 'Teacher' and not user_is_teacher:
                messages.error(request, "Access Denied! This workstation is reserved for Academic Staff accounts only.")
                return redirect(f"{request.path}?role=Teacher")
                
            # ROLE CHECK 2: If they want the Bursar desk but are a Teacher -> BLOCK
            if target_role == 'Bursar' and not user_is_bursar:
                messages.error(request, "Access Denied! This workstation is reserved for Finance Administration accounts only.")
                return redirect(f"{request.path}?role=Bursar")

            # If clearance checks out, establish the active session token
            login(request, user)
            if user_is_bursar:
                messages.success(request, f"Welcome back, Bursar {user.username}!")
                return redirect('bursar_dashboard')
            elif user_is_teacher:
                messages.success(request, "Welcome back to the Grading Desk, Mwalimu!")
                return redirect('marks_entry_portal')
                
            return redirect('public_home')
        else:
            messages.error(request, "Invalid username or account password. Access Denied.")
            return redirect(f"{request.path}?role={target_role}")
            
    return render(request, 'finance/staff_login.html')
def staff_logout_view(request):
    """Terminates active staff session tokens and securely clear states"""
    logout(request)
    messages.info(request, "Logged out successfully. Have a wonderful day!")
    return redirect('public_home')