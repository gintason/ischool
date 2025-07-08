from django.urls import path
from .views import StudentDashboardView
from . import views

urlpatterns = [
    path("", StudentDashboardView.as_view(), name="student-dashboard"),
    path('my-results/', views.TestResultsListView.as_view(), name='my-results'),

]