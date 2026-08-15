from django.utils.crypto import get_random_string
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
import re
from .sms_services import send_email_code, send_sms_auto_fallback
from .serializers import (UserRegistrationSerializer, 
                          CustomTokenObtainPairSerializer, OleStudentRegistrationSerializer, 
                          OleStudentDashboardSerializer)
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import RegistrationGroup, OlePaymentVerification
from .permissions import  IsTeacherUser, IsStudentUser, IsParentUser, IsAdminUser, IsOleStudentUser
from .serializers import CustomUserSerializer 
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import StudentSlot
from .serializers import StudentSlotSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.conf import settings
from dj_rest_auth.views import LoginView
from emails.sendgrid_email import send_email
from datetime import timedelta
from .models import OleStudentSubjectAccess, AdminActionLog
from django.utils import timezone
from users.models import OleStudentSubscription, OleStudentProfile, SubscriptionPlan
from .serializers import OleStudentProfileSerializer
from rest_framework.authentication import TokenAuthentication
import requests
from teachers.models import OleClassLevel, OleSubject, OleStudentMatch, LiveClassSchedule, OleMaterial, OleLesson, AttendanceLog
from django.shortcuts import get_object_or_404
from .serializers import (
    UserRegistrationSerializer,
    MyTokenObtainPairSerializer, LiveClassScheduleDetailSerializer, LessonHistorySerializer, OleMaterialSerializer
)
import json
import re
import random
import uuid
import string
from django.db import IntegrityError  # Make sure this is imported at the top
from django.core.mail import send_mail
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .sms_services import send_sms
import logging
import threading
from django.core.cache import cache
from django.http import JsonResponse
from .models import VerificationCode
from rest_framework.throttling import AnonRateThrottle
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

User = get_user_model()


logger = logging.getLogger(__name__)

from rest_framework.throttling import SimpleRateThrottle, AnonRateThrottle
from rest_framework.decorators import throttle_classes


class OTPRateThrottle(AnonRateThrottle):
    """Tight limit on OTP sends — each SMS costs money and codes are guessable."""
    scope = "otp"


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class RegisterRateThrottle(AnonRateThrottle):
    scope = "register"




def generate_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

from users.models import CustomUser  # adjust import as needed

User = get_user_model()
username = f"ole_{uuid.uuid4().hex[:8]}"

# User Registration View
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "User registered successfully.",
                "data": CustomUserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
   

# Token Authentication View (Login)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]

# Registration Group Creation (For Schools/Homes/Referrals)
class RegistrationGroupView(APIView):
    permission_classes = [IsAdminUser]  # Only admins can create groups

    def post(self, request):
        group_type = request.data.get('group_type')
        state = request.data.get('state')
        slots_applied = request.data.get('slots_applied')
        proof_of_payment = request.data.get('proof_of_payment')

        # Create a new registration group
        group = RegistrationGroup.objects.create(
            group_type=group_type,
            state=state,
            slots_applied=slots_applied,
            slots_remaining=slots_applied,  # Initial remaining slots set to slots applied
            proof_of_payment=proof_of_payment,
        )

        return Response({"message": f"{group_type.capitalize()} registered successfully", "group_id": group.id}, status=status.HTTP_201_CREATED)

# Example of Teacher View
class TeacherTestManagementView(APIView):
    permission_classes = [IsTeacherUser]  # Only teachers can manage tests

    def get(self, request):
        # Example action: Get tests assigned to the teacher
        # Logic for getting tests goes here
        return Response({"message": "Tests for Teacher"}, status=status.HTTP_200_OK)

# Example of Student View
class StudentResultsView(APIView):
    permission_classes = [IsStudentUser]  # Only students can view their results

    def get(self, request):
        # Example action: Get student's results
        # Logic for getting results goes here
        return Response({"message": "Student results"}, status=status.HTTP_200_OK)
    


class StudentLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate using username
        try:
            user_obj = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user_obj.email, password=password)  # using email internally

        if user is not None:
            if user.role.lower() != "student":
                return Response({"error": "User is not a student."}, status=status.HTTP_403_FORBIDDEN)

            # ✅ Check subscription status
            if user.registration_group and not user.registration_group.is_subscription_active():
                return Response(
                    {"detail": "Your subscription has expired. Please buy slots again to continue."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # ✅ Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.role,
                "user_id": user.id
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_student_slots(request):
    data = request.data.get('students', [])
    created_slots = []

    # Prefix example: 001/S001/
    user_prefix = request.user.username[:-3]  # remove last 3 digits

    current_count = StudentSlot.objects.filter(main_user=request.user).count()

    for index, student in enumerate(data):
        serial_number = str(current_count + index + 1).zfill(3)
        username = f"{user_prefix}{serial_number}"
        slot = StudentSlot.objects.create(
            main_user=request.user,
            full_name=student.get('full_name'),
            email=student.get('email'),
            username=username,
            # StudentSlot is bookkeeping only — it is NOT a login account (those
            # are CustomUser, hashed). No usable password is stored here.
            password="",
        )
        created_slots.append(StudentSlotSerializer(slot).data)

    return Response({'slots': created_slots}, status=status.HTTP_201_CREATED)


class AdminOnlyView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Hello Admin!"})


class TeacherOnlyView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Hello Teacher!"})


# 1. Student Registration View
class StudentRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


# 2. Custom JWT Login View
class CustomLoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)



class OleStudentRegistrationView(APIView):
    throttle_classes = [RegisterRateThrottle]
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("OLE Registration Request Data: %s", request.data)

        data = request.data

        # ---------- Manual extraction & validation ----------
        email = str(data.get("email", "")).strip().lower()
        full_name = str(data.get("full_name", "")).strip()
        plan_type = str(data.get("plan_type", "monthly")).strip().lower()
        class_level_id_raw = data.get("class_level_id")
        subject_ids_raw = data.get("subject_ids")

        errors = {}

        # Email validation
        if not email:
            errors["email"] = "Email is required."
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors["email"] = "Enter a valid email address."

        # Full name
        if not full_name:
            errors["full_name"] = "Full name is required."

        # Plan type
        allowed_plan_types = {"monthly", "yearly"}
        if plan_type not in allowed_plan_types:
            errors["plan_type"] = f"Plan type must be one of: {', '.join(allowed_plan_types)}."

        # Class level ID
        try:
            class_level_id = int(class_level_id_raw)
        except (TypeError, ValueError):
            errors["class_level_id"] = "Class level ID must be a valid integer."
            class_level_id = None

        # Subject IDs
        if subject_ids_raw is None:
            subject_ids = []
        elif isinstance(subject_ids_raw, list):
            subject_ids = subject_ids_raw
        elif isinstance(subject_ids_raw, str):
            # Try JSON parsing first
            try:
                subject_ids = json.loads(subject_ids_raw)
                if not isinstance(subject_ids, list):
                    raise ValueError("Not a list")
            except (json.JSONDecodeError, ValueError):
                # Fallback: split by comma
                subject_ids = [s.strip() for s in subject_ids_raw.split(",") if s.strip()]
        else:
            # Single value → wrap in list
            subject_ids = [subject_ids_raw]

        # Convert subject IDs to integers, ignore invalid
        try:
            subject_ids = [int(s) for s in subject_ids]
        except (TypeError, ValueError):
            errors["subject_ids"] = "Subject IDs must be a list of integers."
            subject_ids = []

        if not subject_ids:
            errors["subject_ids"] = "At least one subject ID is required."

        # If any errors, return 400
        if errors:
            logger.error("OLE Registration validation errors: %s", errors)
            return Response({"detail": errors}, status=status.HTTP_400_BAD_REQUEST)

        # ---------- Continue with original logic ----------
        AdminActionLog.objects.create(
            action_type="registration_attempt",
            email=email,
            details=f"Attempting registration with plan: {plan_type}, class_level_id: {class_level_id}",
        )

        try:
            class_level = OleClassLevel.objects.get(id=class_level_id)
            subjects = OleSubject.objects.filter(id__in=subject_ids)
            if not subjects.exists():
                return Response({"detail": "Invalid subject selection."}, status=400)
        except OleClassLevel.DoesNotExist:
            return Response({"detail": "Invalid class level selected."}, status=400)

        # OLE currently offers the monthly plan only.
        plan_id = settings.PAYSTACK_PLAN_IDS.get("monthly")
        amount = settings.PAYSTACK_PLAN_AMOUNTS.get("monthly")

        if not plan_id or not amount:
            logger.error(
                "OLE plan misconfigured: plan_id=%r amount=%r",
                plan_id, amount,
            )
            return Response(
                {"error": "Subscription plan is not configured. Please contact support."},
                status=500,
            )

        is_mobile = request.data.get("is_mobile", False)
        if is_mobile:
            callback_url = "https://api.ischool.ng/api/payments/payment-callback/?ole=true"
        else:
            callback_url = settings.OLE_PAYMENT_CALLBACK_URL

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        paystack_data = {
            "email": email,
            "amount": amount,
            "plan": plan_id,
            "callback_url": callback_url,
            "metadata": {
                "full_name": full_name,
                "email": email,
                "plan_type": plan_type,
                "is_ole_student": True,
                "class_level_id": class_level_id,
                "subject_ids": subject_ids,
                "is_mobile": is_mobile,
            },
        }

        logger.debug("Paystack init payload prepared for %s", email)

        try:
            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                json=paystack_data,
                headers=headers
            )
            result = response.json()
        except Exception as e:
            AdminActionLog.objects.create(
                action_type="error",
                email=email,
                details=f"Paystack error: {str(e)}"
            )
            return Response({"error": "Could not reach Paystack."}, status=502)

        if response.status_code == 200 and result.get("status") and result.get("data"):
            AdminActionLog.objects.create(
                action_type="payment_initialized",
                email=email,
                details="Payment initialized successfully with Paystack."
            )
            return Response({"authorization_url": result["data"]["authorization_url"]}, status=200)

        paystack_message = result.get("message", "Unknown error")
        logger.error(
            "Paystack init failed for %s. plan_id=%s message=%r",
            email, plan_id, paystack_message,
        )
        AdminActionLog.objects.create(
            action_type="error",
            email=email,
            details=f"Paystack init failed (plan_id={plan_id}): {paystack_message}"
        )
        return Response(
            {"error": "We could not start your payment. Please try again shortly, or contact support."},
            status=400
        )




