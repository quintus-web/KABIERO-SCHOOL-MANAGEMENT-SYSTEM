# finance/urls.py
from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [
    # Explicitly mapping names to resolve both 'main_portal_home' and 'portal_home'
    path('dashboard/', views.bursar_dashboard, name='bursar_dashboard'),
    path('portal/', views.main_portal_home, name='main_portal_home'),
    path('portal/home/', views.main_portal_home, name='portal_home'), 
    
    # Financial Ledgers & Receipts
    path('statement/<int:student_id>/', views.student_account_statement, name='student_statement'),
    path('collect-fee/<int:student_id>/', views.collect_fee_payment, name='collect_fee'),
    path('sms-alerts/', views.fee_defaulters_sms_portal, name='fee_sms_portal'),
    
    # Academics spread mapping 
    path('marks/entry/', views.marks_entry_portal, name='marks_entry_portal'),
    path('academics/analytics/', views.academic_analytics_dashboard, name='academic_analytics'),
    path('faculty/directory/', views.faculty_directory, name='faculty_directory'),
    
    # Parent gateway link route map
    path('parents/access/', views.parent_portal_gateway, name='parent_gateway'),

    path('login/', views.staff_login_view, name='staff_login'),
    path('logout/', views.staff_logout_view, name='staff_logout'),
]