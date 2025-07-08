from django.urls import path
from .views import SignUpAPIView

app_name = 'school'

urlpatterns = [
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    # other URLs
]


