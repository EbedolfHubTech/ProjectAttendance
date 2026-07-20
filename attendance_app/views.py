import json
from django.shortcuts import render
from django.http import JsonResponse
from .models import Student, Attendance

# 1. Main Dashboard View
def dashboard(request):
    students = Student.objects.all()
    attendance_records = Attendance.objects.all().order_by('-time')
    
    # Get a list of all student IDs who have scanned in today
    present_student_ids = Attendance.objects.values_list('student_id', flat=True)
    
    # Separate students based on whether their ID is in the present list
    present_students = Student.objects.filter(student_id__in=present_student_ids)
    absent_students = Student.objects.exclude(student_id__in=present_student_ids)

    return render(request, 'attendance_app/dashboard.html', {
        'students': students,
        'attendance': attendance_records,
        'present_students': present_students,
        'absent_students': absent_students[:20], # Show the first 20 absent students to keep it clean
        'absent_count': absent_students.count()
    })
# 2. Browser Scanner Interface View
def scan_page(request):
    return render(request, 'attendance_app/scan.html')

# 3. Process the QR Scan & Prevent Duplicates
def mark_attendance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            student = Student.objects.get(student_id=data['student_id'])
            attendance, created = Attendance.objects.get_or_create(student=student)
            
            if created:
                return JsonResponse({'message': f'✅ Attendance marked for {student.name}'})
            return JsonResponse({'message': '❌ Already marked today!'})
            
        except Student.DoesNotExist:
            return JsonResponse({'message': '❌ Student ID not found.'})
            
    return JsonResponse({'message': 'Invalid Request'}, status=400)