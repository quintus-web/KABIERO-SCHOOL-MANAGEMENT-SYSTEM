# sms_core/urls.py
from django.shortcuts import redirect
from django.urls import path, include


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('bursar_dashboard')
    return redirect('staff_login')


urlpatterns = [
    path('', root_redirect, name='public_home'),
    path('', include('finance.urls')),
]
