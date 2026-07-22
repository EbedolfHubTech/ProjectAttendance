from django.contrib import admin
from django.urls import path
from attendance_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.scan_page, name='scan_page'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
]