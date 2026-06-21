# users/sms_service.py
import africastalking
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Initialize Africa's Talking
africastalking.initialize(
    username=settings.AFRICASTALKING_USERNAME,
    api_key=settings.AFRICASTALKING_API_KEY
)

# Get the SMS service
sms = africastalking.SMS

def format_phone_for_sms(phone_number):
    """
    Format phone number for Africa's Talking (international format)
    Input: 07030673089 or 2347030673089
    Output: +2347030673089
    """
    # Remove any whitespace
    phone_number = phone_number.strip()
    
    # If starts with '0' (local format)
    if phone_number.startswith('0') and len(phone_number) == 11:
        return '+234' + phone_number[1:]
    
    # If starts with '234'
    if phone_number.startswith('234') and len(phone_number) >= 13:
        return '+' + phone_number
    
    # If already has '+'
    if phone_number.startswith('+'):
        return phone_number
    
    # If just the number without country code (10 digits)
    if len(phone_number) == 10:
        return '+234' + phone_number
    
    # Default: just add '+'
    return '+' + phone_number

def send_sms(phone_number, code):
    formatted_phone = format_phone_for_sms(phone_number)
    
    is_test_mode = getattr(settings, 'AFRICASTALKING_USERNAME', '') == 'sandbox'
    
    if is_test_mode:
        print(f"\n{'='*60}")
        print(f"📱 AFRICA'S TALKING SANDBOX MODE")
        print(f"To: {formatted_phone}")
        print(f"Verification Code: {code}")
        print(f"Message: Your iSchool verification code is {code}. Valid for 10 minutes, one-time use only.")
        print(f"{'='*60}\n")
        logger.info(f"TEST MODE: SMS to {formatted_phone} with code: {code}")
        return True
    
    try:
        message = f"Your iSchool verification code is {code}. Valid for 10 minutes, one-time use only."
        
        # Use sender_id only if it's not empty
        sender_id = settings.AFRICASTALKING_SENDER_ID.strip() if settings.AFRICASTALKING_SENDER_ID else None
        
        print(f"\n📤 Sending SMS via Africa's Talking...")
        print(f"To: {formatted_phone}")
        print(f"Sender: {sender_id or 'Default'}")
        print(f"Message: {message}")
        
        # Send SMS - pass sender_id only if it has a value
        if sender_id:
            response = sms.send(
                message=message,
                recipients=[formatted_phone],
                sender_id=sender_id
            )
        else:
            response = sms.send(
                message=message,
                recipients=[formatted_phone]
            )
        
        print(f"Response: {response}")
        logger.info(f"SMS sent to {formatted_phone}: {response}")
        
        if response and isinstance(response, dict):
            recipients = response.get('SMSMessageData', {}).get('Recipients', [])
            if recipients:
                recipient = recipients[0]
                status = recipient.get('status')
                if status == 'Success':
                    message_id = recipient.get('messageId')
                    print(f"✅ SMS sent successfully! Message ID: {message_id}")
                    return True
                else:
                    print(f"❌ SMS failed with status: {status}")
                    return False
        
        return False
            
    except Exception as e:
        print(f"❌ SMS Error: {e}")
        return False


def send_sms_auto_fallback(phone_number, code):
    formatted_phone = format_phone_for_sms(phone_number)
    
    if getattr(settings, 'AFRICASTALKING_USERNAME', '') == 'sandbox':
        return send_sms(phone_number, code)
    
    try:
        message = f"Your iSchool verification code is {code}. Valid for 10 minutes."
        sender_id = settings.AFRICASTALKING_SENDER_ID.strip() if settings.AFRICASTALKING_SENDER_ID else None
        
        print(f"📤 Sending SMS to {formatted_phone}")
        
        if sender_id:
            response = sms.send(
                message=message,
                recipients=[formatted_phone],
                sender_id=sender_id
            )
        else:
            response = sms.send(
                message=message,
                recipients=[formatted_phone]
            )
        
        print(f"📨 API Response: {response}")
        
        if response and isinstance(response, dict):
            recipients = response.get('SMSMessageData', {}).get('Recipients', [])
            if recipients:
                status = recipients[0].get('status')
                if status == 'Success':
                    return True
        
        return False
        
    except Exception as e:
        print(f"❌ SMS Error: {e}")
        return False