class VerifyOleStudentPaymentView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        logger.info("=== VERIFY OLE STUDENT PAYMENT CALLED ===")

        reference = request.data.get("reference")
        if not reference:
            logger.info("❌ Missing reference in request.")
            return Response({"error": "Missing reference."}, status=400)
        
        # ✅ FINAL FIX: Use a database transaction for an atomic and persistent idempotency check.
        try:
            # Attempt to create a new record. This will fail if the reference already exists
            # due to the 'unique=True' constraint on the PaymentVerification model.
            OlePaymentVerification.objects.create(reference=reference)
            logger.info(f"✅ Created new verification record for: {reference}")
        except IntegrityError:
            # If the record already exists, catch the error and immediately return a success response.
            logger.warning(f"⚠️ Duplicate verification attempt for {reference} (DB check).")
            return Response(
                {"status": "duplicate", "message": "Payment already processed."},
                status=200
            )

        logger.info(f"🔍 Verifying payment with reference: {reference}")
        verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }

        try:
            response = requests.get(verify_url, headers=headers)
            result = response.json()
            logger.info(f"✅ PAYSTACK VERIFY RESULT: {json.dumps(result, indent=2)}")
        except Exception as e:
            logger.info(f"❌ Error contacting Paystack: {str(e)}")
            # Consider rolling back the PaymentVerification creation if Paystack is unavailable
            # to allow for a future retry, though this adds complexity.
            return Response({"error": "Verification service unavailable."}, status=502)

        if not (result.get("status") and result["data"].get("status") == "success"):
            logger.info("❌ Payment verification failed or incomplete.")
            return Response({"error": "Payment verification failed or incomplete."}, status=400)

        metadata = result["data"].get("metadata", {})
        logger.info(f"📦 Extracted Metadata: {json.dumps(metadata, indent=2)}")

        email = metadata.get("email", "").strip().lower()
        full_name = metadata.get("full_name")
        plan_type = metadata.get("plan_type")
        class_level_id = metadata.get("class_level_id")
        subject_ids = metadata.get("subject_ids", [])

        if not email or not full_name or not plan_type or not class_level_id:
            logger.info(f"❌ Incomplete metadata from Paystack: {metadata}")
            return Response({"error": "Incomplete metadata from Paystack."}, status=400)

        logger.info(f"👤 Normalized Email: {email}")

        user = CustomUser.objects.filter(email=email).first()
        new_user_created = False
        password = None

        if user:
            logger.info(f"🔍 Found existing user: {email}")
            if user.role == "ole_student" and user.ole_class_level and user.ole_subjects.exists():
                logger.info("✅ Existing user is fully registered.")
                # The frontend will receive the same 200 OK response with the same message and data.
                return Response({
                    "message": "Payment verified. Your account is already active.",
                    "email": user.email,
                    "temporary_password": None,
                    "role": user.role
                }, status=200)
            else:
                logger.info("⚠️ Existing user is incomplete. Proceeding to complete setup.")
        else:
            logger.info("🆕 Creating new user...")
            password = get_random_string(8)
            try:
                user = CustomUser.objects.create_user(
                    email=email,
                    full_name=full_name,
                    role="ole_student",
                    password=password,
                    is_active=True,
                )
                new_user_created = True
                logger.info(f"✅ User created: {user.email}")
            except IntegrityError as e:
                logger.info(f"❌ IntegrityError during user creation: {e}")
                return Response({
                    "error": "User creation failed — possibly due to duplicate or bad data."
                }, status=400)
            except Exception as e:
                logger.info(f"❌ Unexpected error during user creation: {e}")
                return Response({
                    "error": f"Unexpected error during user creation: {str(e)}"
                }, status=500)

        # Step: Assign class and subjects
        try:
            class_level = OleClassLevel.objects.get(id=class_level_id)
            subjects = OleSubject.objects.filter(id__in=subject_ids)
            user.ole_class_level = class_level
            user.save()
            user.ole_subjects.set(subjects)
            logger.info("✅ Class level and subjects assigned.")
        except Exception as e:
            logger.info(f"❌ Error assigning class/subjects: {e}")
            return Response({"error": f"Error assigning class/subjects: {str(e)}"}, status=400)

        # Step: Create subscription
        try:
            now = timezone.now()
            duration = timedelta(days=30) if plan_type == "monthly" else timedelta(days=365)
            OleStudentSubscription.objects.create(
                user=user,
                plan_type=plan_type,
                end_date=now + duration
            )
            logger.info("✅ Subscription created successfully.")
        except Exception as e:
            logger.info(f"❌ Subscription creation failed: {e}")
            return Response({"error": f"Subscription creation failed: {str(e)}"}, status=400)

        # Step: Send welcome email (non-blocking)
        def send_async_email(subject, message, recipient):
            def _send():
                try:
                    send_mail(
                        subject,
                        message,
                        "noreply@ischool.ng",
                        [recipient],
                        fail_silently=True
                    )
                except Exception as e:
                    logger.error(f"❌ Async email send failed: {e}")
            threading.Thread(target=_send, daemon=True).start()

        welcome_subject = "Welcome to iSchool Ole!"
        welcome_message = f"""
        Hello {full_name},

        Your iSchool Ole account has been successfully created.

        Login Details:
        Email: {email}
        Password: {password or '[already set]'}

        Visit: https://www.ischool.ng/ole-student/login

        Best regards,  
        iSchool Ole Team
        """

        send_async_email(welcome_subject, welcome_message, email)
        logger.info(f"📨 Welcome email queued for: {email}")

        # The frontend will receive the same response body and status codes.
        return Response({
            "message": (
                "Payment verified and account created."
                if new_user_created
                else "Account completed successfully. Please copy your email and Password to login"
            ),
            "email": email,
            "temporary_password": password if new_user_created else None,
            "role": "ole_student",
        }, status=201 if new_user_created else 200)


