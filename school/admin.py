from django.contrib import admin
from .models import School, Home, AccreditedReferral

class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'established_year', 'state', 'num_slots']
    search_fields = ['name']

class HomeAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'state', 'num_slots']
    search_fields = ['name']

class AccreditedReferralAdmin(admin.ModelAdmin):
    list_display = ['name', 'referral_code', 'state', 'num_slots']
    search_fields = ['name']

admin.site.register(School, SchoolAdmin)
admin.site.register(Home, HomeAdmin)
admin.site.register(AccreditedReferral, AccreditedReferralAdmin)


