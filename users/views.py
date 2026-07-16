from rest_framework import status, permissions
from django.utils.crypto import get_random_string
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (UserRegistrationSerializer, 
                          CustomTokenObtainPairSerializer, OleStudentRegistrationSerializer, 
                          OleStudentDashboardSerializer)

from .models import RegistrationGroup, OlePaymentVerification
from .permissions import  IsTeacherUser, IsStudentUser, IsParentUser, IsAdminUser, IsOleStudentUser
from rest_framework import status, permissions
from .serializers import CustomUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import StudentSlot
from .serializers import StudentSlotSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
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
import requests
import json
import random
import uuid
import string
from django.utils import timezone
from django.conf import settings
from django.db import IntegrityError  # Make sure this is imported at the top
from django.core.mail import send_mail
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PhoneVerification
from .sms_services import send_sms
import logging
import threading
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

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
        serializer = OleStudentRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"].lower()
        full_name = serializer.validated_data["full_name"]
        plan_type = serializer.validated_data["plan_type"]
        class_level_id = serializer.validated_data["class_level_id"]
        subject_ids = serializer.validated_data["subject_ids"]

        AdminActionLog.objects.create(
            action_type="registration_attempt",
            email=email,
            details=f"Attempting registration with plan: {plan_type}, class_level_id: {class_level_id}",
        )

        try:
            class_level = OleClassLevel.objects.get(id=class_level_id)
            if not subject_ids:
                return Response({"detail": "No subjects selected."}, status=400)

            subjects = OleSubject.objects.filter(id__in=subject_ids)
            if not subjects.exists():
                return Response({"detail": "Invalid subject selection."}, status=400)

        except OleClassLevel.DoesNotExist:
            return Response({"detail": "Invalid class level selected."}, status=400)

        # ✅ DO NOT create user here anymore — let payment verification handle it

        # OLE currently offers the monthly plan only. plan_type is captured for
        # future use but the plan/amount are resolved from the monthly config.
        plan_id = settings.PAYSTACK_PLAN_IDS.get("monthly")
        amount = settings.PAYSTACK_PLAN_AMOUNTS.get("monthly")

        if not plan_id or not amount:
            logger.error(
                "OLE plan misconfigured: plan_id=%r amount=%r. Check "
                "PAYSTACK_PLAN_IDS/PAYSTACK_PLAN_AMOUNTS in settings.",
                plan_id, amount,
            )
            return Response(
                {"error": "Subscription plan is not configured. Please contact support."},
                status=500,
            )

        # ✅ Decide callback URL
        is_mobile = request.data.get("is_mobile", False)
        if is_mobile:
            callback_url = "https://api.ischool.ng/api/payments/payment-callback/?ole=true"  # 👈 deep link back to mobile app
        else:
            callback_url = settings.OLE_PAYMENT_CALLBACK_URL  # 👈 default (web)

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        data = {
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
                "is_mobile": is_mobile,  # 👈 tracked for debugging
            },
        }

        logger.debug("Paystack init payload prepared for %s", email)

        try:
            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                json=data,
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
        # "Plan not found" here means the configured PAYSTACK_PLAN_IDS['monthly']
        # does not exist in the Paystack account tied to the current secret key
        # (usually a test-vs-live key/plan mismatch, or a deleted plan).
        logger.error(
            "Paystack init failed for %s. plan_id=%s message=%r",
            email, plan_id, paystack_message,
        )
        AdminActionLog.objects.create(
            action_type="error",
            email=email,
            details=f"Paystack init failed (plan_id={plan_id}): {paystack_message}"
        )
        user_message = (
            "We could not start your payment. Please try again shortly, or "
            "contact support if this continues."
        )
        return Response({"error": user_message, "gateway_message": paystack_message}, status=400)



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

        materials = OleMaterial.objects.filter(
            class_level=user.ole_class_level,
            subject__in=user.ole_subjects.all()
        ).order_by("-uploaded_at")

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
            "duration_days": plan["duration_days"]
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


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def send_verification_code(request):
    try:
        phone = request.data.get('phone_number')
        platform = request.data.get('platform', 'ole')
        
        if not phone:
            return Response({'error': 'Phone number is required'}, status=400)

        # Canonicalise to E.164 with the same validator the SMS layer uses, so
        # the stored number and the sent number always agree — and reject
        # obviously invalid numbers before spending an SMS on them.
        from .sms_services import format_phone_for_sms
        formatted = format_phone_for_sms(phone)
        if not formatted:
            return Response(
                {'error': 'Please enter a valid Nigerian phone number, e.g. 08031234567.'},
                status=400,
            )
        # Store without the leading '+' to match the existing lookup format (234...).
        phone = formatted.lstrip('+')

        # Delete old codes
        PhoneVerification.objects.filter(phone_number=phone).delete()
        
        # Create new code
        verification = PhoneVerification.objects.create(phone_number=phone)
        
        logger.info(f"VERIFICATION CODE for {phone}: {verification.code}")
        logger.info("Verification code generated for %s", phone)
        
        # Check if we're in sandbox mode
        is_sandbox = getattr(settings, 'AFRICASTALKING_USERNAME', '') == 'sandbox'
        
        # Send SMS using the auto-fallback service
        from .sms_services import send_sms_auto_fallback
        sms_sent = send_sms_auto_fallback(phone, verification.code)
        
        if not sms_sent and not is_sandbox:
            logger.error(f"Failed to send SMS to {phone}")
            # Still return success in DEBUG mode
            if not settings.DEBUG:
                return Response(
                    {'error': 'Failed to send verification code. Please try again.'}, 
                    status=500
                )
        
        # Build response data
        response_data = {
            'message': 'Code sent successfully',
            'expires_in': 600
        }
        
        # Only return the actual code in sandbox mode or DEBUG mode
        if is_sandbox or settings.DEBUG:
            response_data['code'] = verification.code
            response_data['test_mode'] = True
        
        return Response(response_data, status=200)  # ✅ Explicit status
        
    except Exception as e:
        logger.error(f"Error in send_verification_code: {str(e)}", exc_info=True)
        logger.error("send_verification_code error: %s", e, exc_info=True)
        return Response(
            {'error': f'Server error: {str(e)}'}, 
            status=500
        )

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def verify_code(request):
    try:
        phone = request.data.get('phone_number')
        code = request.data.get('code')
        platform = request.data.get('platform', 'ole')
        
        logger.debug("Verifying phone %s", phone)
        
        if not phone or not code:
            return Response({'error': 'Phone number and code are required'}, status=400)
        
        # Format phone using the shared validator.
        phone = format_phone_number(phone)
        if not phone:
            return Response({'error': 'Please enter a valid Nigerian phone number.'}, status=400)
        
        try:
            verification = PhoneVerification.objects.get(
                phone_number=phone,
                code=code,
                is_verified=False
            )
            
            logger.debug("OTP record expires at %s", verification.expires_at)
            logger.debug("Current time %s", timezone.now())
            
            # Check if expired
            if verification.is_expired():
                logger.info("OTP expired for %s", phone)
                # Delete expired code
                verification.delete()
                return Response({
                    'error': 'Code has expired. Please request a new code.',
                    'expired': True
                }, status=400)
            
            # Mark as verified
            verification.is_verified = True
            verification.save()
            
            logger.info("OTP verified for %s", phone)
            
            return Response({
                'message': 'Phone number verified successfully',
                'platform': platform,
                'verified': True
            })
            
        except PhoneVerification.DoesNotExist:
            logger.info("No valid OTP record for %s", phone)
            return Response({'error': 'Invalid verification code'}, status=400)
            
    except Exception as e:
        logger.error("verify_code error: %s", e, exc_info=True)
        import traceback
        traceback.print_exc()
        return Response({'error': f'Server error: {str(e)}'}, status=500)
    

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def check_verification_status(request):
    phone = request.data.get('phone_number')
    platform = request.data.get('platform', 'ole')
    
    if not phone:
        return Response({'error': 'Phone number is required'}, status=400)
    
    # Format phone
    phone = phone.strip().replace(' ', '')
    if not phone.startswith('234'):
        phone = '234' + phone.lstrip('0')
    
    try:
        # Check if there's a verified record for this phone
        verification = PhoneVerification.objects.filter(
            phone_number=phone,
            is_verified=True
        ).exists()
        
        return Response({
            'verified': verification,
            'message': 'Phone number already verified' if verification else 'Phone number not verified'
        })
            
    except Exception as e:
        logger.error(f"Check verification error: {e}")
        return Response({'verified': False, 'error': str(e)}, status=500)
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



