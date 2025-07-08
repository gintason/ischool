from django.urls import path
from .views import create_student_slots
from .views import (UserRegistrationView, 
                    OleStudentLoginView, OleStudentDashboardView,
                    StudentLoginView, 
                    VerifyOleStudentPaymentView, 
                    OleStudentRegistrationView, 
                    AdminOnlyView, UserMeView, 
                    TeacherOnlyView,CustomTokenObtainPairView, 
                    RegistrationGroupView, TeacherTestManagementView, 
                    StudentResultsView, ParentResultsView, StudentRegistrationView, CustomLoginView,
                    get_student_lesson_detail, OleStudentLessonHistoryView, OleStudentMaterialListView, 
                    RenewSubscriptionAPIView, SubscriptionPlanListAPIView, initialize_subscription_payment, 
                    verify_payment, log_student_join, log_student_leave)
# urls.py
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from dj_rest_auth.views import LoginView


urlpatterns = [
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
]

app_name = 'users'

urlpatterns = [

    # User registration endpoint
    path("register/", UserRegistrationView.as_view(), name="user-register"),

    path("register/", StudentRegistrationView.as_view(), name="register"),

    path("login/", CustomLoginView.as_view(), name="login"),
    
    # Login endpoint (JWT token generation)
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Registration group (School/Home/Referral) creation
    path('create-group/', RegistrationGroupView.as_view(), name='create-group'),
    
    # Teacher test management (restricted to teachers)
    path('teacher/tests/', TeacherTestManagementView.as_view(), name='teacher-tests'),
    
    # Student results (restricted to students)
    path('student/results/', StudentResultsView.as_view(), name='student-results'),
    
    # Parent results (restricted to parents)
    path('parent/results/', ParentResultsView.as_view(), name='parent-results'),

    path("auth/login/", StudentLoginView.as_view(), name="student-login"),

    path('student-slots/', create_student_slots, name='create-student-slots'),

    path("admin-only/", AdminOnlyView.as_view(), name="admin_only"),

    path("teacher-only/", TeacherOnlyView.as_view(), name="teacher_only"),

    path("me/", UserMeView.as_view(), name="me"),  # 👈 Add this line

    path("ole-student/register/", OleStudentRegistrationView.as_view(), name="ole_student_register"),

    path("ole-student/verify-payment/", VerifyOleStudentPaymentView.as_view(), name="ole-payment-verify"),

    path('ole-student/login/', OleStudentLoginView.as_view(), name='ole_student_login'),
    path("ole-student/dashboard/", OleStudentDashboardView.as_view(), name="ole-student-dashboard"),
    path("ole-student/lesson/<int:id>/", get_student_lesson_detail, name="lesson-detail"),
    path("ole-student/lesson-history/", OleStudentLessonHistoryView.as_view(), name="ole_lesson_history"),
    path("ole-student/materials/", OleStudentMaterialListView.as_view(), name="ole_student_materials"),
    path("ole-student/renew-subscription/", RenewSubscriptionAPIView.as_view(), name="renew_subscription"),
    path("ole-student/subscription-plans/", SubscriptionPlanListAPIView.as_view(), name="subscription_plans"),
    path("ole-student/init-subscription-payment/", initialize_subscription_payment, name="init_subscription_payment"),
    path("ole-student/verify-subscription-payment/", verify_payment, name="verify_subscription_payment"),  # ✅ ADD THIS
    path('log-join/', log_student_join, name='log_student_join'),
    path('log-leave/', log_student_leave, name='log_student_leave'),
    path('auth/token/', LoginView.as_view(), name='rest_login'),  # or dj-rest-auth login
]
