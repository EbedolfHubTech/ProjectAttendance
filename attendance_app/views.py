from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncHour, TruncDay, TruncWeek, TruncMonth, TruncYear
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
    """Dashboard report with interactive Chart.js analytics"""
    today = timezone.now().date()
    
    # Filters
    search_query = request.GET.get('q', '').strip()
    exact_date = request.GET.get('exact_date', '')
    chart_grouping = request.GET.get('chart_grouping', 'day') # time, day, week, month, year
    selected_class = request.GET.get('student_class', '')
    selected_course = request.GET.get('course_offered', '')
    selected_gender = request.GET.get('gender', '').strip()

    attendance_records = Attendance.objects.select_related('student').all()

    if exact_date:
        attendance_records = attendance_records.filter(timestamp__date=exact_date)

    if search_query:
        attendance_records = attendance_records.filter(
            Q(student__full_name__icontains=search_query) |
            Q(student__student_id__icontains=search_query)
        )

    if selected_class:
        attendance_records = attendance_records.filter(student__student_class=selected_class)
    if selected_course:
        attendance_records = attendance_records.filter(student__course_offered=selected_course)

    # Updated Gender Filter (Handles 'M', 'Male', 'F', and 'Female')
    if selected_gender:
        if selected_gender in ['M', 'Male', 'male']:
            attendance_records = attendance_records.filter(
                Q(student__gender__iexact='M') | Q(student__gender__iexact='Male')
            )
        elif selected_gender in ['F', 'Female', 'female']:
            attendance_records = attendance_records.filter(
                Q(student__gender__iexact='F') | Q(student__gender__iexact='Female')
            )

    # Dynamic Chart Grouping (Truncation)
    if chart_grouping == 'time':
        trunc_func = TruncHour('timestamp')
        date_format = "%I:%00 %p"
    elif chart_grouping == 'week':
        trunc_func = TruncWeek('timestamp')
        date_format = "Week of %b %d"
    elif chart_grouping == 'month':
        trunc_func = TruncMonth('timestamp')
        date_format = "%b %Y"
    elif chart_grouping == 'year':
        trunc_func = TruncYear('timestamp')
        date_format = "%Y"
    else:  # 'day' default
        trunc_func = TruncDay('timestamp')
        date_format = "%b %d, %Y"

    # Aggregate attendance trends for line chart
    trend_data = (
        attendance_records
        .annotate(period=trunc_func)
        .values('period')
        .annotate(count=Count('id'))
        .order_by('period')
    )

    chart_labels = [item['period'].strftime(date_format) if item['period'] else '' for item in trend_data]
    chart_counts = [item['count'] for item in trend_data]

    # Summary Statistics
    summary = attendance_records.aggregate(
        total_records=Count('id'),
        total_present=Count('id', filter=Q(is_present=True)),
        total_absent=Count('id', filter=Q(is_present=False)),
        total_males=Count('id', filter=Q(student__gender__iexact='m') | Q(student__gender__iexact='male')),
        total_females=Count('id', filter=Q(student__gender__iexact='f') | Q(student__gender__iexact='female')),
    )

    context = {
        'attendance_records': attendance_records.order_by('-timestamp'),
        'exact_date': exact_date,
        'search_query': search_query,
        'chart_grouping': chart_grouping,
        'selected_class': selected_class,
        'selected_course': selected_course,
        'selected_gender': selected_gender,
        'summary': summary,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_counts_json': json.dumps(chart_counts),
        'classes': Student.objects.values_list('student_class', flat=True).distinct(),
        'courses': Student.objects.values_list('course_offered', flat=True).distinct(),
    }
    return render(request, 'attendance_app/report.html', context)