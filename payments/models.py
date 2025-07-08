from django.db import models
from django.db import models
from django.contrib.auth import get_user_model
import users

User = get_user_model()

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tx_ref = models.CharField(max_length=100, unique=True)  # Transaction reference
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)  # e.g., success, failed
    payment_type = models.CharField(max_length=50, blank=True, null=True)  # optional
    paid_at = models.DateTimeField(auto_now_add=True)
    raw_response = models.JSONField()  # stores full Flutterwave response

    def __str__(self):
        return f"{self.user or 'Anonymous'} - {self.tx_ref} - {self.status}"


# payments/models.py

class PaymentTransaction(models.Model):
    registration_group = models.ForeignKey('users.RegistrationGroup', on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    tx_ref = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    verified = models.BooleanField(default=False)
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"
