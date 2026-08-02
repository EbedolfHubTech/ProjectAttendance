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
    """Lecturer report page with timeframe, exact date, name search, gender, class, and course filters"""
    today = timezone.now().date()
    
    # Query parameters
    search_query = request.GET.get('q', '').strip()
    exact_date = request.GET.get('exact_date', '')
    filter_option = request.GET.get('time_filter', 'today')
    selected_class = request.GET.get('student_class', '')
    selected_course = request.GET.get('course_offered', '')
    selected_gender = request.GET.get('gender', '')

    attendance_records = Attendance.objects.select_related('student').all()

    # 1. Filter by Exact Date (e.g., 2026-10-01) if provided
    if exact_date:
        attendance_records = attendance_records.filter(timestamp__date=exact_date)
    else:
        # 2. Otherwise, filter by Timeframe Range
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
        elif filter_option == '6months':
            start_date = today - timedelta(days=180)
            end_date = today
        elif filter_option == 'all_time':
            start_date = None
            end_date = None
        else: # 'today' default
            start_date = today
            end_date = today

        if start_date and end_date:
            attendance_records = attendance_records.filter(
                timestamp__date__gte=start_date,
                timestamp__date__lte=end_date
            )

    # 3. Search by Student Name or Student ID
    if search_query:
        attendance_records = attendance_records.filter(
            Q(student__full_name__icontains=search_query) |
            Q(student__student_id__icontains=search_query)
        )

    # 4. Attribute Filters
    if selected_class:
        attendance_records = attendance_records.filter(student__student_class=selected_class)
    if selected_course:
        attendance_records = attendance_records.filter(student__course_offered=selected_course)
    if selected_gender:
        attendance_records = attendance_records.filter(student__gender=selected_gender)

    # Order newest first
    attendance_records = attendance_records.order_by('-timestamp')

    # Summary Statistics for filtered dataset
    summary = attendance_records.aggregate(
        total_records=Count('id'),
        total_present=Count('id', filter=Q(is_present=True)),
        total_absent=Count('id', filter=Q(is_present=False)),
        total_males=Count('id', filter=Q(student__gender__iexact='m') | Q(student__gender__iexact='male')),
        total_females=Count('id', filter=Q(student__gender__iexact='f') | Q(student__gender__iexact='female')),
    )

    context = {
        'attendance_records': attendance_records,
        'filter_option': filter_option,
        'exact_date': exact_date,
        'search_query': search_query,
        'selected_class': selected_class,
        'selected_course': selected_course,
        'selected_gender': selected_gender,
        'summary': summary,
        'classes': Student.objects.values_list('student_class', flat=True).distinct(),
        'courses': Student.objects.values_list('course_offered', flat=True).distinct(),
    }
    return render(request, 'attendance_app/report.html', context)