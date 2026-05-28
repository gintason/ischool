# users/sms_service.py
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def format_phone_for_sms(phone_number):
    """
    Format phone number for SMS sending
    Input: 2347030673089
    Output: 7030673089 (for Termii)
    """
    if phone_number.startswith('234'):
        return phone_number[3:]
    return phone_number

def send_sms(phone_number, code):
    """
    Send SMS using Termii API with DND compliance
    """
    formatted_phone = format_phone_for_sms(phone_number)
    
    # Check if we're in test mode
    is_test_mode = getattr(settings, 'TERMII_TEST_MODE', False)
    
    if is_test_mode:
        print(f"\n{'='*60}")
        print(f"📱 TERMII TEST MODE ACTIVE")
        print(f"To: {formatted_phone}")
        print(f"Verification Code: {code}")
        print(f"Message: Your iSchool verification code is {code}. Valid for 10 minutes, one-time use only.")
        print(f"{'='*60}\n")
        return True
    
    try:
        # DND-compliant message format
        # Requirements met:
        # 1. Company name: iSchool
        # 2. Verification code (not OTP code)
        # 3. Expiry time
        # 4. One-time use notice
        message = f"Your iSchool verification code is {code}. Valid for 10 minutes, one-time use only."
        
        payload = {
            'to': formatted_phone,
            'from': 'N-Alert',  # Termii's default DND ID
            'sms': message,
            'type': 'plain',
            'channel': 'dnd',  # DND channel for transactional messages
            'api_key': settings.TERMII_API_KEY,
        }
        
        print(f"\n📤 Sending DND-compliant SMS via Termii...")
        print(f"To: {formatted_phone}")
        print(f"Sender: N-Alert")
        print(f"Message: {message}")
        
        response = requests.post(
            'https://api.ng.termii.com/api/sms/send',
            json=payload,
            timeout=10
        )
        
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('message_id'):
            print(f"✅ SMS sent successfully via DND channel")
            return True
        else:
            print(f"⚠️ SMS sending failed: {response_data}")
            return False
            
    except Exception as e:
        print(f"❌ SMS Error: {e}")
        return False