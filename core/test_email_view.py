from django.core.mail import send_mail
from django.http import JsonResponse

def test_email(request):
    try:
        sent = send_mail(
            subject='✅ Django SMTP Test',
            message='Hey Gintason, this is a real test email from your backend 🎉',
            from_email='noreply@ischool.ng',
            recipient_list=['gintason@gmail.com'],
            fail_silently=False,
        )
        return JsonResponse({"status": "success", "sent": sent})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


