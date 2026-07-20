import os
import django
import pandas as pd

# Setup Django environment configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance_app.models import Student

def load_data():
    excel_file_path = 'student_attendance_dataset.csv.xlsx' 
    
    if not os.path.exists(excel_file_path):
        print(f"❌ Error: Could not find '{excel_file_path}' in this folder.")
        return

    print("Reading Excel dataset...")
    df = pd.read_excel(excel_file_path)
    
    # Standardize column headers to lowercase to avoid matching errors
    df.columns = [str(col).strip().lower() for col in df.columns]
    print("Standardized Columns found:", df.columns.tolist())
    
    # Automatically look for matching column names
    id_col = next((c for c in df.columns if 'id' in c), None)
    name_col = next((c for c in df.columns if 'name' in c), None)
    course_col = next((c for c in df.columns if 'course' in c or 'class' in c or 'module' in c), None)
    
    if not id_col or not name_col or not course_col:
        print("❌ Error: Could not automatically map columns.")
        print(f"Detected mapping -> ID: {id_col}, Name: {name_col}, Course: {course_col}")
        return
        
    students_to_create = []
    print(f"Processing {len(df)} records... Please wait.")
    
    for index, row in df.iterrows():
        # Clean data into plain strings
        s_id = str(row[id_col]).strip()
        s_name = str(row[name_col]).strip()
        s_course = str(row[course_col]).strip()
        
        if not Student.objects.filter(student_id=s_id).exists():
            students_to_create.append(
                Student(
                    student_id=s_id,
                    name=s_name,
                    course=s_course
                )
            )
            
    if students_to_create:
        Student.objects.bulk_create(students_to_create)
        print(f"✅ Successfully added {len(students_to_create)} new students to the database!")
    else:
        print("ℹ️ No new records to add. They might already exist.")

if __name__ == '__main__':
    load_data()