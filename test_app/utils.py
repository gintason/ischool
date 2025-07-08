from difflib import SequenceMatcher
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import os


def calculate_theory_score(answer, expected):
    ratio = SequenceMatcher(None, answer.lower(), expected.lower()).ratio()
    return round(ratio * 100, 2)  # percentage match

def send_test_result_email(user, test_session, mcq_details, theory_details):
    subject = f"Your Test Results – {test_session.subject}"
    context = {
        "full_name": user.full_name,
        "test_time": test_session.created_at.strftime("%Y-%m-%d %H:%M"),
        "mcq_details": mcq_details,
        "theory_details": theory_details,
    }
    message = render_to_string("emails/test_result.txt", context)

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

