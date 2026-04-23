# test_app/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
import pandas as pd
import json
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
    list_filter = ['question_type']
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
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-questions/', self.upload_questions, name='upload_questions'),
            path('upload-json/', self.upload_json, name='upload_json'),  # Add JSON upload URL
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        from django.contrib import messages
        from django.utils.safestring import mark_safe
        
        extra_context = extra_context or {}
        extra_context['upload_url'] = 'upload-questions/'
        
        # Add buttons for both upload methods
        messages.info(request, mark_safe(
            '<div style="display: flex; gap: 10px; margin-bottom: 10px;">'
            '<a href="upload-questions/" style="background-color: #28a745; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px;">'
            '📊 Upload Excel/CSV'
            '</a>'
            '<a href="upload-json/" style="background-color: #007bff; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px;">'
            '📄 Upload JSON'
            '</a>'
            '</div>'
        ))
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def upload_json(self, request):
        """Handle JSON file upload for questions"""
        if request.method == 'POST':
            json_file = request.FILES.get('json_file')
            
            if not json_file:
                messages.error(request, 'Please select a JSON file')
                return HttpResponseRedirect('../')
            
            # Check file extension
            if not json_file.name.endswith('.json'):
                messages.error(request, 'Please upload a valid JSON file (.json)')
                return HttpResponseRedirect('../')
            
            try:
                # Read and parse JSON file
                file_content = json_file.read().decode('utf-8')
                data = json.loads(file_content)
                
                # Handle both array and object formats
                if isinstance(data, dict):
                    # If it's a dict, look for questions key
                    questions_data = data.get('questions', [])
                elif isinstance(data, list):
                    questions_data = data
                else:
                    messages.error(request, 'Invalid JSON format. Expected array or object with "questions" key.')
                    return HttpResponseRedirect('../')
                
                if not questions_data:
                    messages.error(request, 'No questions found in JSON file')
                    return HttpResponseRedirect('../')
                
                created_count = 0
                error_count = 0
                errors = []
                
                for index, q in enumerate(questions_data):
                    try:
                        # Extract question data with defaults
                        subject_name = q.get('subject_name', '')
                        topic_name = q.get('topic_name', '')
                        class_level = q.get('class_level', '').upper()
                        question_text = q.get('question_text', '')
                        question_type = q.get('question_type', 'mcq').lower()
                        option_a = q.get('option_a', '')
                        option_b = q.get('option_b', '')
                        option_c = q.get('option_c', '')
                        option_d = q.get('option_d', '')
                        correct_answer = q.get('correct_answer', '')
                        
                        # Validate required fields
                        if not subject_name:
                            errors.append(f"Question {index + 1}: Missing subject_name")
                            error_count += 1
                            continue
                        if not topic_name:
                            errors.append(f"Question {index + 1}: Missing topic_name")
                            error_count += 1
                            continue
                        if not class_level:
                            errors.append(f"Question {index + 1}: Missing class_level")
                            error_count += 1
                            continue
                        if not question_text:
                            errors.append(f"Question {index + 1}: Missing question_text")
                            error_count += 1
                            continue
                        
                        # Get or create Subject
                        subject, _ = Subject.objects.get_or_create(
                            name=subject_name,
                            class_level=class_level
                        )
                        
                        # Get or create Topic
                        topic, _ = Topic.objects.get_or_create(
                            name=topic_name,
                            subject=subject
                        )
                        
                        # Get or create Test
                        test, created = Test.objects.get_or_create(
                            class_level=class_level,
                            subject_fk=subject,
                            topic_fk=topic,
                            defaults={
                                'created_by': request.user,
                                'subject': subject_name,
                                'topic': topic_name
                            }
                        )
                        
                        if not created and not test.created_by:
                            test.created_by = request.user
                            test.save()
                        
                        # Create Question
                        Question.objects.create(
                            test=test,
                            text=question_text,
                            question_type=question_type,
                            option_a=option_a,
                            option_b=option_b,
                            option_c=option_c,
                            option_d=option_d,
                            correct_answer=str(correct_answer).upper() if correct_answer else ''
                        )
                        
                        created_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Question {index + 1}: {str(e)}")
                
                # Show results
                if created_count > 0:
                    messages.success(request, f'✅ Successfully uploaded {created_count} questions from JSON!')
                
                if error_count > 0:
                    messages.warning(request, f'⚠️ {error_count} errors. Details: {"; ".join(errors[:5])}')
                
            except json.JSONDecodeError as e:
                messages.error(request, f'Invalid JSON format: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error reading JSON file: {str(e)}')
            
            return HttpResponseRedirect('../')
        
        # GET request - show upload form
        return render(request, 'admin/upload_json.html', {
            'title': 'Upload Questions from JSON',
            'opts': self.model._meta,
        })
    
    def upload_questions(self, request):
        if request.method == 'POST':
            excel_file = request.FILES.get('excel_file')

            if not excel_file:
                messages.error(request, 'Please select an Excel file')
                return HttpResponseRedirect('../')

            # Check file extension
            file_ext = excel_file.name.split('.')[-1].lower()
            if file_ext not in ['xlsx', 'xls', 'csv']:
                messages.error(
                    request,
                    'Please upload a valid file (.xlsx, .xls or .csv)'
                )
                return HttpResponseRedirect('../')

            try:
                import pandas as pd
                from io import BytesIO

                # Read uploaded file
                file_data = BytesIO(excel_file.read())

                # Try to read file safely
                try:
                    if file_ext == 'csv':
                        file_data.seek(0)
                        df = pd.read_csv(file_data)

                    else:
                        file_data.seek(0)

                        # Load workbook first
                        xls = pd.ExcelFile(file_data, engine='openpyxl')

                        # FIX: No worksheet found
                        if not xls.sheet_names:
                            messages.error(
                                request,
                                'This Excel file has no worksheets. '
                                'Please open it and save again as a new .xlsx file.'
                            )
                            return HttpResponseRedirect('../')

                        # Read first sheet
                        df = pd.read_excel(
                            xls,
                            sheet_name=xls.sheet_names[0]
                        )

                except Exception as e:
                    messages.error(
                        request,
                        f'Could not read file. Please ensure it is a valid Excel/CSV file. Error: {str(e)}'
                    )
                    return HttpResponseRedirect('../')

                # Check if dataframe is empty
                if df.empty:
                    messages.error(
                        request,
                        'File is empty. Please add data to your file.'
                    )
                    return HttpResponseRedirect('../')

                # Clean column names
                df.columns = df.columns.str.lower().str.strip()

                # Required columns
                required_columns = [
                    'subject_name',
                    'topic_name',
                    'class_level',
                    'question_text',
                    'question_type',
                    'option_a',
                    'option_b',
                    'option_c',
                    'option_d',
                    'correct_answer'
                ]

                # Check missing columns
                missing_columns = [
                    col for col in required_columns if col not in df.columns
                ]

                if missing_columns:
                    messages.error(
                        request,
                        f'Missing columns: {", ".join(missing_columns)}. '
                        f'Found columns: {list(df.columns)}'
                    )
                    return HttpResponseRedirect('../')

                created_count = 0
                error_count = 0
                errors = []

                # Process rows
                for index, row in df.iterrows():
                    try:
                        subject_name = row['subject_name']
                        topic_name = row['topic_name']
                        class_level = row['class_level']
                        question_text = row['question_text']
                        question_type = row['question_type']
                        option_a = row['option_a']
                        option_b = row['option_b']
                        option_c = row['option_c']
                        option_d = row['option_d']
                        correct_answer = row['correct_answer']

                        # Skip empty rows
                        if pd.isna(question_text) or str(question_text).strip() == '':
                            continue

                        # Convert safely
                        subject_name = str(subject_name).strip() if not pd.isna(subject_name) else ''
                        topic_name = str(topic_name).strip() if not pd.isna(topic_name) else ''
                        class_level = str(class_level).strip().upper() if not pd.isna(class_level) else ''
                        question_text = str(question_text).strip()

                        # Validate
                        if not subject_name:
                            errors.append(f"Row {index + 2}: Missing subject_name")
                            error_count += 1
                            continue

                        if not topic_name:
                            errors.append(f"Row {index + 2}: Missing topic_name")
                            error_count += 1
                            continue

                        if not class_level:
                            errors.append(f"Row {index + 2}: Missing class_level")
                            error_count += 1
                            continue

                        # Question type
                        if pd.isna(question_type) or not question_type:
                            question_type = 'mcq'
                        else:
                            question_type = str(question_type).lower().strip()
                            if question_type not in ['mcq', 'theory']:
                                question_type = 'mcq'

                        # Subject
                        subject, _ = Subject.objects.get_or_create(
                            name=subject_name,
                            class_level=class_level
                        )

                        # Topic
                        topic, _ = Topic.objects.get_or_create(
                            name=topic_name,
                            subject=subject
                        )

                        # Test
                        test, created = Test.objects.get_or_create(
                            class_level=class_level,
                            subject_fk=subject,
                            topic_fk=topic,
                            defaults={
                                'created_by': request.user,
                                'subject': subject_name,
                                'topic': topic_name
                            }
                        )

                        if not created and not test.created_by:
                            test.created_by = request.user
                            test.save()

                        # Options
                        opt_a = str(option_a).strip() if not pd.isna(option_a) else ''
                        opt_b = str(option_b).strip() if not pd.isna(option_b) else ''
                        opt_c = str(option_c).strip() if not pd.isna(option_c) else ''
                        opt_d = str(option_d).strip() if not pd.isna(option_d) else ''
                        correct = str(correct_answer).strip().upper() if not pd.isna(correct_answer) else ''

                        # Create question
                        Question.objects.create(
                            test=test,
                            text=question_text,
                            question_type=question_type,
                            option_a=opt_a,
                            option_b=opt_b,
                            option_c=opt_c,
                            option_d=opt_d,
                            correct_answer=correct
                        )

                        created_count += 1

                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {index + 2}: {str(e)}")

                # Results
                if created_count > 0:
                    messages.success(
                        request,
                        f'✅ Successfully uploaded {created_count} questions!'
                    )

                if error_count > 0:
                    messages.warning(
                        request,
                        f'⚠️ {error_count} errors. First few: {"; ".join(errors[:5])}'
                    )

                if created_count == 0 and error_count == 0:
                    messages.warning(
                        request,
                        'No questions found in the file. Please check your data.'
                    )

            except Exception as e:
                import traceback
                traceback.print_exc()
                messages.error(
                    request,
                    f'Error reading file: {str(e)}'
                )

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