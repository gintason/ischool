from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from users.models import CustomUser  # adjust if needed

# Constants
CLASS_CHOICES = [
    ("JSS1", "JSS1"),
    ("JSS2", "JSS2"),
    ("JSS3", "JSS3"),
    ("SSS1", "SSS1"),
    ("SSS2", "SSS2"),
    ("SSS3", "SSS3"),
]

QUESTION_TYPE_CHOICES = [
    ("mcq", "Multiple Choice"),
    ("theory", "Theory"),
]

SUBJECT_CHOICES = [
    ("Mathematics", "Mathematics"),
    ("English", "English"),
    ("Biology", "Biology"),
    ("Chemistry", "Chemistry"),
    ("Physics", "Physics"),
    ("Civic Education", "Civic Education"),
    ("Literature", "Literature"),
    # Extend as needed
]


class Test(models.Model):
    class_level = models.CharField(max_length=10, choices=CLASS_CHOICES, default="JSS1")  # Add this line
    subject = models.CharField(max_length=100, default="Mathematics")
    topic = models.CharField(max_length=100, default="Basic Science")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.topic}"


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions", default=1)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)
    text = models.TextField()
    
    # MCQ-specific
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=1, blank=True, null=True)  # A/B/C/D

    # Theory-specific
    expected_answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.text[:50]} - Class: {self.test.class_level}"


class TestSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    class_level = models.CharField(max_length=10, choices=CLASS_CHOICES)
    subject = models.CharField(max_length=100)
    topic = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    duration = models.FloatField(null=True, blank=True) # ← NEW

    def __str__(self):
        return f"TestSession {self.id} - {self.student.username}"


class TestResult(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, default="Mathematics")  # ✅ New field
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_questions = models.IntegerField(default=0)  # Optional: store total for reuse

    def __str__(self):
        return f"Result for {self.student.username} - {self.test_session.subject}"


class StudentAnswer(models.Model):
    result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    # MCQ
    selected_option = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(blank=True, null=True)

    # Theory
    theory_answer = models.TextField(blank=True, null=True)
    theory_match_percentage = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Answer by {self.result.student.username} to Q{self.question.id}"




 