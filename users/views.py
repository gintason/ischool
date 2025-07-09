from rest_framework import status, permissions
from django.utils.crypto import get_random_string
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (UserRegistrationSerializer, 
                          CustomTokenObtainPairSerializer, OleStudentRegistrationSerializer, 
                          OleStudentDashboardSerializer)

from .models import RegistrationGroup
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
from django.conf import settings
from django.db import IntegrityError  # Make sure this is imported at the top
from django.core.mail import send_mail
from django.contrib import messages



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
            password=username  # temporary
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


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)



class OleStudentRegistrationView(APIView):
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

        plan_id = settings.PAYSTACK_PLAN_IDS.get(plan_type)
        amount = settings.PAYSTACK_PLAN_AMOUNTS.get(plan_type)

        if not plan_id or not amount:
            return Response({"error": "Invalid plan type selected."}, status=400)

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "email": email,
            "amount": amount,
            "plan": plan_id,
            "callback_url": settings.OLE_PAYMENT_CALLBACK_URL,
            "metadata": {
                "full_name": full_name,
                "email": email,
                "plan_type": plan_type,
                "is_ole_student": True,
                "class_level_id": class_level_id,
                "subject_ids": subject_ids,
            },
        }

        print("🚀 Payload being sent to Paystack:", json.dumps(data, indent=2))

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

        AdminActionLog.objects.create(
            action_type="error",
            email=email,
            details=f"Paystack init failed: {result.get('message', 'Unknown error')}"
        )
        return Response({"error": result.get("message", "Payment initialization failed.")}, status=400)



# ole students payment verification and account creation
class VerifyOleStudentPaymentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not request.data:
            return Response({"error": "No data provided."}, status=400)

        reference = request.data.get("reference")
        if not reference:
            return Response({"error": "Missing reference."}, status=400)

        # Step 1: Verify with Paystack
        verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }

        try:
            response = requests.get(verify_url, headers=headers)
            result = response.json()
            print("✅ PAYSTACK VERIFY RESULT:", json.dumps(result, indent=2))
        except Exception:
            return Response({"error": "Verification service unavailable."}, status=502)

        if not (result.get("status") and result["data"].get("status") == "success"):
            return Response({"error": "Payment verification failed or incomplete."}, status=400)

        # Step 2: Extract metadata
        metadata = result["data"].get("metadata", {})
        email = metadata.get("email", "").strip().lower()
        full_name = metadata.get("full_name")
        plan_type = metadata.get("plan_type")
        class_level_id = metadata.get("class_level_id")
        subject_ids = metadata.get("subject_ids", [])

        print("📧 Email from Paystack metadata:", email)
        print("👤 Checking if user exists for email:", email)

        if not email or not full_name or not plan_type or not class_level_id:
            return Response({"error": "Incomplete metadata from Paystack."}, status=400)

        # Step 3: Check if user already exists
        existing_user = CustomUser.objects.filter(email=email).first()
        if existing_user:
            return Response({
                "message": "Payment verified. Your account is already active.",
                "email": existing_user.email,
                "temporary_password": None,
                "role": existing_user.role
            }, status=200)

        # Step 4: Create the user
        password = get_random_string(8)
        try:
            user = CustomUser.objects.create_user(
                email=email,
                full_name=full_name,
                role="ole_student",
                password=password,
                is_active=True,
            )
        except IntegrityError:
            user = CustomUser.objects.get(email=email)
            return Response({
                "message": "User already exists. Payment was likely verified already.",
                "email": user.email,
                "temporary_password": None,
                "role": user.role
            }, status=200)

        # Step 5: Assign class and subjects
        try:
            from teachers.models import OleClassLevel, OleSubject
            class_level = OleClassLevel.objects.get(id=class_level_id)
            subjects = OleSubject.objects.filter(id__in=subject_ids)
            user.ole_class_level = class_level
            user.save()
            user.ole_subjects.set(subjects)
        except Exception as e:
            return Response({"error": f"Error assigning class/subjects: {str(e)}"}, status=400)

        # Step 6: Create subscription
        try:
            now = timezone.now()
            duration = timedelta(days=30) if plan_type == "monthly" else timedelta(days=365)
            OleStudentSubscription.objects.create(
                user=user,
                plan_type=plan_type,
                end_date=now + duration
            )
        except Exception as e:
            return Response({"error": f"Subscription creation failed: {str(e)}"}, status=400)

        # Step 7: Send email
        try:
            send_mail(
                "Welcome to iSchool Ole!",
                f"""
            Hello {full_name},

            Your iSchool Ole account has been successfully created.

            Login Details:
            Email: {email}
            Password: {password}

            Visit: https://www.ischool.ng/ole-student/login

            Best regards,  
            iSchool Ole Team
                    """,
                    "noreply@ischool.ng",  # <-- from_email required!
                     [email],               # <-- recipient list must be a list
                )
        except Exception as e:
            print("Email sending error:", e)

        return Response({
            "message": "Payment verified and account created.",
            "email": email,
            "temporary_password": password,
            "role": "ole_student"
        }, status=201)
                    
    


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
