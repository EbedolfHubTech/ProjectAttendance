import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

application = get_wsgi_application()

# Automatically run migrations every time Render starts/deploys the app
try:
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Auto-migration error: {e}")