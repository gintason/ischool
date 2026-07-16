from django.core.mail import send_mail
from django.conf import settings

from .models import CustomUser, StudentSlot
from .serializers import generate_secure_password


def assign_main_user_and_slots(user, num_slots):
    """
    Give the paying user their login credentials and create their student slots.

    NOTE: this previously referenced StudentSlot fields that don't exist
    (`parent`, `student_username`), so it raised TypeError on every call — the
    exception was swallowed by the caller's try/except and surfaced as a generic
    500 after payment. Fields corrected to the real model, and passwords are now
    random (never equal to the username).
    """
    state_code = getattr(user, "state_code", None) or "000"
    prefix = "S" if getattr(user, "registration_type", None) == "school" else "H"
    base_username = f"{state_code}/{prefix}{user.id:03}/000"

    # Give the main account a real, random password and email it once.
    raw_password = generate_secure_password()
    user.username = base_username
    user.set_password(raw_password)
    user.save()

    send_mail(
        subject="Your iSchool Ola Login Details",
        message=(
            f"Hello {user.full_name},\n\n"
            f"Your account is ready.\n\n"
            f"Username: {base_username}\n"
            f"Password: {raw_password}\n\n"
            f"Please keep these safe.\n\niSchool Ola Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    # Create the student slots (bookkeeping only — not login accounts, so no
    # usable password is stored on them).
    for i in range(1, num_slots + 1):
        serial = f"{i:03}"
        student_username = base_username[:-3] + serial
        StudentSlot.objects.create(
            main_user=user,
            full_name=user.full_name,
            email=user.email,
            username=student_username,
            password="",
        )
