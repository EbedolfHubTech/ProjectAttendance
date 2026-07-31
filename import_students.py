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
    gender_col = next((c for c in df.columns if 'gender' in c or 'sex' in c), None)
    
    if not id_col or not name_col:
        print("❌ Error: Could not automatically map essential columns (ID & Name).")
        print(f"Detected mapping -> ID: {id_col}, Name: {name_col}")
        return
        
    students_to_create = []
    print(f"Processing {len(df)} records... Please wait.")
    
    for index, row in df.iterrows():
        # Safely extract values and filter out NaN / empty values
        s_id = str(row[id_col]).strip() if pd.notna(row[id_col]) else None
        s_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ''
        s_course = str(row[course_col]).strip() if course_col and pd.notna(row[course_col]) else ''
        s_gender = str(row[gender_col]).strip() if gender_col and pd.notna(row[gender_col]) else 'Other'
        
        # Skip rows missing a Student ID or invalid IDs like 'nan'
        if not s_id or s_id.lower() == 'nan':
            continue
            
        # Avoid duplicate database entries
        if not Student.objects.filter(student_id=s_id).exists():
            students_to_create.append(
                Student(
                    student_id=s_id,
                    full_name=s_name,          # Corrected model field name
                    gender=s_gender,            # Added gender field
                    student_class=s_course,     # Corrected model field name
                    course_offered=s_course     # Corrected model field name
                )
            )
            
    if students_to_create:
        Student.objects.bulk_create(students_to_create)
        print(f"✅ Successfully added {len(students_to_create)} new students to the database!")
    else:
        print("ℹ️ No new records to add. They might already exist.")

if __name__ == '__main__':
    load_data()