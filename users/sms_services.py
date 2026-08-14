# users/sms_services.py
import logging
import threading

import africastalking
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

AT_USERNAME = getattr(settings, 'AFRICASTALKING_USERNAME', '')
AT_API_KEY = getattr(settings, 'AFRICASTALKING_API_KEY', '')

if AT_USERNAME and AT_API_KEY:
    africastalking.initialize(
        username=AT_USERNAME,
        api_key=AT_API_KEY,
    )
    sms = africastalking.SMS
else:
    sms = None
    logger.warning("Africa's Talking credentials are not configured.")


def format_phone_for_sms(phone_number):
    """
    Normalize Nigerian mobile numbers to E.164: +234XXXXXXXXXX.
    Accepts 08031234567, 8031234567, 2348031234567, or +2348031234567.
    """
    if not phone_number:
        return None

    digits = ''.join(char for char in str(phone_number) if char.isdigit())

    if digits.startswith('234') and len(digits) == 13:
        subscriber = digits[3:]
    elif digits.startswith('0') and len(digits) == 11:
        subscriber = digits[1:]
    elif len(digits) == 10:
        subscriber = digits
    else:
        return None

    if len(subscriber) != 10 or subscriber[0] not in '789':
        return None

    return '+234' + subscriber


def send_sms(phone_number, code):
    formatted_phone = format_phone_for_sms(phone_number)

    if not formatted_phone:
        logger.error('Invalid phone number for SMS: %r', phone_number)
        return False

    if not sms:
        logger.error("Africa's Talking SMS service is unavailable.")
        return False

    if AT_USERNAME == 'sandbox':
        logger.debug('Sandbox SMS to %s: code %s', formatted_phone, code)
        return True

    sender_id = str(
        getattr(settings, 'AFRICASTALKING_SENDER_ID', '') or ''
    ).strip()

    options = {
        'message': (
            'Your iSchool verification code is '
            + str(code)
            + '. Valid for 10 minutes, one-time use only.'
        ),
        'recipients': [formatted_phone],
        'enqueue': True,
    }

    if sender_id:
        options['sender_id'] = sender_id

    try:
        logger.info("Sending SMS via Africa's Talking to %s", formatted_phone)
        response = sms.send(**options)

        recipients = (
            response.get('SMSMessageData', {}).get('Recipients', [])
            if isinstance(response, dict)
            else []
        )

        if not recipients:
            logger.error(
                "Africa's Talking returned no recipient result for %s: %s",
                formatted_phone,
                response,
            )
            return False

        recipient = recipients[0]
        status = recipient.get('status')

        if status == 'Success':
            logger.info(
                'SMS accepted for %s, message id=%s',
                formatted_phone,
                recipient.get('messageId'),
            )
            return True

        logger.error(
            'SMS rejected for %s: %s (code: %s)',
            formatted_phone,
            status,
            recipient.get('statusCode'),
        )
        return False

    except Exception:
        logger.exception("Africa's Talking SMS send failed for %s", formatted_phone)
        return False


def send_sms_auto_fallback(phone_number, code):
    """
    Kept because the OTP view calls this function.
    Add another provider here later if you need a real SMS fallback.
    """
    return send_sms(phone_number, code)


def _send_otp_email_in_background(subject, message, recipient):
    """
    Uses the same Django SMTP mechanism as VerifyOleStudentPaymentView.
    Runs in a daemon thread so SMTP cannot block the OTP API request.
    """
    try:
        sent_count = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )

        if sent_count == 1:
            logger.info('OTP email sent to %s', recipient)
        else:
            logger.error(
                'SMTP accepted no OTP email for %s; send_mail returned %s',
                recipient,
                sent_count,
            )
    except Exception:
        logger.exception('OTP email send failed for %s', recipient)


def send_email_code(email, code):
    """
    Queue an email OTP using the existing iSchool SMTP configuration.

    True means the email was successfully queued in a background thread.
    The actual SMTP result is recorded in the Render logs.
    """
    email = str(email or '').strip().lower()

    if not email:
        logger.error('Cannot send OTP email: empty recipient.')
        return False

    subject = 'Your iSchool verification code'
    message = (
        'Hello,\n\n'
        'Your iSchool verification code is: '
        + str(code)
        + '\n\n'
        'This code expires in 10 minutes and can only be used once.\n\n'
        'If you did not request this code, you can ignore this email.\n\n'
        'Regards,\n'
        'iSchool Team'
    )

    try:
        threading.Thread(
            target=_send_otp_email_in_background,
            args=(subject, message, email),
            daemon=True,
        ).start()

        logger.info('OTP email queued for %s', email)
        return True
    except Exception:
        logger.exception('Could not queue OTP email for %s', email)
        return False