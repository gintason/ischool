from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.utils.crypto import get_random_string
from datetime import date
import random


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)

        # ✅ Auto-generate username if not provided
        if not user.username:
            if role == "ole_student":
                user.username = self.generate_ole_username(email)
            elif user.registration_group:
                user.username = self.generate_username_from_group(user.registration_group, role)
            else:
                # ✅ Use phone number based username for phone-auth users
                if user.phone_number:
                    user.username = f"phone_{user.phone_number[-8:]}_{get_random_string(4).lower()}"
                else:
                    user.username = email

        # ✅ Fixed: Set password properly without calling non-existent super method
        if password:
            user.set_password(password)
        else:
            # Generate a random secure password for users without one (e.g., phone-auth)
            random_password = get_random_string(20)
            user.set_password(random_password)
            
        user.save(using=self._db)

        # ✅ Decrease slots only if registration_group exists
        if user.registration_group:
            user.registration_group.decrease_slots()

        return user
    
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


    def generate_ole_username(self, email):
        """Generate simple, unique username for ole students."""
        base = email.split('@')[0].replace('.', '').replace('+', '')
        suffix = get_random_string(4).upper()
        username = f"ole_{base}_{suffix}"
        
        # Ensure uniqueness
        counter = 1
        base_username = username
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
            
        return username

    def generate_username_from_group(self, group, role):
        role_codes = {
            "student": "S",
            "teacher": "T",
            "parent": "P",
            "admin": "A",
        }
        role_code = role_codes.get(role, "X")  # Default to 'X' if role is not recognized

        # Include state code, group serial number, user count, and year
        state_code = group.state_code
        group_serial = group.serial_prefix
        year = str(group.date_registered.year)  # Extract year of registration
        user_count = group.users.filter(role=role).count() + 1

        # Construct the username in format: YEAR/ROLECODE-STATE/SerialNumber/Count
        return f"{year}/{role_code}-{state_code}/{group_serial}/{str(user_count).zfill(3)}"

    def generate_unique_username(self, role, group=None):
        if group:
            year = str(group.date_registered.year)
            state_code = group.state_code.zfill(3)
            group_code = group.serial_prefix.zfill(3)
            type_code = "S" if group.group_type == "school" else "H"
            prefix = f"{year}/{state_code}/{type_code}{group_code}/"

            count = self.model.objects.filter(group=group, role=role).count() + 1
            username = f"{prefix}{str(count).zfill(4)}"

            while self.model.objects.filter(username=username).exists():
                count += 1
                username = f"{prefix}{str(count).zfill(4)}"
            return username
        else:
            role_prefix = role.lower()
            count = self.model.objects.filter(role=role).count() + 1
            return f"{role_prefix}_{str(count).zfill(4)}"

    # ✅ Removed the broken make_random_password method - using get_random_string instead


# Custom User model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("teacher", "Teacher"),
        ("student", "Student"),
        ("parent", "Parent"),
        ('ole_student', 'Ole Student'),  # ✅ New role
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    username = models.CharField(max_length=50, unique=True, blank=True)
    full_name = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # ✅ Phone number field for phone-based authentication
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    registration_group = models.ForeignKey(
        "RegistrationGroup",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # ✅ OLE-specific fields
    ole_class_level = models.ForeignKey(
        "teachers.OleClassLevel", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="ole_students"
    )
    ole_subjects = models.ManyToManyField(
        "teachers.OleSubject", blank=True, related_name="ole_students"
    )

    # ✅ Subscription support
    subscription_expires_on = models.DateField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role", "full_name"]

    objects = CustomUserManager()

    class Meta:
        indexes = [
            # `role` is filtered on nearly every role-scoped query and permission
            # check; without an index those become full table scans as the user
            # count grows.
            models.Index(fields=["role"], name="user_role_idx"),
            # subscription sweeps / "is this user still active" checks.
            models.Index(fields=["subscription_expires_on"], name="user_sub_expires_idx"),
            # counting/listing users within a registration group.
            models.Index(fields=["registration_group"], name="user_reg_group_idx"),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.username})"

    def save(self, *args, **kwargs):
        if self.role:
            self.role = self.role.lower()
        if not self.username:
            # ✅ Allow save without username (will be auto-generated)
            pass
        super().save(*args, **kwargs)


    def is_subscription_active(self):
        # A user may simply have no subscription yet; the related-object access
        # raises RelatedObjectDoesNotExist (a subclass of ObjectDoesNotExist).
        # The previous code caught OleStudentSubscription.DoesNotExist by a name
        # that wasn't imported here, so the guard itself raised NameError.
        from django.core.exceptions import ObjectDoesNotExist
        try:
            subscription = self.ole_subscription
        except ObjectDoesNotExist:
            return False
        if not subscription or not subscription.end_date:
            return False
        return subscription.end_date >= timezone.now()


