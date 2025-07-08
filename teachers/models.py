
# teachers/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.timezone import now
from django.conf import settings
from django.utils.text import slugify

User = get_user_model()


class ApplicationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SHORTLISTED = 'shortlisted', 'Shortlisted'
    REJECTED = 'rejected', 'Rejected'
    HIRED = 'hired', 'Hired'


class InterviewOutcome(models.TextChoices):
    PASSED = 'passed', 'Passed'
    FAILED = 'failed', 'Failed'
    PENDING = 'pending', 'Pending'


class TeacherApplication(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    subjects = models.CharField(max_length=255)
    availability = models.TextField()
    cv = models.FileField(upload_to='teacher_cvs/')
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"


# OLE Curriculum Structure
class OleClassLevel(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g. "JSS1", "SS2"

    def __str__(self):
        return self.name
    

class OleSubject(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g. "Mathematics", "English"

    def __str__(self):
        return self.name
    

class OleTopic(models.Model):
    subject = models.ForeignKey(OleSubject, on_delete=models.CASCADE, related_name="topics")
    class_level = models.ForeignKey(OleClassLevel, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    reference_material = models.FileField(upload_to="ole_topic_refs/", blank=True, null=True)

    class Meta:
        unique_together = ('subject', 'class_level', 'title')

    def __str__(self):
        return f"{self.title} ({self.subject.name} - {self.class_level.name})"
    

class OleStudentTopicHistory(models.Model):
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    topic = models.ForeignKey(OleTopic, on_delete=models.CASCADE)
    viewed_on = models.DateTimeField(auto_now_add=True)
    

# Teacher-to-Class Assignment
class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    subject = models.ForeignKey(OleSubject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(OleClassLevel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher.full_name} - {self.subject.name} ({self.class_level.name})"
    

# Schedule for live classes
class LiveClassSchedule(models.Model):
    subject = models.ForeignKey(OleSubject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(OleClassLevel, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.subject.name} ({self.class_level.name}) - {self.date} {self.start_time}"
    

# Actual lesson plan used during a live class
class OleLessonPlan(models.Model):
    subject = models.ForeignKey(OleSubject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(OleClassLevel, on_delete=models.CASCADE)
    topic = models.ForeignKey('OleTopic', on_delete=models.CASCADE, related_name='lesson_plans')
    reference_material = models.FileField(upload_to="lesson_references/", blank=True, null=True)

    def __str__(self):
        return f"{self.topic} - {self.subject.name} ({self.class_level.name})"
    

# Live class session connected to a schedule
class LiveClassSession(models.Model):
    schedule = models.OneToOneField(LiveClassSchedule, on_delete=models.CASCADE)
    lesson_plan = models.ForeignKey(OleLessonPlan, on_delete=models.SET_NULL, null=True, blank=True)
    meeting_link = models.URLField(blank=True, null=True)  # Zoom/WebRTC link
    started_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Session: {self.schedule.subject.name} on {self.schedule.date}"
    

# Student attendance during a live session
class AttendanceLog(models.Model):
    session = models.ForeignKey(LiveClassSession, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)  # 👈 Add this line

    def __str__(self):
        return f"{self.student.full_name} joined {self.session}"



class OleStudentMatch(models.Model):
    schedule = models.ForeignKey(
        LiveClassSchedule, 
        on_delete=models.CASCADE, 
        related_name='matched_students'
    )
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'ole_student'}
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('schedule', 'student')  # ✅ Reinstate uniqueness

    def __str__(self):
        return f"{self.student.full_name} matched to {self.schedule}"

    

class SessionReference(models.Model):
    session = models.OneToOneField(LiveClassSession, on_delete=models.CASCADE)
    chapter = models.ForeignKey('elibrary.ELibraryChapter', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.session} → {self.chapter.title}"


class StudentAttendanceSummary(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'ole_student'})
    week_start = models.DateField()
    week_end = models.DateField()
    total_classes_attended = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('student', 'week_start')

    def __str__(self):
        return f"{self.student.full_name} ({self.week_start} - {self.week_end}): {self.total_classes_attended}"


class TeacherLessonSummary(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    week_start = models.DateField()
    week_end = models.DateField()
    total_lessons_taken = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('teacher', 'week_start')

    def __str__(self):
        return f"{self.teacher.full_name} ({self.week_start} - {self.week_end}): {self.total_lessons_taken}"
    


class StudentLessonSummary(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'ole_student'})
    week_start = models.DateField()
    week_end = models.DateField()
    total_classes_attended = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('student', 'week_start')

    def __str__(self):
        return f"{self.student.full_name} ({self.week_start} - {self.week_end}): {self.total_classes_attended}"



class TeacherInterview(models.Model):
    application = models.OneToOneField(TeacherApplication, on_delete=models.CASCADE, related_name='interview')
    scheduled_date = models.DateTimeField()
    outcome = models.CharField(max_length=10, choices=InterviewOutcome.choices, default=InterviewOutcome.PENDING)
    notes = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview for {self.application.full_name} - {self.outcome}"


# Lesson Material (e.g., PDF, Video)
class OleMaterial(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="ole_materials/", blank=True, null=True)
    subject = models.ForeignKey(OleSubject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(OleClassLevel, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# A Scheduled Lesson
class OleLesson(models.Model):
    class_level = models.ForeignKey(OleClassLevel, on_delete=models.CASCADE)
    subject = models.ForeignKey(OleSubject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    materials = models.ManyToManyField(OleMaterial, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_chat_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.topic} - {self.subject.name}"


class TeacherPayroll(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    month = models.DateField()  # Usually the first day of the month
    total_lessons = models.PositiveIntegerField(default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'month')

    def __str__(self):
        return f"{self.teacher.full_name} - {self.month.strftime('%B %Y')} - ₦{self.amount_paid}"
