from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('apply/', views.apply_leave, name='apply_leave'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:id>/', views.approve_leave, name='approve_leave'),
    path('delete/<int:id>/', views.delete_leave, name='delete_leave'),
    path('logout/', views.logout_view, name='logout'),
    path('update-status/<int:id>/', views.update_leave_status, name='update_leave_status'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('delete-employee/<int:id>/', views.delete_employee, name='delete_employee'),
    path('update-employee/<int:id>/', views.update_employee, name='update_employee'),
    path('delete-leave/<int:id>/', views.delete_leave, name='delete_leave'),
]