class RegistrationGroup(models.Model):
    ACCOUNT_TYPES = [
        ('school', 'School'),
        ('home', 'Home'),
        ('referral', 'Referral'),
    ]

    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default="school")
    name = models.CharField(max_length=100, default="John Ken")
    location = models.CharField(max_length=100, default="Ikeja")
    state = models.CharField(max_length=100, default="Lagos")
    email = models.EmailField(default="email@example.com")
    slots_applied = models.PositiveIntegerField(default=1)
    slots_remaining = models.PositiveIntegerField(default=1)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')  # ✅ enforced
    subscription_expires = models.DateField(null=True, blank=True)  # ✅ New field
    referral_code = models.CharField(max_length=50, blank=True)
    account_details = models.TextField(blank=True, default="Not provided")

    created_at = models.DateTimeField(auto_now_add=True)

    state_code = models.CharField(max_length=10, blank=True)
    serial_prefix = models.CharField(max_length=10, blank=True)

    def save(self, *args, **kwargs):
        if not self.state_code and self.state:
            self.state_code = self.state[:2].upper()
        if not self.serial_prefix and self.account_type:
            self.serial_prefix = self.account_type[:3].upper()
        
        # ✅ Ensure new subscriptions get 30 days validity if not set
        if not self.subscription_expires:
            self.subscription_expires = timezone.now().date() + timedelta(days=30)

        super().save(*args, **kwargs)

    def decrease_slots(self, count=1):
        """
        Atomically consume `count` slots.

        The previous read-modify-write let two concurrent registrations both
        read the last slot and both succeed — overselling. This locks the row
        (select_for_update) inside a transaction so the check and decrement are
        a single atomic step.
        """
        from django.db import transaction

        with transaction.atomic():
            fresh = type(self).objects.select_for_update().get(pk=self.pk)
            if fresh.slots_remaining < count:
                raise ValueError("You don't have enough slots left, please buy more to continue")
            fresh.slots_remaining -= count
            fresh.save(update_fields=["slots_remaining"])
            self.slots_remaining = fresh.slots_remaining

    def __str__(self):
        return f"{self.name} ({self.account_type}) - {self.slots_remaining} slots"
    
    
    def is_subscription_active(self):
        return self.subscription_expires and self.subscription_expires >= timezone.now().date()



class StudentSlot(models.Model):
    main_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_slots')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    username = models.CharField(max_length=100, unique=True)
    # Bookkeeping table, not a login account. Kept blank; real credentials
    # live on CustomUser (hashed). Column retained to avoid a destructive drop.
    password = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.full_name}"



class OleStudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ole_profile')
    class_level = models.ForeignKey("teachers.OleClassLevel", on_delete=models.SET_NULL, null=True)
    subjects = models.ManyToManyField("teachers.OleSubject")

    def __str__(self):
        return f"{self.user.full_name} - {self.class_level.name if self.class_level else 'No Class'}"



class OleStudentSubscription(models.Model):
    PLAN_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='ole_subscription')
    plan_type = models.CharField(max_length=10, choices=PLAN_CHOICES)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def is_active(self):
        return self.end_date >= timezone.now()

    def __str__(self):
        return f"{self.user.email} - {self.plan_type} (Expires: {self.end_date.date()})"
    
    
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    duration_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    

class OleStudentSubjectAccess(models.Model):
    ole_student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ole_class_level = models.ForeignKey("teachers.OleClassLevel", on_delete=models.CASCADE)
    ole_subjects = models.ManyToManyField("teachers.OleSubject")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ole_student.email} - {self.ole_class_level.name}"


class AdminActionLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('other', 'Other'),
    ]

    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    email = models.EmailField()
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Admin Action Log"
        verbose_name_plural = "Admin Action Logs"

    def __str__(self):
        return f"{self.action_type} by {self.email} at {self.timestamp}"
    

class OlePaymentVerification(models.Model):
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference

    class Meta:
        verbose_name = "Payment Verification"
        verbose_name_plural = "Payment Verifications"

# Add to your existing models.py
class PhoneVerification(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if the verification code has expired"""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.phone_number} - {self.code} - {'Verified' if self.is_verified else 'Pending'}"