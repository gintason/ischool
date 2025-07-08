from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import RegistrationSource, StudentSlot, ContactOleMessage

@admin.register(RegistrationSource)
class RegistrationSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'state', 'number_of_slots', 'is_verified')
    list_filter = ('source_type', 'state', 'is_verified')
    search_fields = ('name', 'state', 'account_details')
    readonly_fields = ('is_verified',)
    ordering = ('-id',)


@admin.register(StudentSlot)
class StudentSlotAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'serial_number', 'registration_source')
    list_filter = ('registration_source__source_type',)
    search_fields = ('serial_number', 'user__email')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Student Email'


@admin.register(ContactOleMessage)
class ContactOleMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "created_at")
    search_fields = ("full_name", "email", "message")