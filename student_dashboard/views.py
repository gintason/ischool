from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from datetime import date
from .serializers import StudentDashboardSerializer, TestResultSummarySerializer, RelatedStudentSerializer
from test_app.models import TestResult  # adjust app name
from users.models import CustomUser  # adjust as needed

class StudentDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "student":
            return Response({"detail": "Only students can access this dashboard."}, status=status.HTTP_403_FORBIDDEN)

        today = date.today()
        tests_taken_today = TestResult.objects.filter(student=user, created_at__date=today).count()
        recent_tests_qs = TestResult.objects.filter(student=user).order_by('-created_at')[:5]

        related_students_qs = CustomUser.objects.none()
        if user.registration_group:
            related_students_qs = CustomUser.objects.filter(
                registration_group=user.registration_group
            ).exclude(id=user.id)

        # Create context dictionary to pass to serializer
        context = {
            "request": request
        }

        data = {
            "user": user,
            "tests_taken_today": tests_taken_today,
            "tests_remaining_today": max(0, 6 - tests_taken_today),
            "recent_tests": recent_tests_qs,
            "related_students": related_students_qs
        }

        serializer = StudentDashboardSerializer(data, context=context)
        return Response(serializer.data)




class TestResultsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        results = TestResult.objects.filter(student=request.user).order_by('-created_at')
        serializer = TestResultSummarySerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



