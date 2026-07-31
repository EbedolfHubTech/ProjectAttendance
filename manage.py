import os
import django
import pandas as pd

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance_app.models import Student

def import_students_from_excel(file_path):
    # Read Excel file
    df = pd.read_excel(file_path)
    
    # Strip any extra whitespace from column names
    df.columns = df.columns.str.strip()

    created_count = 0
    updated_count = 0

    for index, row in df.iterrows():
        # Map columns from your Excel dataset
        # Adjust the column names in row[...] below to match your Excel header names exactly
        student_id = str(row['Student ID']).strip() if 'Student ID' in row and pd.notna(row['Student ID']) else None
        full_name = str(row['Full Name']).strip() if 'Full Name' in row and pd.notna(row['Full Name']) else ''
        gender = str(row['Gender']).strip() if 'Gender' in row and pd.notna(row['Gender']) else 'Other'
        student_class = str(row['Class']).strip() if 'Class' in row and pd.notna(row['Class']) else ''
        course_offered = str(row['Course Offered']).strip() if 'Course Offered' in row and pd.notna(row['Course Offered']) else ''

        if not student_id:
            print(f"Skipping row {index + 1}: Missing Student ID")
            continue

        # Create or update student record
        student, created = Student.objects.update_or_create(
            student_id=student_id,
            defaults={
                'full_name': full_name,
                'gender': gender,
                'student_class': student_class,
                'course_offered': course_offered,
            }
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

    print(f"Import Complete! Created: {created_count}, Updated: {updated_count}")

if __name__ == "__main__":
    # Replace 'students.xlsx' with the actual path/filename of your Excel dataset
    excel_file_path = 'students.xlsx'
    
    if os.path.exists(excel_file_path):
        import_students_from_excel(excel_file_path)
    else:
        print(f"Error: File '{excel_file_path}' not found. Please place your Excel file in the project folder.")