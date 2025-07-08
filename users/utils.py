from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, StudentSlot

def assign_main_user_and_slots(user, num_slots):
    # Generate a main username (e.g. 001/S001/000 or 001/H001/000)
    state_code = user.state_code or "000"  # you must define how state codes are handled
    prefix = "S" if user.registration_type == "school" else "H"  # example only
    base_username = f"{state_code}/{prefix}{user.id:03}/000"

    user.username = base_username
    user.set_password(base_username)  # User password = username
    user.save()

    # Email the user their main username
    send_mail(
        subject="Your iSchool Ola Login Username",
        message=f"Your account has been created. Username and password: {base_username}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

    # Generate student usernames (e.g. 001/S001/001 to 001/S001/00N)
    for i in range(1, num_slots + 1):
        serial = f"{i:03}"
        student_username = base_username[:-3] + serial

        # Create a StudentSlot object or any model you're using
        StudentSlot.objects.create(
            parent=user,
            student_username=student_username,
            password=student_username  # can be hashed later on login
        )
