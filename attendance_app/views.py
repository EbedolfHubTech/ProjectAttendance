from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
import json
from .models import Student, Attendance

def scan_page(request):
    """Renders the webcam scanner page"""
    return render(request, 'attendance_app/scan.html')

def mark_attendance(request):
    """API endpoint called when QR code is scanned via webcam"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            
            student = Student.objects.get(student_id=student_id)
            
            # Check if student already marked attendance today
            today = timezone.now().date()
            already_marked = Attendance.objects.filter(student=student, timestamp__date=today).exists()
            
            if already_marked:
                return JsonResponse({'message': f'Attendance already marked for {student.full_name} today!'})
            
            Attendance.objects.create(student=student, is_present=True)
            return JsonResponse({'message': f'Attendance marked successfully for {student.full_name}!'})
            
        except Student.DoesNotExist:
            return JsonResponse({'message': 'Error: Student ID not found in database!'}, status=404)
        except Exception as e:
            return JsonResponse({'message': f'Error: {str(e)}'}, status=400)

def attendance_report(request):
    """Lecturer report page with timeframe, gender, class, and course filters"""
    today = timezone.now().date()
    
    filter_option = request.GET.get('time_filter', 'today')
    selected_class = request.GET.get('student_class', '')
    selected_course = request.GET.get('course_offered', '')
    selected_gender = request.GET.get('gender', '')

    if filter_option == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = start_date
    elif filter_option == 'day_before_yesterday':
        start_date = today - timedelta(days=2)
        end_date = start_date
    elif filter_option == 'week_ago':
        start_date = today - timedelta(days=7)
        end_date = today
    elif filter_option == 'month_ago':
        start_date = today - timedelta(days=30)
        end_date = today
    else:
        start_date = today
        end_date = today

    attendance_records = Attendance.objects.filter(
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    )

    if selected_class:
        attendance_records = attendance_records.filter(student__student_class=selected_class)
    if selected_course:
        attendance_records = attendance_records.filter(student__course_offered=selected_course)
    if selected_gender:
        attendance_records = attendance_records.filter(student__gender=selected_gender)

    summary = attendance_records.aggregate(
        total_records=Count('id'),
        total_present=Count('id', filter=Q(is_present=True)),
        total_absent=Count('id', filter=Q(is_present=False)),
        total_males=Count('id', filter=Q(student__gender='M')),
        total_females=Count('id', filter=Q(student__gender='F')),
    )

    context = {
        'attendance_records': attendance_records,
        'filter_option': filter_option,
        'summary': summary,
        'classes': Student.objects.values_list('student_class', flat=True).distinct(),
        'courses': Student.objects.values_list('course_offered', flat=True).distinct(),
    }
    return render(request, 'attendance_app/report.html', context)