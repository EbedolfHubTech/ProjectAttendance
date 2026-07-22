from django.db import models
from django.utils import timezone

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    student_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    student_class = models.CharField(max_length=50) # e.g., ND1, HND2
    course_offered = models.CharField(max_length=100) # e.g., OTM, Computer Science

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    is_present = models.BooleanField(default=True)
    absence_reason = models.TextField(blank=True, null=True, default="N/A")

    @property
    def formatted_timestamp(self):
        # Format: HH:MM:SS DDMMYY
        return self.timestamp.strftime("%H:%M:%S %d%m%y")

    class Meta:
        unique_together = ('student', 'timestamp')