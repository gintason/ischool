# student_dashboard/serializers.py

from rest_framework import serializers

class TestResultSummarySerializer(serializers.Serializer):
    subject = serializers.CharField()
    score = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_questions = serializers.IntegerField()
    date_taken = serializers.DateTimeField(source="created_at")


class RelatedStudentSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    username = serializers.CharField()


class StudentDashboardSerializer(serializers.Serializer):
    full_name = serializers.CharField(source="user.full_name")
    username = serializers.CharField(source="user.username")
    email = serializers.EmailField(source="user.email")
    profile_photo = serializers.ImageField(source="user.profile_photo", allow_null=True, required=False)
    last_login = serializers.DateTimeField(source="user.last_login")
    date_joined = serializers.DateTimeField(source="user.date_joined")
    tests_taken_today = serializers.IntegerField()
    tests_remaining_today = serializers.IntegerField()

    recent_tests = serializers.SerializerMethodField()
    related_students = serializers.SerializerMethodField()

    def get_recent_tests(self, obj):
        return TestResultSummarySerializer(obj['recent_tests'], many=True, context=self.context).data

    def get_related_students(self, obj):
        return RelatedStudentSerializer(obj['related_students'], many=True, context=self.context).data