class OleStudentLoginView(LoginView):
    """
    Custom login view that only allows users with the role 'ole_student' to log in.

    - Uses dj-rest-auth's LoginView for authentication.
    - After authentication, checks the user's role.
    - Denies access if the user is not an 'ole_student'.
    """

    def post(self, request, *args, **kwargs):
        # Authenticate using built-in LoginView logic
        response = super().post(request, *args, **kwargs)

        # Get the authenticated user
        user = self.user

        # If user exists but is not an ole_student → deny access
        if user and user.role != "ole_student":
            return Response(
                {"error": "Access denied. You are not registered as an Ole Student."},
                status=status.HTTP_403_FORBIDDEN
            )

        # If ole_student, return the original login response (includes token)
        return response

        

class OleStudentDashboardView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # ✅ Handle AnonymousUser gracefully
        if user.is_anonymous:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ Check if user has correct role
        if user.role != "ole_student":
            return Response({"error": "Access denied. Only Ole Students can access this view."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OleStudentDashboardSerializer(user)
        return Response(serializer.data, status=200)
    

# Example of Parent View
class ParentResultsView(APIView):
    permission_classes = [IsParentUser]  # Only parents can view their child's results

    def get(self, request):
        # Example action: Get child's results (assuming parent is related to student)
        # Logic for getting child's results goes here
        return Response({"message": "Parent's view of child's results"}, status=status.HTTP_200_OK)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_student_lesson_detail(request, id):
    user = request.user

    try:
        match = OleStudentMatch.objects.get(student=user, schedule_id=id)
    except OleStudentMatch.DoesNotExist:
        return Response({"error": "Not matched to this lesson."}, status=403)

    if not user.is_subscription_active():
        return Response({"error": "Inactive subscription. Please renew to access this lesson."}, status=403)

    lesson = get_object_or_404(LiveClassSchedule, id=id)
    serializer = LiveClassScheduleDetailSerializer(lesson)
    return Response(serializer.data)



class OleStudentLessonHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "ole_student":
            return Response({"error": "Unauthorized"}, status=403)
        
        if not user.is_subscription_active():
            return Response(
                {"detail": "Your subscription has expired. Please renew to continue."},
                status=status.HTTP_403_FORBIDDEN
            )

        lessons = OleLesson.objects.filter(
            class_level=user.ole_class_level,
            subject__in=user.ole_subjects.all(),
            date__lt=timezone.now().date()
        ).order_by("-date")

        serializer = LessonHistorySerializer(lessons, many=True)
        return Response(serializer.data)


class OleStudentMaterialListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_subscription_active():
            return Response(
                {"detail": "Your subscription has expired. Please renew to continue."},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.role != "ole_student":
            return Response({"error": "Unauthorized"}, status=403)

        materials = (
            OleMaterial.objects
            .filter(
                class_level=user.ole_class_level,
                subject__in=user.ole_subjects.all(),
            )
            .select_related("subject", "class_level")  # serializer renders both
            .order_by("-uploaded_at")
        )

        serializer = OleMaterialSerializer(materials, many=True)
        return Response(serializer.data)

class RenewSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        plan_id = request.data.get("plan_id")

        if not plan_id:
            return Response({"error": "Plan ID is required."}, status=400)

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Invalid subscription plan."}, status=404)

        now = timezone.now().date()  # Use `.date()` to match the model field type

        # Extend or set the subscription expiration correctly
        if user.subscription_expires_on and user.subscription_expires_on >= now:
            user.subscription_expires_on += timedelta(days=plan.duration_days)
        else:
            user.subscription_expires_on = now + timedelta(days=plan.duration_days)

        user.save()
        return Response({
            "message": "Subscription renewed successfully.",
            "expires_on": user.subscription_expires_on
        })

# views.py
class SubscriptionPlanListAPIView(APIView):
    def get(self, request):
        plans = SubscriptionPlan.objects.all().values('id', 'name', 'price', 'duration_days')
        return Response(plans)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initialize_subscription_payment(request):
    user = request.user
    plan = {
        "id": 1,
        "name": "Monthly Access",
        "price": 5000,  # NGN
        "duration_days": 30
    }

    reference = f"SUB-{uuid.uuid4().hex[:10].upper()}"

    # ✅ Mobile clients must be sent to the API callback, which responds with a
    # redirect into the app (ischoolmobile://payment-callback?...). The web
    # callback is a plain website and strands mobile users in the browser.
    is_mobile = request.data.get("is_mobile", False)
    if is_mobile:
        callback_url = "https://api.ischool.ng/api/payments/payment-callback/?ole=true"
    else:
        callback_url = settings.OLE_PAYMENT_CALLBACK_URL

    paystack_payload = {
        "reference": reference,
        "amount": plan["price"] * 100,  # Kobo
        "email": user.email,
        "callback_url": callback_url,
        "metadata": {
            "user_id": user.id,
            "plan_id": plan["id"],
            "plan_name": plan["name"],
            "duration_days": plan["duration_days"],
            "is_mobile": is_mobile
        }
    }
    return Response(paystack_payload)@api_view(["POST"])


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    reference = request.data.get("reference")
    if not reference:
        return Response({"error": "Transaction reference is required."}, status=400)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    verify_url = f"https://api.paystack.co/transaction/verify/{reference}"

    try:
        paystack_response = requests.get(verify_url, headers=headers)
        result = paystack_response.json()

        if result["status"] is not True:
            return Response({"error": "Payment verification failed."}, status=400)

        data = result["data"]
        if data["status"] != "success":
            return Response({"error": "Payment was not successful."}, status=400)

        metadata = data.get("metadata", {})
        user_id = metadata.get("user_id")
        plan_id = metadata.get("plan_id")

        # Safety check
        if user_id != request.user.id:
            return Response({"error": "User mismatch."}, status=403)

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription plan not found."}, status=404)

        user = request.user
        now = timezone.now()
        if user.subscription_expiry and user.subscription_expiry > now:
            user.subscription_expiry += timedelta(days=plan.duration_days)
        else:
            user.subscription_expiry = now + timedelta(days=plan.duration_days)

        user.plan_type = plan.name  # Optional: track what plan they're on
        user.save()

        return Response({"message": "Subscription renewed successfully.", "expires_on": user.subscription_expiry})

    except requests.RequestException:
        return Response({"error": "Error contacting Paystack."}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def log_student_join(request):
    session_id = request.data.get("session_id")
    user = request.user

    if AttendanceLog.objects.filter(session_id=session_id, student=user).exists():
        return Response({"detail": "Already logged."})

    log = AttendanceLog.objects.create(session_id=session_id, student=user)
    return Response({"attendance_id": log.id})



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def log_student_leave(request):
    session_id = request.data.get("session_id")
    user = request.user

    try:
        log = AttendanceLog.objects.get(session_id=session_id, student=user)
        log.left_at = timezone.now()
        log.save()
        return Response({"detail": "Left time logged."})
    except AttendanceLog.DoesNotExist:
        return Response({"detail": "Attendance not found."}, status=404)

def format_phone_number(phone):
    """
    Canonical NG number as 234XXXXXXXXXX (no leading +), or None if invalid.

    Delegates to the single validator in sms_services so the send and verify
    paths can never disagree about what a number normalises to — a mismatch
    there silently breaks OTP verification.
    """
    from .sms_services import format_phone_for_sms
    formatted = format_phone_for_sms(phone)
    return formatted.lstrip('+') if formatted else None


class OTPRateThrottle(AnonRateThrottle):
    """Rate-limit anonymous OTP requests by client IP address."""

    scope = 'otp'
    rate = '5/min'


def _normalise_verification_identifier(request):
    """
    Read the identifier field (or legacy fields) and return the identifier
    exactly as it is stored in VerificationCode.

    Returns: (identifier, method, error_message)
    """
    raw_identifier = (
        request.data.get('identifier')
        or request.data.get('email')
        or request.data.get('phone_number')
    )
    identifier = str(raw_identifier).strip() if raw_identifier is not None else ''

    if not identifier:
        return None, None, 'Identifier (email or phone) is required'

    requested_method = str(request.data.get('method') or '').strip().lower()
    if requested_method and requested_method not in ('email', 'phone'):
        return None, None, 'Method must be either email or phone'

    # Older clients do not send method, so infer it for backwards compatibility.
    method = requested_method or ('email' if '@' in identifier else 'phone')

    if method == 'email':
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', identifier):
            return None, None, 'Invalid email address'
        return identifier.lower(), method, None

    # Keep this import local if sms_services imports models or Django settings.
    from .sms_services import format_phone_for_sms

    formatted_phone = format_phone_for_sms(identifier)
    if not formatted_phone:
        return (
            None,
            None,
            'Please enter a valid Nigerian phone number, e.g. 08031234567.',
        )

    # VerificationCode historically stores phone identifiers without the plus.
    return formatted_phone.lstrip('+'), method, None


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def send_verification_code(request):
    identifier, method, error = _normalise_verification_identifier(request)
    if error:
        return Response({'error': error}, status=400)

    # Only one active code should exist for an identifier.
    VerificationCode.objects.filter(identifier=identifier).delete()

    verification = VerificationCode.objects.create(
        identifier=identifier,
        method=method,
    )

    if method == 'email':
        from .sms_services import send_email_code

        sent = send_email_code(identifier, verification.code)
    else:
        from .sms_services import send_sms_auto_fallback

        sent = send_sms_auto_fallback(identifier, verification.code)

    # In development/sandbox, allow the client to continue if the provider is
    # intentionally unavailable. Do not do this in production.
    if not sent and not settings.DEBUG:
        return Response({'error': 'Failed to send verification code'}, status=500)

    response_data = {
        'message': 'Code sent successfully',
        'expires_in': 600,
        'method': method,
    }

    is_sandbox = getattr(settings, 'AFRICASTALKING_USERNAME', '') == 'sandbox'
    if is_sandbox or settings.DEBUG:
        response_data['code'] = verification.code
        response_data['test_mode'] = True

    return Response(response_data, status=200)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def verify_code(request):
    identifier, _method, error = _normalise_verification_identifier(request)
    code = str(request.data.get('code') or '').strip()

    if error:
        return Response({'error': error}, status=400)
    if not code:
        return Response({'error': 'Identifier and code are required'}, status=400)

    try:
        verification = VerificationCode.objects.get(
            identifier=identifier,
            code=code,
            is_verified=False,
        )
    except VerificationCode.DoesNotExist:
        return Response({'error': 'Invalid verification code'}, status=400)

    if verification.is_expired():
        verification.delete()
        return Response({'error': 'Code expired', 'expired': True}, status=400)

    verification.is_verified = True
    verification.save(update_fields=['is_verified'])

    return Response(
        {
            'message': 'Verification successful',
            'identifier': identifier,
            'verified': True,
        },
        status=200,
    )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def check_verification_status(request):
    identifier, _method, error = _normalise_verification_identifier(request)
    if error:
        return Response({'error': error}, status=400)

    verified = VerificationCode.objects.filter(
        identifier=identifier,
        is_verified=True,
    ).exists()

    return Response({'verified': verified}, status=200)



@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_or_register(request):
    """
    After verification, either login existing user or create new user.
    Accepts 'identifier' (email or phone) and 'method' (optional, inferred).
    """
    identifier = request.data.get('identifier')
    platform = request.data.get('platform', 'ole')

    if not identifier:
        return Response({'error': 'Identifier required'}, status=400)

    # Normalize and determine method
    if '@' in identifier and '.' in identifier:
        method = 'email'
        identifier = identifier.lower()
    else:
        method = 'phone'
        from .sms_services import format_phone_for_sms
        formatted = format_phone_for_sms(identifier)
        if not formatted:
            return Response({'error': 'Invalid phone number'}, status=400)
        identifier = formatted.lstrip('+')

    # Check if verification exists and is verified
    try:
        verification = VerificationCode.objects.filter(
            identifier=identifier,
            is_verified=True
        ).latest('created_at')
    except VerificationCode.DoesNotExist:
        return Response({
            'error': 'Identifier not verified. Please verify first.',
            'verified': False
        }, status=400)

    User = get_user_model()
    if method == 'email':
        user = User.objects.filter(email=identifier).first()
    else:
        user = User.objects.filter(phone_number=identifier).first()

    is_new_user = False
    if not user:
        # Create new user
        is_new_user = True
        # Generate a random username and password
        import uuid
        random_suffix = str(uuid.uuid4())[:8]
        if method == 'email':
            # email is already unique, use as identifier
            username = f"user_{random_suffix}"
            email = identifier
            phone_number = None
        else:
            # phone
            username = f"user_{random_suffix}"
            email = None
            phone_number = identifier

        # Ensure username uniqueness
        while User.objects.filter(username=username).exists():
            random_suffix = str(uuid.uuid4())[:8]
            username = f"user_{random_suffix}"

        # Create user with unusable password (OTP login)
        user = User(
            email=email,
            phone_number=phone_number,
            username=username,
            full_name=f"{'Student' if platform=='ole' else 'User'} {identifier[-4:]}",
            role='ole_student' if platform == 'ole' else 'student',
            is_active=True
        )
        user.set_unusable_password()
        user.save()

        # Create OLE profile if needed
        if platform == 'ole':
            try:
                OleStudentProfile.objects.get_or_create(user=user)
            except:
                pass

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    response_data = {
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'full_name': user.full_name,
            'phone_number': user.phone_number,
            'email': user.email,
            'username': user.username,
            'role': user.role,
        },
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
        'is_new_user': is_new_user
    }

    return Response(response_data)



@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def phone_logout(request):
    """
    Logout by blacklisting refresh token
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get current user's profile including phone number
    """
    user = request.user
    
    # Get additional profile data based on role
    profile_data = {
        'id': user.id,
        'full_name': user.full_name,
        'phone_number': user.phone_number,
        'email': user.email,
        'username': user.username,
        'role': user.role,
    }
    
    # Add OLE-specific data
    if user.role == 'ole_student':
        try:
            profile = user.ole_profile
            profile_data['class_level'] = profile.class_level.name if profile.class_level else None
            profile_data['subjects'] = list(profile.subjects.values_list('name', flat=True))
        except OleStudentProfile.DoesNotExist:
            pass
        
        # Add subscription status
        try:
            subscription = user.ole_subscription
            profile_data['subscription'] = {
                'plan_type': subscription.plan_type,
                'is_active': subscription.is_active(),
                'expires_in_days': (subscription.end_date.date() - timezone.now().date()).days
            }
        except OleStudentSubscription.DoesNotExist:
            profile_data['subscription'] = None
    
    return Response(profile_data)


@csrf_exempt
def api_root(request):
    return JsonResponse({
        'status': 'success',
        'message': 'Users API is working',
        'available_endpoints': [
            'POST /api/users/phone/send-code/',
            'POST /api/users/phone/verify-code/',
            'POST /api/users/phone/check-verification/',
        ]
    })