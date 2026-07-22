import os
import sqlite3
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

application = get_wsgi_application()

# 1. Auto-detect outdated SQLite database on Render and reset it if missing 'full_name'
db_path = settings.DATABASES['default']['NAME']
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(attendance_app_student)")
        columns = [column[1] for column in cursor.fetchall()]
        conn.close()

        if columns and 'full_name' not in columns:
            os.remove(db_path)
            print("Outdated database file detected and removed.")
    except Exception as e:
        print(f"Database check notice: {e}")

# 2. Run migrations
try:
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Auto-migration error: {e}")

# 3. Create default admin superuser automatically if it doesn't exist
try:
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
        print("Superuser 'admin' created successfully.")
except Exception as e:
    print(f"Superuser creation error: {e}")