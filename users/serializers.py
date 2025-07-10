from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import RegistrationGroup
from rest_framework import serializers
from .models import CustomUser
from django.core.mail import send_mail
from django.conf import settings
from .models import StudentSlot
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from teachers.models import OleClassLevel, OleSubject, LiveClassSchedule, OleLesson, OleMaterial, LiveClassSession
from users.models import CustomUser
from users.models import OleStudentSubscription  # Adjust import path if needed
from datetime import date
from django.utils import timezone
from .models import OleStudentProfile

# Custom user serializer for registration
from rest_framework import serializers
from .models import CustomUser, RegistrationGroup

from rest_framework import serializers
from users.models import CustomUser, RegistrationGroup

from django.core.mail import send_mail
from django.conf import settings

class UserRegistrationSerializer(serializers.ModelSerializer):
    registration_group = serializers.PrimaryKeyRelatedField(
        queryset=RegistrationGroup.objects.all(),
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'role', 'registration_group', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        group = validated_data.pop("registration_group")
        role = validated_data.get("role")

        # Step 1: Generate student serial number (e.g. 001)
        total_registered = CustomUser.objects.filter(registration_group=group).count() + 1
        user_serial = f"{total_registered:03d}"

        # Step 2: Get state code and serial prefix from group
        state_code = group.state_code.upper()  # e.g. "NG"
        serial_prefix = group.serial_prefix.upper()  # e.g. "HOM"

        # Step 3: Construct username
        username = f"{state_code}/{serial_prefix}/{user_serial}"

        # Step 4: Create user with generated username as password
        user = CustomUser.objects.create_user(
            username=username,
            registration_group=group,
            **validated_data
        )
        user.set_password(username)  # Password same as username
        user.save()

        # Step 5: Reduce available slot
        group.decrease_slots()

        # Step 6: Send login details via email
        subject = "Your iSchool Ola Login Details"
        message = (
            f"Hello {user.full_name},\n\n"
            f"Thank you for registering with iSchool Ola.\n\n"
            f"Your login credentials are:\n"
            f"Username: {username}\n"
            f"Password: {username}\n\n"
            f"Please keep these details safe and secure.\n\n"
            f"iSchool Ola Team"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return user


# Serializer to handle login and JWT token generation
class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Check if user exists and validate credentials
        user = get_user_model().objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return {
            'refresh': str(refresh),
            'access': str(access_token)
        }
    

# users/serializers.py
from rest_framework import serializers
from .models import CustomUser, RegistrationGroup

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password", "full_name", "role", "registration_group")

    def validate(self, data):
        if not data.get("registration_group"):
            raise serializers.ValidationError("registration_group is required.")
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class StudentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSlot
        fields = ['id', 'main_user', 'full_name', 'email', 'username', 'password', 'created_at']
        read_only_fields = ['username', 'password', 'main_user', 'created_at']
        
    
class StudentDetailSerializer(serializers.Serializer):
    fullName = serializers.CharField()
    email = serializers.EmailField()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['registration_group'] = {
            "id": user.registration_group.id,
            "name": user.registration_group.name,
            "email": user.registration_group.email,
        } if hasattr(user, 'registration_group') else None
        return token
    

OLE_PLAN_CHOICES = [
    ('ole_monthly', 'Monthly'),
]

class OleStudentRegistrationSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    plan_type = serializers.ChoiceField(choices=OLE_PLAN_CHOICES)
    class_level_id = serializers.IntegerField()
    subject_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        allow_empty=False,
        help_text="List of subject IDs the student is registering for"
    )

    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_class_level_id(self, value):
        if not OleClassLevel.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid class level selected.")
        return value

    def validate_subject_ids(self, value):
        invalid_ids = [sid for sid in value if not OleSubject.objects.filter(id=sid).exists()]
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid subject IDs: {invalid_ids}")
        return value


class OleStudentBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email']


class OleStudentSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OleStudentSubscription
        fields = ['plan_type', 'start_date', 'end_date', 'is_active']
        read_only_fields = fields


class OleStudentProfileSerializer(serializers.ModelSerializer):
    class_level = serializers.StringRelatedField()
    subjects = serializers.StringRelatedField(many=True)
    subscription_status = serializers.SerializerMethodField()

    class Meta:
        model = OleStudentProfile
        fields = ['class_level', 'subjects', 'subscription_status']

    def get_subscription_status(self, obj):
        try:
            subscription = OleStudentSubscription.objects.get(user=obj.user)
            return {
                "plan_type": subscription.plan_type,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date,
                "is_active": subscription.is_active,
                "expires_in_days": (subscription.end_date - date.today()).days
            }
        except OleStudentSubscription.DoesNotExist:
            return None
        
        

class OleStudentDashboardSerializer(serializers.ModelSerializer):
    class_level = serializers.CharField(source="ole_class_level.name", default="")
    subjects = serializers.SlugRelatedField(
        many=True,
        source="ole_subjects",
        read_only=True,
        slug_field="name"
    )
    subscription_status = serializers.SerializerMethodField()
    plan_type = serializers.SerializerMethodField()

    def get_plan_type(self, obj):
        try:
            return obj.ole_subscription.plan_type
        except OleStudentSubscription.DoesNotExist:
            return None

    class Meta:
        model = CustomUser
        fields = [
            'full_name',
            'email',
            'plan_type',
            'class_level',
            'subjects',
            'subscription_status'
        ]

    def get_subscription_status(self, obj):
        try:
            sub = obj.ole_subscription
            if not sub:
                raise OleStudentSubscription.DoesNotExist

            return {
                "plan_type": sub.plan_type,
                "is_active": sub.is_active() if callable(getattr(sub, "is_active", None)) else sub.end_date > timezone.now(),
                "expires_in_days": (sub.end_date.date() - timezone.now().date()).days
            }

        except OleStudentSubscription.DoesNotExist:
            return {
                "plan_type": None,
                "is_active": False,
                "expires_in_days": -1
            }
        
    
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = OleSubject
        fields = ['name']


class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OleClassLevel
        fields = ['name']


class LiveClassScheduleDetailSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    class_level = ClassLevelSerializer()
    teacher = serializers.SerializerMethodField()
    meeting_link = serializers.SerializerMethodField()

    class Meta:
        model = LiveClassSchedule
        fields = [
            "id", "subject", "class_level", "teacher",
            "date", "start_time", "meeting_link"
        ]

    def get_subject(self, obj):
        if obj.subject:
            return {"name": obj.subject.name}
        return None

    def get_teacher(self, obj):
        if obj.teacher:
            return {"full_name": obj.teacher.full_name}
        return None

    def get_meeting_link(self, obj):
        try:
            return obj.liveclasssession.meeting_link
        except LiveClassSession.DoesNotExist:
            return None



class LessonHistorySerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source="subject.name")
    class_level = serializers.CharField(source="class_level.name")
    teacher = serializers.CharField(source="teacher.full_name")
    materials = serializers.SerializerMethodField()

    class Meta:
        model = OleLesson
        fields = ["id", "topic", "date", "start_time", "subject", "class_level", "teacher", "materials"]

    def get_materials(self, obj):
        return [{"title": m.title, "file_url": m.file.url if m.file else None} for m in obj.materials.all()]


class OleMaterialSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source="subject.name")
    class_level = serializers.CharField(source="class_level.name")

    class Meta:
        model = OleMaterial
        fields = ["id", "title", "description", "subject", "class_level", "file", "uploaded_at"]
