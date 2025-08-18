# payments/urls.py
from django.urls import path
from .views import verify_paystack_payment, initiate_payment, verify_and_register, payment_callback

urlpatterns = [
    path('verify/', verify_paystack_payment, name='verify_paystack-payment'),
    path('initiate-payment/', initiate_payment),
    path('verify-and-register/', verify_and_register),  
    path("payment-callback/", payment_callback, name="payment_callback"),
 
]

