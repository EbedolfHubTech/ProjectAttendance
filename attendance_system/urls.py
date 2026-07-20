from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from attendance_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('scan/', views.scan_page, name='scan_page'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)