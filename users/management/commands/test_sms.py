"""
Diagnose SMS/OTP delivery.

Prints the exact Africa's Talking config in use, then attempts a real send and
shows the raw provider response — so a failing OTP can be traced to its cause
(sandbox mode, exhausted credit, unapproved sender ID, bad key) without guessing.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from users.sms_services import format_phone_for_sms, send_sms


class Command(BaseCommand):
    help = "Send a test SMS to verify Africa's Talking configuration."

    def add_arguments(self, parser):
        parser.add_argument("phone", help="Recipient phone (e.g. 08031234567)")

    def handle(self, *args, **options):
        phone = options["phone"]
        self.stdout.write("Africa's Talking configuration:")
        self.stdout.write(f"  username : {settings.AFRICASTALKING_USERNAME}")
        self.stdout.write(f"  sender   : {settings.AFRICASTALKING_SENDER_ID or '(default)'}")
        self.stdout.write(f"  api_key  : {'set' if settings.AFRICASTALKING_API_KEY else 'MISSING'}")

        if settings.AFRICASTALKING_USERNAME == "sandbox":
            self.stdout.write(self.style.WARNING(
                "\nUsername is 'sandbox' — real SMS is NOT delivered in sandbox mode. "
                "Set AFRICASTALKING_USERNAME to your live username to send real texts."
            ))

        self.stdout.write(f"\nFormatted number: {format_phone_for_sms(phone)}")
        self.stdout.write("Sending test code 123456 ...")
        ok = send_sms(phone, "123456")
        if ok:
            self.stdout.write(self.style.SUCCESS("Reported success — check the handset."))
        else:
            self.stdout.write(self.style.ERROR(
                "Send failed. Check the logged reason above (credit, sender ID, key)."
            ))
