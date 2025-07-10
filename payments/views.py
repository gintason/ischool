import uuid
import logging
import requests
from django.conf import settings
from django.utils.timezone import now
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from users.models import CustomUser
from users.models import RegistrationGroup  # Adjust to actual app name
from users.utils import assign_main_user_and_slots
from .models import Payment
from .models import PaymentTransaction  # Make sure this exists
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from users.models import CustomUser, CustomUserManager
from password_generator import PasswordGenerator
from emails.sendgrid_email import send_email
import json
from django.core.mail import send_mail
from django.contrib import messages
from datetime import timedelta


pwo = PasswordGenerator()
pwo.minlen = 8
pwo.maxlen = 12
pwo.minuchars = 1
pwo.minlchars = 1
pwo.minnumbers = 1
pwo.minschars = 1

logger = logging.getLogger(__name__)
User = get_user_model()

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_paystack_payment(request):
    tx_ref = request.data.get('transaction_id')

    if not tx_ref:
        return Response({'error': 'Transaction ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    url = f"https://api.paystack.co/transaction/verify/{tx_ref}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        result = response.json()

        if result.get("status") is True:
            data = result.get("data", {})
            metadata = data.get("metadata", {})
            num_slots = int(metadata.get("num_slots", 1))

            payment = Payment.objects.create(
                user=request.user if request.user.is_authenticated else None,
                tx_ref=tx_ref,
                amount=data.get('amount') / 100,  # Convert kobo to Naira
                status=data.get('status'),
                payment_type='paystack',
                paid_at=now(),
                raw_response=result
            )

            assign_main_user_and_slots(user=request.user, num_slots=num_slots)

            return Response({'message': 'Payment verified and slots assigned.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Payment verification failed.', 'details': result}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Verification exception: {e}")
        return Response({'error': f'Verification exception: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def initiate_payment(request):
    data = request.data

    required_fields = ["account_type", "email", "state", "num_slots", "billing_cycle"]
    if not all(data.get(field) for field in required_fields):
        return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

    tx_ref = str(uuid.uuid4())
    num_slots = int(data.get("num_slots", 1))

    billing_cycle = data.get("billing_cycle", "monthly").lower()
    if billing_cycle not in ["monthly", "yearly"]:
        billing_cycle = "monthly"

    slot_price = settings.SLOT_PRICE_MONTHLY if billing_cycle == "monthly" else settings.SLOT_PRICE_YEARLY
    amount = num_slots * slot_price
    amount_in_kobo = int(amount * 100)

    payload = {
        "reference": tx_ref,
        "amount": amount_in_kobo,
        "currency": "NGN",
        "callback_url": "https://api.ischool.ng/payment-verify",  # ✅ Update this in production
        "email": data["email"],
        "metadata": {
            "account_type": data["account_type"],
            "state": data["state"],
            "num_slots": num_slots,
            "billing_cycle": billing_cycle,
            "account_name": data.get("account_name"),
            "account_number": data.get("account_number"),
            "bank": data.get("bank"),
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.paystack.co/transaction/initialize", json=payload, headers=headers)
        result = response.json()
        if result.get("status") is True:
            return Response({
                "payment_link": result["data"]["authorization_url"],
                "tx_ref": tx_ref
            }, status=status.HTTP_200_OK)
        return Response({"error": result.get("message", "Payment initiation failed.")}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Payment initiation error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def verify_and_register(request):
    print("Incoming data:", request.data)
    data = request.data
    transaction_id = data.get("transaction_id")
    tx_ref = data.get("tx_ref")
    email = data.get("email")
    account_type = data.get("account_type")
    state = data.get("state")
    name = data.get("name")
    location = data.get("location")
    slots = int(data.get("slots", 1))
    referral_code = data.get("referral_code", "").strip()
    account_details = data.get("account_details", "").strip()
    student_details = data.get("studentDetails", [])

    if isinstance(student_details, str):
        try:
            student_details = json.loads(student_details)
        except json.JSONDecodeError:
            return Response({"detail": "Invalid format for student details."}, status=status.HTTP_400_BAD_REQUEST)

    if not all([transaction_id, tx_ref, email, account_type, name, location, state]):
        return Response({"detail": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

    if len(student_details) != slots:
        return Response({"detail": "Number of student details does not match the number of slots."},
                        status=status.HTTP_400_BAD_REQUEST)

    if PaymentTransaction.objects.filter(transaction_id=transaction_id).exists():
        return Response({"detail": "Transaction already verified."}, status=status.HTTP_200_OK)

    url = f"https://api.paystack.co/transaction/verify/{transaction_id}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    try:
        res = requests.get(url, headers=headers)
        res_data = res.json()

        logger.info(f"Paystack verification response: {res_data}")

    except Exception as e:
        logger.error(f"Paystack verification failed: {e}")
        return Response({"detail": f"Paystack verification failed: {str(e)}"},
                        status=status.HTTP_502_BAD_GATEWAY)

    if res_data.get("status") is not True:
        logger.error(f"Transaction verification failed. Response: {res_data}")
        return Response({"detail": "Transaction verification failed."}, status=status.HTTP_400_BAD_REQUEST)

    data_info = res_data.get("data", {})
    amount_paid = float(data_info.get("amount", 0)) / 100

    # ✅ Handle billing cycle
    billing_cycle = data.get("billing_cycle", "monthly").lower()
    if billing_cycle not in ["monthly", "yearly"]:
        billing_cycle = "monthly"

    slot_price = settings.SLOT_PRICE_MONTHLY if billing_cycle == "monthly" else settings.SLOT_PRICE_YEARLY
    expected_amount = slots * slot_price

    if amount_paid < expected_amount:
        return Response({"detail": "Amount paid does not match expected slot payment."},
                        status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        group = RegistrationGroup.objects.create(
            account_type=account_type,
            state=state,
            name=name,
            email=email,
            location=location,
            slots_applied=slots,
            slots_remaining=slots,
            referral_code=referral_code if account_type == "referral" else "",
            account_details=account_details if account_type == "referral" else ""
        )

        PaymentTransaction.objects.create(
            registration_group=group,
            transaction_id=transaction_id,
            tx_ref=tx_ref,
            amount=amount_paid,
            verified=True,
            status="successful",
            timestamp=timezone.now()
        )

        created_users = []

    registration_email = request.data.get("email")

    account_type_to_role = {
        "school": "student",
        "home": "student",
        "referral": "student"
    }

    for i, student in enumerate(student_details):
        full_name = student.get("fullName", f"{account_type.capitalize()} User {i+1}")
        student_email = student.get("email")
        if not student_email:
            return Response({"detail": f"Missing email for student {i+1}."}, status=status.HTTP_400_BAD_REQUEST)

        username = f"{account_type[:2].upper()}{timezone.now().strftime('%H%M%S%f')}{i}"
        password = pwo.generate()
        role = account_type_to_role.get(account_type, "student")

        if CustomUser.objects.filter(email=student_email).exists():
            transaction.set_rollback(True)
            return Response(
                {"detail": f"A user with email '{student_email}' already exists. Please use a different email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = CustomUser.objects.create_user(
            email=student_email,
            password=password,
            role=role,
            full_name=full_name,
            username=username,
            registration_group=group
        )

        created_users.append({
            "username": username,
            "password": password,
            "full_name": full_name,
            "email": student_email
        })

    login_details = "\n\n".join(
        f"{user['full_name']} ({user['email']})\nUsername: {user['username']}\nPassword: {user['password']}"
        for user in created_users
    )

    try:
        send_mail(
            subject='Your iSchool Ola Login Details',
            message=f"""Dear User,

Welcome to iSchool Ola! Your registration was successful. Below are the login details for your registered slot(s):

{login_details}

Login here: https://www.ischool.ng/student/login

Best regards,  
iSchool Ola Team
""",
            from_email="noreply@ischool.ng",
            recipient_list=[registration_email],
            fail_silently=False,
        )

    except Exception as e:
        print(f"Error sending email to {registration_email}: {e}")

    return Response({
        "detail": "Registration successful.",
        "users": created_users,
        "group_id": group.id,
        "slots": slots
    }, status=status.HTTP_201_CREATED)
