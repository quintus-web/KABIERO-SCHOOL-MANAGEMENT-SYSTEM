# finance/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Navigation Core Home Portal Link
    path('', views.main_portal_home, name='main_portal_home'),
    
    # Financial Hub & Bursar Dashboard Operations Paths
    path('finance/dashboard/', views.bursar_dashboard, name='bursar_dashboard'),
    path('finance/statement/student/<int:student_id>/', views.student_account_statement, name='student_statement'),
    path('finance/collect-fee/student/<int:student_id>/', views.collect_fee_payment, name='collect_fee'),
    
    # Text Alerts Communication Management System Link
    path('finance/communications/sms-reminders/', views.fee_defaulters_sms_portal, name='fee_sms_portal'),
    
    # Academic Grading Registry Portals
    path('finance/marks/entry/', views.marks_entry_portal, name='marks_entry_portal'),
    path('finance/academics/analytics/', views.academic_analytics_dashboard, name='academic_analytics'),
    
    # External Parent Gateway Subdomain Interface Portal
    path('parents/access/', views.parent_portal_gateway, name='parent_gateway'),
    
    # Faculty Management Staff Directory
    path('faculty/directory/', views.faculty_directory, name='faculty_directory'),
]