import os
import pandas as pd
import qrcode

def generate_all_qrcodes():
    excel_file_path = 'student_attendance_dataset.csv.xlsx'
    output_folder = 'student_qr_codes'
    
    if not os.path.exists(excel_file_path):
        print(f"❌ Error: Could not find '{excel_file_path}'")
        return

    # Create a clean folder to store the QR code images safely
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("Reading dataset columns...")
    df = pd.read_excel(excel_file_path)
    
    # Standardize headers to match our flexible import rules
    df.columns = [str(col).strip().lower() for col in df.columns]
    id_col = next((c for c in df.columns if 'id' in c), None)
    
    if not id_col:
        print("❌ Error: Could not find a Student ID column.")
        return

    print(f"Generating QR codes for {len(df)} records... Please wait.")
    
    # Track performance intervals
    counter = 0
    
    for index, row in df.iterrows():
        student_id = str(row[id_col]).strip()
        
        # Skip empty rows if any exist
        if not student_id or student_id.lower() == 'nan':
            continue
            
        # Configure static text data embedded into the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(student_id)
        qr.make(fit=True)
        
        # Create and save image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(os.path.join(output_folder, f"{student_id}.png"))
        
        counter += 1
        if counter % 2000 == 0:
            print(f"Progress: {counter} QR codes generated...")

    print(f"✅ Successfully created {counter} static QR code images in the '{output_folder}' directory!")

if __name__ == '__main__':
    generate_all_qrcodes()