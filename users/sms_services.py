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
    Normalise a Nigerian number to E.164 (+234XXXXXXXXXX).

    A valid Nigerian mobile is the country code 234 followed by a 10-digit
    subscriber number that starts with a 7/8/9 (e.g. 803..., 703..., 913...).
    Locally people write it as 0803... (11 digits). This strips spaces, dashes,
    and any leading 0 / +234 / 234, then validates the result — returning None
    for anything that isn't a real 10-digit subscriber number, so we never hand
    Africa's Talking an InvalidPhoneNumber.
    """
    if not phone_number:
        return None

    # Keep digits only (drops spaces, dashes, parentheses, leading +).
    digits = "".join(ch for ch in str(phone_number) if ch.isdigit())

    # Peel off whichever country/trunk prefix is present, leaving 10 subscriber digits.
    if digits.startswith("234") and len(digits) == 13:
        subscriber = digits[3:]
    elif digits.startswith("0") and len(digits) == 11:
        subscriber = digits[1:]
    elif len(digits) == 10:
        subscriber = digits
    else:
        return None  # not a recognisable NG mobile

    # Nigerian mobile subscriber numbers start 7, 8, or 9.
    if len(subscriber) != 10 or subscriber[0] not in "789":
        return None

    return "+234" + subscriber

def send_sms(phone_number, code):
    formatted_phone = format_phone_for_sms(phone_number)
    if not formatted_phone:
        logger.error("Rejecting invalid phone number before send: %r", phone_number)
        return False
    
    is_test_mode = getattr(settings, 'AFRICASTALKING_USERNAME', '') == 'sandbox'
    
    if is_test_mode:
        print(f"\n{'='*60}")
        print(f"📱 AFRICA'S TALKING SANDBOX MODE")
        print(f"To: {formatted_phone}")
        print(f"Verification Code: {code}")
        print(f"{'='*60}\n")
        return True
    
    try:
        message = f"Your iSchool verification code is {code}. Valid for 10 minutes, one-time use only."
        
        sender_id = settings.AFRICASTALKING_SENDER_ID.strip() if settings.AFRICASTALKING_SENDER_ID else None
        
        print(f"\n📤 Sending SMS via Africa's Talking...")
        print(f"To: {formatted_phone}")
        print(f"Sender: {sender_id or 'Default'}")
        print(f"Message: {message}")
        
        # Use enqueue parameter to bypass DND
        options = {
            "message": message,
            "recipients": [formatted_phone],
            "enqueue": True  # ✅ This helps bypass DND for transactional messages
        }
        
        if sender_id:
            options["sender_id"] = sender_id
        
        response = sms.send(**options)
        
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
                    reason = f"{status} (code: {recipient.get('statusCode')})"
                    logger.error("SMS rejected by Africa's Talking for %s: %s", formatted_phone, reason)
                    return False
            logger.error("SMS: no recipients in AT response for %s: %s", formatted_phone, response)
        return False

    except Exception as e:
        # Common causes: exhausted AT credit, unregistered/!approved sender ID,
        # invalid API key, or account still in sandbox. Surface it in logs.
        logger.error("SMS send failed for %s: %s", formatted_phone, e, exc_info=True)
        return False
    

def send_sms_auto_fallback(phone_number, code):
    formatted_phone = format_phone_for_sms(phone_number)
    if not formatted_phone:
        logger.error("Rejecting invalid phone number before send: %r", phone_number)
        return False
    
    if getattr(settings, 'AFRICASTALKING_USERNAME', '') == 'sandbox':
        return send_sms(phone_number, code)
    
    try:
        message = f"Your iSchool verification code is {code}. Valid for 10 minutes."
        sender_id = settings.AFRICASTALKING_SENDER_ID.strip() if settings.AFRICASTALKING_SENDER_ID else None
        
        print(f"📤 Sending SMS to {formatted_phone}")
        
        options = {
            "message": message,
            "recipients": [formatted_phone],
            "enqueue": True
        }
        
        if sender_id:
            options["sender_id"] = sender_id
        
        response = sms.send(**options)
        
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