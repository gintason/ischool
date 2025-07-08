from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import RegistrationSourceViewSet, StudentSlotViewSet, test_email_view, ContactOleMessageAPIView, ole_contact_submission, ola_contact_view
from .test_email_view import test_email  # adjust import path based on location
from . import views
from .views import frontend


router = DefaultRouter()
router.register(r'registration-sources', RegistrationSourceViewSet)
router.register(r'student-slots', StudentSlotViewSet)

app_name = 'core'

urlpatterns = [
    path('api/test-email/', test_email),  # ✅ Correct placement
    path("test-email/", test_email_view, name="test-email"),

    path('', include(router.urls)),
    path("ole-contact/", ContactOleMessageAPIView.as_view(), name="contact_ole"),
    path('ole-contact', ole_contact_submission, name='ole-contact'),
    path('ola-contact/', ola_contact_view, name='ola-contact'),

    re_path(r'^.*$', frontend),
    
]
