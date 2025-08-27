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
import hmac
import hashlib

from django.http import HttpResponseRedirect  # <-- Add this import
from django.views.decorators.csrf import csrf_exempt


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
    num_slots = int(data.get("num_slots", 1))

    # Validate billing cycle
    billing_cycle = data.get("billing_cycle", "monthly").lower()
    if billing_cycle not in ["monthly", "yearly"]:
        billing_cycle = "monthly"

    # Calculate amount
    slot_price = settings.SLOT_PRICE_MONTHLY if billing_cycle == "monthly" else settings.SLOT_PRICE_YEARLY
    amount = num_slots * slot_price
    amount_in_kobo = int(amount * 100)

    base_callback_url = settings.PAYMENT_CALLBACK_URL
     # Ensure the base URL has a trailing slash for consistency
    if not base_callback_url.endswith('/'):
        base_callback_url += '/'
        
    callback_url_with_params = f"{base_callback_url}?reference={tx_ref}&slots={num_slots}"

    payload = {
        "reference": tx_ref,
        "amount": amount_in_kobo,
        "currency": "NGN",
        # ✅ Use the consistent callback URL with parameters
        "callback_url": callback_url_with_params,
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
    logger.info("Request headers: %s", request.headers)

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


logger = logging.getLogger(__name__)



def verify_paystack_signature(payload, expected_signature):
    """
    Verify that the webhook request is actually from Paystack
    """
    secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
    computed_signature = hmac.new(secret, payload, digestmod=hashlib.sha512).hexdigest()
    return hmac.compare_digest(computed_signature, expected_signature or '')


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def payment_callback(request):
    logger.info("Incoming payment callback request: %s", request.method)
    logger.info("Request query parameters: %s", request.GET)

    # Paystack's webhook sends a POST request with the reference in the body
    # The user's browser redirect sends a GET request with the reference in the URL
    if request.method == 'POST':
        # Handle the webhook from Paystack
        try:
            # 🔽 CRITICAL FIX: Read the raw body FIRST before accessing request.data
            raw_body = request.body
            
            # 🔽 Now parse the JSON data
            payload = json.loads(raw_body.decode('utf-8'))
            logger.info("Request data: %s", payload)
            
            # Verify Paystack signature for security
            expected_signature = request.headers.get('x-paystack-signature')
            if not verify_paystack_signature(raw_body, expected_signature):
                logger.warning("Invalid Paystack signature received")
                return JsonResponse({"error": "Invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)
            
            event = payload.get("event")
            if event != "charge.success":
                # We only care about successful charges
                logger.info("Ignoring non-success event: %s", event)
                return JsonResponse({"status": "ignored"}, status=status.HTTP_200_OK)

            reference = payload.get("data", {}).get("reference")
            
            if not reference:
                logger.error("No reference found in Paystack webhook payload")
                return JsonResponse({"error": "No reference provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify payment with Paystack for webhook too
            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            url = f"https://api.paystack.co/transaction/verify/{reference}"

            try:
                res = requests.get(url, headers=headers)
                res.raise_for_status()
                data = res.json()
                logger.info("Paystack verification response: %s", data)
            except requests.exceptions.RequestException as e:
                logger.error("Paystack verification request failed: %s", e)
                return JsonResponse({"error": "Failed to communicate with Paystack."}, status=status.HTTP_502_BAD_GATEWAY)

            # Check if the payment was a success
            if data.get("status") and data["data"].get("status") == "success":
                # For webhook, just log success and return 200
                # The actual account creation will happen when frontend calls verify-and-register
                logger.info(f"Webhook: Payment {reference} verified successfully")
                return JsonResponse({"status": "success"}, status=status.HTTP_200_OK)
            else:
                logger.error(f"Webhook: Payment {reference} failed verification")
                return JsonResponse({"status": "failed"}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook payload")
            return JsonResponse({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except UnicodeDecodeError:
            logger.error("Invalid encoding in request body")
            return JsonResponse({"error": "Invalid encoding"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        # Handle the browser redirect from Paystack
        logger.info("Request data: %s", request.GET)  # For GET, data is in query params
        
        reference = request.GET.get('reference')
        slots = request.GET.get('slots')

        # The slots parameter is crucial, so we should handle its absence gracefully
        if not slots:
            slots_to_pass = "1"  # Default to 1 slot if not provided, or handle as an error
            logger.warning("Slots parameter missing from GET request. Defaulting to 1.")
        else:
            slots_to_pass = slots

        if not reference:
            logger.error("No transaction reference found in GET request.")
            return JsonResponse({"error": "No transaction reference found."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify payment with Paystack
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        url = f"https://api.paystack.co/transaction/verify/{reference}"

        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            data = res.json()
            logger.info("Paystack verification response: %s", data)
        except requests.exceptions.RequestException as e:
            logger.error("Paystack verification request failed: %s", e)
            return JsonResponse({"error": "Failed to communicate with Paystack."}, status=status.HTTP_502_BAD_GATEWAY)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid response from Paystack."}, status=status.HTTP_502_BAD_GATEWAY)

        # Check if the payment was a success
        if data.get("status") and data["data"].get("status") == "success":
            # Use HTML meta refresh to redirect to the app
            redirect_url = f"ischoolmobile://payment-callback?reference={reference}&slots={slots_to_pass}&status=success"
            html_content = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8">
                    <title>Redirecting to App</title>
                    <meta http-equiv="refresh" content="0; url={redirect_url}">
                </head>
                <body>
                    <p>Payment successful! <a href="{redirect_url}">Click here</a> to return to the app.</p>
                    <script>
                        window.location.href = "{redirect_url}";
                    </script>
                </body>
            </html>
            """
            return HttpResponse(html_content, content_type="text/html")
        else:
            # Payment failed or was not successful
            logger.error("Paystack transaction was not successful. Status: %s", data.get("data", {}).get("status"))
            redirect_url = f"ischoolmobile://payment-callback?reference={reference}&status=failed"
            html_content = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8">
                    <title>Redirecting to App</title>
                    <meta http-equiv="refresh" content="0; url={redirect_url}">
                </head>
                <body>
                    <p>Payment failed! <a href="{redirect_url}">Click here</a> to return to the app.</p>
                    <script>
                        window.location.href = "{redirect_url}";
                    </script>
                </body>
            </html>
            """
            return HttpResponse(html_content, content_type="text/html")
    
    # Return a 405 for any other method
    return JsonResponse({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)