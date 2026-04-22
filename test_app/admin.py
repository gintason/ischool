# test_app/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
import pandas as pd
from .models import (
    Question,
    Test,
    TestSession,
    TestResult,
    StudentAnswer,
    Subject,
    Topic
)

# NEW: Inline admin for Topics under Subject
class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    fields = ['name', 'description', 'order']
    show_change_link = True

# NEW: Subject Admin with inline topics
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_level', 'created_at']
    list_filter = ['class_level']
    search_fields = ['name', 'description']
    inlines = [TopicInline]
    
    fieldsets = (
        ('Subject Information', {
            'fields': ('name', 'class_level', 'description')
        }),
    )

# NEW: Topic Admin for standalone management
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'order', 'created_at']
    list_filter = ['subject__class_level', 'subject']
    search_fields = ['name', 'subject__name']
    list_editable = ['order']
    
    fieldsets = (
        ('Topic Information', {
            'fields': ('name', 'subject', 'description', 'order')
        }),
    )

# Updated Question Admin
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question_type', 'get_subject', 'get_topic']
    list_filter = ['question_type']  # Remove the invalid filters for now
    search_fields = ['text']
    
    def get_subject(self, obj):
        if obj.test and obj.test.subject_fk:
            return obj.test.subject_fk.name
        elif obj.test and obj.test.subject:
            return obj.test.subject
        return '-'
    get_subject.short_description = 'Subject'
    
    def get_topic(self, obj):
        if obj.test and obj.test.topic_fk:
            return obj.test.topic_fk.name
        elif obj.test and obj.test.topic:
            return obj.test.topic
        return '-'
    get_topic.short_description = 'Topic'
    
    # Add custom URL for Excel upload
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-questions/', self.upload_questions, name='upload_questions'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        from django.contrib import messages
        from django.utils.safestring import mark_safe
        
        # Add a clickable button message
        messages.success(request, mark_safe(
            '<div style="background-color: #28a745; color: white; padding: 10px; border-radius: 5px; text-align: center;">'
            '📤 <strong>Quick Action:</strong> '
            '<a href="upload-questions/" style="color: white; font-weight: bold; text-decoration: underline;">'
            'Click here to upload questions from Excel</a>'
            '</div>'
        ))
        
        return super().changelist_view(request, extra_context=extra_context)
    
    
    def upload_questions(self, request):
        if request.method == 'POST':
            excel_file = request.FILES.get('excel_file')
            
            if not excel_file:
                messages.error(request, 'Please select an Excel file')
                return HttpResponseRedirect('../')
            
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'Please upload a valid Excel file (.xlsx or .xls)')
                return HttpResponseRedirect('../')
            
            try:
                df = pd.read_excel(excel_file)
                
                required_columns = ['subject_name', 'topic_name', 'class_level', 'question_text', 'question_type', 
                                'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
                
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f'Missing columns: {", ".join(missing_columns)}')
                    return HttpResponseRedirect('../')
                
                created_count = 0
                error_count = 0
                errors = []
                
                for index, row in df.iterrows():
                    try:
                        # Get or create Subject
                        subject, _ = Subject.objects.get_or_create(
                            name=row['subject_name'],
                            class_level=row['class_level']
                        )
                        
                        # Get or create Topic
                        topic, _ = Topic.objects.get_or_create(
                            name=row['topic_name'],
                            subject=subject
                        )
                        
                        # Get or create Test - FIXED: use created_by (not created_by_id)
                        test, created = Test.objects.get_or_create(
                            class_level=row['class_level'],
                            subject_fk=subject,
                            topic_fk=topic,
                            defaults={'created_by': request.user}
                        )
                        
                        # If test already exists but has no created_by, update it
                        if not created and not test.created_by:
                            test.created_by = request.user
                            test.save()
                        
                        # Create question
                        question = Question.objects.create(
                            test=test,
                            text=row['question_text'],
                            question_type=row['question_type'] if pd.notna(row['question_type']) else 'mcq',
                            option_a=str(row['option_a']) if pd.notna(row['option_a']) else '',
                            option_b=str(row['option_b']) if pd.notna(row['option_b']) else '',
                            option_c=str(row['option_c']) if pd.notna(row['option_c']) else '',
                            option_d=str(row['option_d']) if pd.notna(row['option_d']) else '',
                            correct_answer=str(row['correct_answer']) if pd.notna(row['correct_answer']) else '',
                        )
                        
                        created_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {index + 2}: {str(e)}")
                
                if created_count > 0:
                    messages.success(request, f'Successfully uploaded {created_count} questions!')
                
                if errors:
                    messages.warning(request, f'Completed with {error_count} errors. Details: {"; ".join(errors[:5])}')
                
            except Exception as e:
                messages.error(request, f'Error reading Excel file: {str(e)}')
            
            return HttpResponseRedirect('../')
        
        return render(request, 'admin/upload_questions.html', {
            'title': 'Upload Questions from Excel',
            'opts': self.model._meta,
        })
    

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['get_subject_name', 'get_topic_name', 'class_level', 'created_by', 'date_created']
    search_fields = ['subject_fk__name', 'topic_fk__name', 'subject', 'topic']
    list_filter = ['class_level', 'date_created']
    
    def get_subject_name(self, obj):
        if obj.subject_fk:
            return obj.subject_fk.name
        return obj.subject
    get_subject_name.short_description = 'Subject'
    
    def get_topic_name(self, obj):
        if obj.topic_fk:
            return obj.topic_fk.name
        return obj.topic
    get_topic_name.short_description = 'Topic'
    
    fieldsets = (
        ('Test Information', {
            'fields': ('class_level', 'subject_fk', 'topic_fk', 'subject', 'topic')
        }),
    )
    
    # Auto-set created_by to current user
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    # Filter form fields
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "topic_fk":
            kwargs["queryset"] = Topic.objects.select_related('subject').all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    

# Keep existing admin registrations for other models
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