from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('home', views.home_redirect, name='home'),
    path('student/dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('staff/dashboard/', views.staff_profile_view, name='staff_dashboard'),
    path('student/profile/', views.student_profile_view, name='student_profile'),
    path('staff/profile/', views.staff_profile_view, name='staff_profile'),
    path('staff/menu/', views.update_menu_view, name='update_menu'),
    path('student/menu/', views.menu_view, name='menu'),
    path('student/complain/', views.complain_view, name='complain'),
    path('staff/complaints/', views.ComplaintsView.as_view(), name='complaints'),
    path('staff/ratings/', views.ratings_view, name='ratings'),
    path('staff/attendance', views.attendance_history_view, name='attendance_history'),
    path('staff/bills/', views.bills_view, name='bills'),
    path('staff/bills/download/', views.bills_download_view, name='bills_download')
]
