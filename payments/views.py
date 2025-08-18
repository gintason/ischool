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
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponse
from django.http import JsonResponse


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

    required_fields = ["account_type", "email", "state", "num_slots", "billing_cycle", "callback_url"]
    if not all(data.get(field) for field in required_fields):
        return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

    # Generate a unique transaction reference
    tx_ref = str(uuid.uuid4())
    num_slots = int(data.get("num_slots", 1))  # ✅ keep this as your slots variable

    # Validate billing cycle
    billing_cycle = data.get("billing_cycle", "monthly").lower()
    if billing_cycle not in ["monthly", "yearly"]:
        billing_cycle = "monthly"

    # Calculate amount
    slot_price = settings.SLOT_PRICE_MONTHLY if billing_cycle == "monthly" else settings.SLOT_PRICE_YEARLY
    amount = num_slots * slot_price
    amount_in_kobo = int(amount * 100)

    # ✅ Step 3 Integration: Append transaction_id & slots to callback_url
    callback_url = f"{data['callback_url']}?transaction_id={tx_ref}&slots={num_slots}"

    payload = {
        "reference": tx_ref,
        "amount": amount_in_kobo,
        "currency": "NGN",
        # ✅ use num_slots here instead of undefined slots
        "callback_url": f"https://api.ischool.ng/api/payments/payment-callback/?slots={num_slots}",
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
            # ✅ Add initiation_data for mobile apps without affecting web
            return Response({
                "payment_link": result["data"]["authorization_url"],
                "tx_ref": tx_ref,
                "initiation_data": {
                    "transaction_id": tx_ref,
                    "tx_ref": tx_ref,
                    "email": data["email"],
                    "account_type": data["account_type"],
                    "name": data.get("name"),
                    "location": data.get("location"),
                    "state": data["state"],
                    "slots": num_slots,
                    "billing_cycle": billing_cycle,
                    "referral_code": data.get("referral_code", ""),
                    "account_details": data.get("account_details", ""),
                    "studentDetails": data.get("studentDetails", []),
                }
            }, status=status.HTTP_200_OK)

        return Response({"error": result.get("message", "Payment initiation failed.")}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Payment initiation error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def verify_and_register(request):
    logger.info("Incoming payment verification request: %s", request.data)

    data = request.data

    # Extract fields
    transaction_id = data.get("transaction_id")  # This should match Paystack's reference
    tx_ref = data.get("tx_ref") or transaction_id
    email = data.get("email")
    account_type = data.get("account_type")
    state = data.get("state")
    name = data.get("name")
    location = data.get("location")
    slots = int(data.get("slots", 1))
    referral_code = (data.get("referral_code") or "").strip()
    account_details = (data.get("account_details") or "").strip()
    billing_cycle = data.get("billing_cycle", "monthly").lower()
    student_details = data.get("studentDetails", [])

    # Parse student details if string
    if isinstance(student_details, str):
        try:
            student_details = json.loads(student_details)
        except json.JSONDecodeError:
            return Response({"detail": "Invalid format for student details."}, status=status.HTTP_400_BAD_REQUEST)

    # Required fields check
    required_fields = ["transaction_id", "tx_ref", "email", "account_type", "name", "location", "state"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return Response({"detail": f"Missing required fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

    # Slot count validation
    if len(student_details) != slots:
        return Response({"detail": "Number of student details does not match the number of slots."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Prevent duplicate verification
    if PaymentTransaction.objects.filter(transaction_id=transaction_id).exists():
        return Response({"detail": "Transaction already verified."}, status=status.HTTP_200_OK)

    # Verify with Paystack
    paystack_url = f"https://api.paystack.co/transaction/verify/{transaction_id}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    try:
        res = requests.get(paystack_url, headers=headers)
        res_data = res.json()
        logger.info("Paystack verification response: %s", res_data)
    except Exception as e:
        logger.error("Paystack verification failed: %s", e)
        return Response({"detail": f"Paystack verification failed: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

    if not res_data.get("status"):
        return Response({"detail": "Transaction verification failed."}, status=status.HTTP_400_BAD_REQUEST)

    # Amount check
    amount_paid = float(res_data.get("data", {}).get("amount", 0)) / 100
    if billing_cycle not in ["monthly", "yearly"]:
        billing_cycle = "monthly"

    slot_price = settings.SLOT_PRICE_MONTHLY if billing_cycle == "monthly" else settings.SLOT_PRICE_YEARLY
    expected_amount = slots * slot_price

    if amount_paid < expected_amount:
        return Response({"detail": "Amount paid does not match expected slot payment."}, status=status.HTTP_400_BAD_REQUEST)

    # Create group and users atomically
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
        account_type_to_role = {"school": "student", "home": "student", "referral": "student"}

        for i, student in enumerate(student_details):
            full_name = student.get("fullName", f"{account_type.capitalize()} User {i+1}")
            student_email = student.get("email")

            if not student_email:
                transaction.set_rollback(True)
                return Response({"detail": f"Missing email for student {i+1}."}, status=status.HTTP_400_BAD_REQUEST)

            if CustomUser.objects.filter(email=student_email).exists():
                transaction.set_rollback(True)
                return Response({"detail": f"A user with email '{student_email}' already exists. Please use a different email."},
                                status=status.HTTP_400_BAD_REQUEST)

            username = f"{account_type[:2].upper()}{timezone.now().strftime('%H%M%S%f')}{i}"
            password = pwo.generate()
            role = account_type_to_role.get(account_type, "student")

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

    # Send login details email
    login_details = "\n\n".join(
        f"{u['full_name']} ({u['email']})\nUsername: {u['username']}\nPassword: {u['password']}"
        for u in created_users
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
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error("Error sending email to %s: %s", email, e)

    return Response({
        "detail": "Registration successful.",
        "users": created_users,
        "group_id": group.id,
        "slots": slots
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def payment_callback(request):
    reference = request.GET.get('reference')
    slots = request.GET.get('slots')

    if not reference:
        return JsonResponse({"error": "No transaction reference found."}, status=400)

    # Verify payment with Paystack
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    res = requests.get(url, headers=headers)
    data = res.json()

    if data.get("status") and data["data"]["status"] == "success":
        # Redirect user to mobile/web frontend
        return redirect(f"ischoolmobile://payment-success?slots={slots}&reference={reference}")
    else:
        return redirect(f"ischoolmobile://payment-failed?reference={reference}")
