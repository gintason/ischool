from django.db import models
from django.conf import settings  # ✅ Use settings.AUTH_USER_MODEL

class RegistrationSource(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('school', 'School'),
        ('home', 'Home'),
        ('referral', 'Accredited Referral'),
    ]

    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    number_of_slots = models.PositiveIntegerField()
    payment_proof = models.FileField(upload_to='payment_proofs/')
    account_details = models.TextField(blank=True, null=True)  # Only for referrals
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.source_type.title()}: {self.name} ({self.state})"


class StudentSlot(models.Model):
    registration_source = models.ForeignKey(RegistrationSource, on_delete=models.CASCADE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Fixed
    serial_number = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.user.email} - {self.serial_number}"

# core/models.py


class ContactOleMessage(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"



class ContactOla(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"