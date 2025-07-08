from django.contrib import admin
from .models import ParentProfile

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')

