from django.contrib import admin
from .models import (
    Question,
    Test,
    TestSession,
    TestResult,
    StudentAnswer,
)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question_type']
    list_filter = [ 'question_type']
    search_fields = ['text']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['subject', 'topic', 'created_by', 'date_created']
    search_fields = ['subject', 'topic']
    list_filter = ['subject', 'date_created']


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'class_level', 'subject', 'topic', 'created_at', 'completed']
    list_filter = ['class_level', 'subject', 'completed']
    search_fields = ['student__username', 'subject', 'topic']


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['result', 'question', 'selected_option', 'is_correct', 'theory_match_percentage']
    list_filter = ['is_correct']
    search_fields = ['result__student__username', 'question__text']

class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    readonly_fields = ['question', 'selected_option', 'is_correct', 'theory_answer', 'theory_match_percentage']

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'test_session', 'score', 'created_at']
    search_fields = ['student__username', 'test_session__subject']
    list_filter = ['created_at']
    inlines = [StudentAnswerInline]


      

