from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'gender', 'student_class', 'course_offered')
    search_fields = ('student_id', 'full_name', 'student_class', 'course_offered')
    list_filter = ('gender', 'student_class', 'course_offered')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'formatted_timestamp', 'is_present', 'absence_reason')
    list_filter = ('is_present', 'timestamp')
    search_fields = ('student__full_name', 'student__student_id')