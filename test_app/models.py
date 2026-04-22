# test_app/models.py - Update with a safer approach
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from users.models import CustomUser

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

# New models
class Subject(models.Model):
    name = models.CharField(max_length=100)
    class_level = models.CharField(max_length=10, choices=CLASS_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'class_level']
    
    def __str__(self):
        return f"{self.name} ({self.class_level})"

class Topic(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'subject']
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.subject.name})"

# Updated Test model - KEEP old fields temporarily
class Test(models.Model):
    class_level = models.CharField(max_length=10, choices=CLASS_CHOICES, default="JSS1")
    
    # Keep old fields for migration
    subject_old = models.CharField(max_length=100, default="Mathematics", db_column='subject')
    topic_old = models.CharField(max_length=100, default="Basic Science", db_column='topic')
    
    # Add new foreign key fields
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, related_name='tests')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True, related_name='tests')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.subject and self.topic:
            return f"{self.subject.name} - {self.topic.name}"
        return f"{self.subject_old} - {self.topic_old}"

# Keep Question model same but update test reference
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions", default=1)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)
    text = models.TextField()
    
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=1, blank=True, null=True)
    expected_answer = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.test and self.test.subject:
            return f"{self.text[:50]} - {self.test.subject.name}"
        return f"{self.text[:50]}"

# Keep other models as they were
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
    duration = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"TestSession {self.id} - {self.student.username}"

class TestResult(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, default="Mathematics")
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_questions = models.IntegerField(default=0)

    def __str__(self):
        return f"Result for {self.student.username} - {self.test_session.subject}"

class StudentAnswer(models.Model):
    result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(blank=True, null=True)
    theory_answer = models.TextField(blank=True, null=True)
    theory_match_percentage = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Answer by {self.result.student.username} to Q{self.question.id}"