@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def phone_login_or_register(request):
    """
    After phone verification, either:
    1. Login existing user by phone number
    2. Create new user and login
    """
    try:
        phone = request.data.get('phone_number')
        platform = request.data.get('platform', 'ole')
        
        if not phone:
            return Response({'error': 'Phone number is required'}, status=400)
        
        # Format phone
        phone = format_phone_number(phone)
        
        logger.info(f"Phone login/register attempt for: {phone}")
        
        # Check if verification exists and is verified
        try:
            verification = PhoneVerification.objects.filter(
                phone_number=phone,
                is_verified=True
            ).latest('created_at')
        except PhoneVerification.DoesNotExist:
            return Response({
                'error': 'Phone number not verified. Please verify first.',
                'verified': False
            }, status=400)
        
        User = get_user_model()
        
        # ✅ Check if user already exists with this phone
        user = User.objects.filter(phone_number=phone).first()
        
        if user:
            # ✅ EXISTING USER - just login
            is_new_user = False
            logger.info(f"Existing user found: {user.email}")
            
            # Update full_name if it was auto-generated
            if user.full_name.startswith('Student '):
                user.full_name = f"Student {phone[-4:]}"
                user.save()
        else:
            # ✅ NEW USER - create account
            is_new_user = True
            random_suffix = get_random_string(6).lower()
            email = f"phone_{phone[-8:]}_{random_suffix}@ischool.ng"
            username = f"ole_{phone[-6:]}_{random_suffix[:4]}"
            
            # Ensure unique username
            counter = 1
            base_username = username
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            # Ensure unique email
            counter = 1
            base_email = email
            while User.objects.filter(email=email).exists():
                email = f"phone_{phone[-8:]}_{random_suffix}_{counter}@ischool.ng"
                counter += 1
            
            # Create user
            user = User(
                email=email,
                phone_number=phone,
                username=username,
                full_name=f"Student {phone[-4:]}",
                role='ole_student' if platform == 'ole' else 'student',
                is_active=True,
            )
            
            # Set an unusable password (phone auth doesn't need passwords)
            user.set_unusable_password()
            
            try:
                user.save()
                logger.info(f"New user created: {user.email} with phone {phone}")
            except Exception as e:
                logger.error(f"Failed to save user: {str(e)}")
                raise
            
            # Create OLE profile if applicable
            if platform == 'ole':
                try:
                    OleStudentProfile.objects.get_or_create(user=user)
                except Exception as e:
                    logger.error(f"Failed to create OLE profile: {e}")
        
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
        
    except Exception as e:
        logger.error(f"Phone login/register error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Server error: {str(e)}'}, 
            status=500
        )


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