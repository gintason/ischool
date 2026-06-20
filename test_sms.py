import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iSchool_Ola.settings')
django.setup()

from users.sms_services import send_sms, format_phone_for_sms

# Test with your phone number
test_phone = "07030673089"  # Replace with your actual phone
test_code = "123456"

print(f"Formatted phone: {format_phone_for_sms(test_phone)}")
result = send_sms(test_phone, test_code)
print(f"SMS sent: {result}")