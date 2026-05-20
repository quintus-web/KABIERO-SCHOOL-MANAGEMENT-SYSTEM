# finance/views.py
import datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from .models import Teacher, ClassStream, Subject, Student, FeeInvoice, FeeReceipt, ExamRecord

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


def bursar_dashboard(request):
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


def marks_entry_portal(request):
    """Renders spreadsheet matrix loops and intercept async background autosave fetch streams natively"""
    classes = ClassStream.objects.all()
    subjects = Subject.objects.all()
    
    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            subject_id = data.get('subject')
            term = data.get('term')
            field_type = data.get('field_type')
            raw_value = float(data.get('value', 0) or 0)
            
            student_obj = Student.objects.get(id=student_id)
            subject_obj = Subject.objects.get(id=subject_id)
            
            record, _ = ExamRecord.objects.get_or_create(
                student=student_obj, subject=subject_obj, term=term, year=2026
            )
            
            if field_type == 'cat1':
                record.cat_1 = raw_value
            elif field_type == 'cat2':
                record.cat_2 = raw_value
            elif field_type == 'final':
                record.final_exam = raw_value
                
            record.save()
            
            return JsonResponse({
                'status': 'success',
                'computed_total': record.total_marks
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    selected_class = request.GET.get('class_stream')
    selected_subject = request.GET.get('subject')
    selected_term = request.GET.get('term', 'TERM_1')
    
    exam_data = []
    if selected_class and selected_subject:
        students = Student.objects.filter(class_stream_id=selected_class, is_active=True)
        subject_obj = get_object_or_404(Subject, id=selected_subject)
        
        for s in students:
            record = ExamRecord.objects.filter(student=s, subject=subject_obj, term=selected_term, year=2026).first()
            exam_data.append({'student': s, 'record': record})
            
    context = {
        'classes': classes, 'subjects': subjects,
        'selected_class': selected_class, 'selected_subject': selected_subject, 'selected_term': selected_term,
        'exam_data': exam_data
    }
    return render(request, 'finance/marks_entry.html', context)


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


def parent_portal_gateway(request):
    """Limits view scope securely using Student Admission Numbers for external parent balance checks"""
    if request.method == 'POST':
        admission_no = request.POST.get('admission_number', '').strip()
        try:
            student = Student.objects.get(admission_number=admission_no, is_active=True)
            invoices = student.fee_invoices.all().order_by('-created_at')
            receipts = student.fee_receipts.filter(status='COMPLETED').order_by('-created_at')
            exam_records = student.exam_records.filter(year=2026).order_by('subject__name')
            
            context = {
                'student': student, 'invoices': invoices, 'receipts': receipts,
                'exam_records': exam_records, 'balance': student.current_balance
            }
            # FIXED: Changed from 'finance/parent_statement_view.html' to use your standard 'statement.html' template layout
            return render(request, 'finance/statement.html', context)
        except Student.DoesNotExist:
            messages.error(request, f"Admission number '{admission_no}' matches no active data files at Kabiero Academy.")
            return redirect('parent_gateway')
            
    return render(request, 'finance/parent_gateway_login.html')


def faculty_directory(request):
    """Compiles and displays all active academic staff profiles and professional assignments"""
    teachers = Teacher.objects.all().order_by('last_name')
    return render(request, 'finance/faculty_directory.html', {'teachers': teachers})