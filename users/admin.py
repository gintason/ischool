# admin.py

from django.contrib import admin
from .models import CustomUser, RegistrationGroup, AdminActionLog
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import OleStudentSubscription  # adjust if needed
from django.utils.html import format_html
from django.utils import timezone


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'full_name', 'role', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'full_name')
    list_filter = ('role', 'is_staff', 'is_active')
    ordering = ('email',)
    readonly_fields = ('username',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'role', 'registration_group')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login',)}),
        ('System Info', {'fields': ('username',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'registration_group', 'password1', 'password2'),
        }),
    )

@admin.register(RegistrationGroup)
class RegistrationGroupAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'account_type', 'name', 'location', 'state', 'state_code', 
        'serial_prefix', 'slots_applied', 'slots_remaining', 'referral_code', 'account_details', 'created_at'
    )
    list_filter = ('account_type', 'state', 'account_type')
    readonly_fields = ('state_code', 'serial_prefix', 'created_at')
    search_fields = ('name', 'email', 'referral_code')

    def get_readonly_fields(self, request, obj=None):
        # Make fields read-only once an object is created
        if obj:
            return self.readonly_fields + ('account_details',)  # Adding account details to readonly when an object is already created.
        return self.readonly_fields
    

@admin.register(OleStudentSubscription)
class OleStudentSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_type', 'start_date', 'end_date', 'active_status']
    list_filter = ['plan_type', 'start_date', 'end_date']

    def active_status(self, obj):
        return obj.is_active()
    active_status.boolean = True
    active_status.short_description = 'Active?'


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ("action_type", "email", "short_details", "timestamp")
    list_filter = ("action_type", "timestamp")
    search_fields = ("email", "details")
    ordering = ("-timestamp",)

    def short_details(self, obj):
        return (obj.details[:50] + "...") if obj.details and len(obj.details) > 50 else obj.details
    short_details.short_description = "Details"