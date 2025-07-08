from django.contrib import admin

from django.contrib import admin
from .models import Payment, PaymentTransaction

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'tx_ref', 'amount', 'status', 'paid_at')
    search_fields = ('tx_ref', 'user__email')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('registration_group', 'transaction_id', 'amount', 'verified', 'status', 'timestamp')
    search_fields = ('transaction_id', 'tx_ref', 'registration_group__email')

