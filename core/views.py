from rest_framework import viewsets
from .models import RegistrationSource, StudentSlot, ContactOleMessage, ContactOla
from .serializers import RegistrationSourceSerializer, StudentSlotSerializer
from emails.sendgrid_email import send_email
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import ContactOleMessageSerializer, ContactOlaSerializer
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.shortcuts import render

class RegistrationSourceViewSet(viewsets.ModelViewSet):
    queryset = RegistrationSource.objects.all()
    serializer_class = RegistrationSourceSerializer


class StudentSlotViewSet(viewsets.ModelViewSet):
    queryset = StudentSlot.objects.all()
    serializer_class = StudentSlotSerializer


# myapp/views.py

def my_view(request):
    response = send_email(
        subject="Welcome to iSchool Ola",
        content="Thanks for joining our platform!",
        to_email="gintason@gmail.com"
    )
    print(response)

    

def test_email_view(request):
    result = send_email(
        subject="Test Email from iSchool Ola",
        content="This is a test email sent via SendGrid Web API.",
        to_email="gintason@gmail.com"  # replace with your own email
    )
    return JsonResponse(result)



class ContactOleMessageAPIView(APIView):
    def post(self, request):
        serializer = ContactOleMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Message sent successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def ole_contact_submission(request):
    serializer = ContactOleMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        full_name = serializer.validated_data.get("full_name")
        email = serializer.validated_data.get("email")
        message = serializer.validated_data.get("message")

        # Initialize SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

        # ✅ Admin Notification Email
        admin_email = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=settings.CONTACT_EMAIL,
            subject=f"New Contact Message from {full_name} (Ole)",
            plain_text_content=f"""
A new contact form message was submitted on iSchool Ole:

Full Name: {full_name}
Email: {email}

Message:
{message}
""",
        )
        sg.send(admin_email)

        # ✅ Confirmation Email to Sender
        confirmation_email = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=email,
            subject="Thanks for contacting iSchool Ole!",
            plain_text_content=f"""
Hi {full_name},

Thank you for reaching out to iSchool Ole! We’ve received your message and will respond shortly.

Here’s a copy of your message:
------------------------
{message}
------------------------

Need urgent help? Call or WhatsApp us at +234 902 765 4321.

Best regards,  
iSchool Ole Team
""",
        )
        sg.send(confirmation_email)

        return Response(
            {"message": "Message sent and confirmation email delivered."},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def ola_contact_view(request):
    serializer = ContactOlaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        # Send confirmation email
        message = Mail(
            from_email='no-reply@ischool.ng',
            to_emails=serializer.validated_data['email'],
            subject='Thanks for Contacting iSchool Ola!',
            html_content=f"""
                <p>Dear {serializer.validated_data['full_name']},</p>
                <p>Thank you for reaching out to iSchool Ola. We have received your message and will get back to you shortly.</p>
                <p><strong>Your Message:</strong><br>{serializer.validated_data['message']}</p>
                <br><p>Best regards,<br>The iSchool Ola Team</p>
            """
        )

        try:
            sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            print("SendGrid Error:", e)

        return Response({"detail": "Message submitted successfully."}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def frontend(request):
    return render(request, "index.html")  # Replace with the correct path