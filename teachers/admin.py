# teachers/admin.py
from django.utils.html import format_html
from django.contrib import admin, messages
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import UserManager
from django.utils.crypto import get_random_string
from .services.scheduler import auto_schedule_classes
from django import forms
import csv
from django.http import HttpResponse
from .models import (
    TeacherApplication,
    ApplicationStatus,
    OleSubject,
    OleClassLevel,
    OleTopic,
    TeacherAssignment,
    LiveClassSchedule,
    LiveClassSession,
    AttendanceLog, TeacherInterview,
    OleStudentMatch, TeacherPayroll, OleLessonPlan
)
from users.models import CustomUser
from emails.sendgrid_email import send_email
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta



@admin.register(TeacherApplication)
class TeacherApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'status', 'applied_at']
    list_filter = ['status']
    search_fields = ['full_name', 'email']
    actions = ['mark_as_hired']

    def mark_as_hired(self, request, queryset):
        hired_count = 0
        skipped_emails = []

        for application in queryset:
            if application.status != ApplicationStatus.HIRED:
                if CustomUser.objects.filter(email=application.email).exists():
                    skipped_emails.append(application.email)
                    continue

                password = get_random_string(length=10)  # ✅ generate password here
              

                user = CustomUser.objects.create_user(
                    email=application.email,
                    full_name=application.full_name,
                    password=password,
                    role='teacher',
                )

                application.status = ApplicationStatus.HIRED
                application.save()

                subject = "Welcome to iSchool Ole – You're Hired!"
                message = (
                    f"Dear {user.full_name},\n\n"
                    f"You’ve been hired as a teacher on iSchool Ole.\n\n"
                    f"Login credentials:\n"
                    f"Email: {user.email}\n"
                    f"Password: {password}\n\n"
                    f"To Login, visit: www.ischool.ng/teacher/login and start teaching.\n\n"
                    f"– iSchool Ole Team"
                )

                send_mail(
                     subject,
                     message,
                     "noreply@ischool.ng",  # from_email
                     [user.email],          # recipient list
                     fail_silently=False,
                            )

                hired_count += 1

        if hired_count:
            self.message_user(request, f"✅ {hired_count} teacher(s) hired and notified.", level=messages.SUCCESS)

        if skipped_emails:
            self.message_user(request, f"⚠️ Skipped existing users: {', '.join(skipped_emails)}", level=messages.WARNING)

    mark_as_hired.short_description = "Hire selected teachers and create accounts"
    


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'student_name',
        'subject',
        'class_level',
        'session',
        'joined_at'
    ]
    list_filter = ['session__schedule__subject', 'session__schedule__class_level', 'joined_at']
    search_fields = ['student__full_name', 'student__email']

    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Student'

    def subject(self, obj):
        return obj.session.schedule.subject.name
    subject.short_description = 'Subject'

    def class_level(self, obj):
        return obj.session.schedule.class_level.name
    class_level.short_description = 'Class Level'

# ✅ Inline must be defined before it's referenced below
class OleStudentMatchInline(admin.TabularInline):
    model = OleStudentMatch
    extra = 0
    readonly_fields = ['student', 'assigned_at']
    can_delete = False
    verbose_name = "Matched Student"
    verbose_name_plural = "Matched Students"

@admin.register(LiveClassSchedule)
class LiveClassScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'teacher_email', 
        'subject_name', 
        'class_level_name', 
        'start_time', 
        'end_time', 
        'date',  # ✅ Added date to see when class happens
        'total_matched_students',
        'auto_match_status'  # ✅ NEW: Shows if auto-matched
    ]
    list_filter = ['class_level', 'subject', 'teacher', 'date']  # ✅ Added date filter
    search_fields = ['teacher__email', 'subject__name', 'class_level__name']
    actions = ['run_auto_scheduler', 'force_rematch_students', 'show_matching_details']  # ✅ NEW actions
    inlines = [OleStudentMatchInline]
    readonly_fields = ['match_summary', 'match_timestamp']  # ✅ NEW: Show match details in detail view

    def subject_name(self, obj):
        return obj.subject.name
    subject_name.short_description = 'Subject'
    subject_name.admin_order_field = 'subject__name'  # ✅ Allow sorting

    def class_level_name(self, obj):
        return obj.class_level.name
    class_level_name.short_description = 'Class Level'
    class_level_name.admin_order_field = 'class_level__name'  # ✅ Allow sorting

    def teacher_email(self, obj):
        return obj.teacher.email
    teacher_email.short_description = 'Teacher Email'
    teacher_email.admin_order_field = 'teacher__email'  # ✅ Allow sorting

    def total_matched_students(self, obj):
        count = obj.matched_students.count()
        if count > 0:
            # Color code based on count
            if count >= 10:
                color = 'green'
            elif count >= 5:
                color = 'orange'
            else:
                color = 'red'
            return format_html('<span style="color: {}; font-weight: bold;">{} student(s)</span>', color, count)
        return format_html('<span style="color: gray;">0 students</span>')
    total_matched_students.short_description = '📚 Matched Students'
    total_matched_students.admin_order_field = 'matched_students__count'

    def auto_match_status(self, obj):
        """Show if this schedule was automatically matched"""
        if obj.matched_students.exists():
            # Check when first student was matched
            first_match = obj.matched_students.first()
            if first_match:
                # If matched within 5 minutes of creation, assume auto-match
                time_diff = first_match.assigned_at - (obj.date if hasattr(obj, 'created_at') else timezone.now())
                if time_diff.total_seconds() < 300:  # 5 minutes
                    return format_html('<span style="color: green;">✅ Auto-matched</span>')
                return format_html('<span style="color: blue;">✓ Manually matched</span>')
        return format_html('<span style="color: orange;">⚠️ No matches yet</span>')
    auto_match_status.short_description = 'Match Status'

    def match_summary(self, obj):
        """Show detailed match summary in detail view"""
        matches = obj.matched_students.select_related('student').all()
        
        if not matches:
            return format_html(
                '<div style="padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107;">'
                '<strong>⚠️ No students matched yet.</strong><br>'
                'Click "Force Re-match" below to automatically match students.'
                '</div>'
            )
        
        # Count matches
        total_matches = matches.count()
        
        # Get unique class levels (should all be same)
        class_levels = set(match.student.ole_class_level.name for match in matches if match.student.ole_class_level)
        
        # Get unique subjects (should all be same)
        subjects = set(match.student.ole_subjects.filter(id=obj.subject.id).exists() for match in matches)
        
        # Show recent matches (last 10)
        recent_matches = matches.order_by('-assigned_at')[:10]
        
        html = f'''
        <div style="padding: 15px; background: #d4edda; border-left: 4px solid #28a745; margin-bottom: 10px;">
            <strong>✅ Match Summary:</strong><br>
            Total Matched Students: <strong>{total_matches}</strong><br>
            Class Level: {', '.join(class_levels) if class_levels else 'Not specified'}<br>
            Auto-match Status: <strong>Enabled</strong>
        </div>
        
        <div style="padding: 15px; background: #e7f3ff; border-left: 4px solid #2196F3;">
            <strong>👨‍🎓 Recently Matched Students:</strong>
            <ul style="margin: 10px 0 0 20px;">
        '''
        
        for match in recent_matches:
            html += f'<li><strong>{match.student.full_name}</strong> ({match.student.email}) - Matched at {match.assigned_at.strftime("%Y-%m-%d %H:%M:%S")}</li>'
        
        if total_matches > 10:
            html += f'<li><em>... and {total_matches - 10} more students</em></li>'
        
        html += '''
            </ul>
        </div>
        '''
        
        return format_html(html)
    match_summary.short_description = '👥 Student Match Details'

    def match_timestamp(self, obj):
        """Show when first match was created"""
        first_match = obj.matched_students.first()
        if first_match:
            return first_match.assigned_at
        return "Not yet matched"
    match_timestamp.short_description = 'First Match Created'

    def force_rematch_students(self, request, queryset):
        """Admin action to manually trigger re-matching"""
        from .utils.scheduler import auto_match_students_to_schedule
        
        total_matched = 0
        schedules_processed = 0
        
        for schedule in queryset:
            try:
                matched = auto_match_students_to_schedule(schedule)
                total_matched += matched
                schedules_processed += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"❌ Error processing schedule #{schedule.id}: {str(e)}",
                    level=messages.ERROR
                )
        
        self.message_user(
            request,
            f"✅ Re-matched {total_matched} students across {schedules_processed} schedules",
            level=messages.SUCCESS
        )
    force_rematch_students.short_description = "🔄 Force re-match students for selected schedules"

    def show_matching_details(self, request, queryset):
        """Show detailed matching information for selected schedules"""
        from io import StringIO
        import csv
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="matching_details.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Schedule ID', 'Subject', 'Class Level', 'Teacher', 'Date', 'Start Time',
            'Total Matched Students', 'Student Names', 'Student Emails', 'Match Timestamps'
        ])
        
        for schedule in queryset:
            matches = schedule.matched_students.select_related('student').all()
            
            if matches:
                student_names = '; '.join([match.student.full_name for match in matches])
                student_emails = '; '.join([match.student.email for match in matches])
                match_times = '; '.join([match.assigned_at.strftime("%Y-%m-%d %H:%M") for match in matches])
                
                writer.writerow([
                    schedule.id,
                    schedule.subject.name,
                    schedule.class_level.name,
                    schedule.teacher.full_name,
                    schedule.date,
                    schedule.start_time,
                    matches.count(),
                    student_names,
                    student_emails,
                    match_times
                ])
            else:
                writer.writerow([
                    schedule.id,
                    schedule.subject.name,
                    schedule.class_level.name,
                    schedule.teacher.full_name,
                    schedule.date,
                    schedule.start_time,
                    0,
                    'No matches',
                    'No matches',
                    'N/A'
                ])
        
        self.message_user(
            request,
            f"📊 Exported matching details for {queryset.count()} schedules",
            level=messages.SUCCESS
        )
        return response
    show_matching_details.short_description = "📊 Export matching details (CSV)"

    def run_auto_scheduler(self, request, queryset):
        """Run auto-scheduler for selected schedules"""
        from .services.scheduler import auto_schedule_classes
    
        try:
            results = auto_schedule_classes(days=1)
            for msg in results:
                self.message_user(request, msg, messages.INFO)
        except Exception as e:
            self.message_user(
                request,
                f"❌ Auto-scheduler error: {str(e)}",
                level=messages.ERROR
            )
    run_auto_scheduler.short_description = "📅 Auto-Schedule Classes (Today)"

    # Add custom buttons to change list
    change_list_template = 'admin/teachers/liveclassschedule/change_list.html'

    def changelist_view(self, request, extra_context=None):
        """Add extra context to changelist view"""
        from django.utils import timezone
        from datetime import timedelta
        
        extra_context = extra_context or {}
        
        # Get statistics for dashboard
        upcoming_schedules = self.model.objects.filter(date__gte=timezone.localdate())
        total_upcoming = upcoming_schedules.count()
        total_matches = sum(sched.matched_students.count() for sched in upcoming_schedules)
        schedules_without_matches = upcoming_schedules.filter(matched_students__isnull=True).count()
        
        extra_context.update({
            'total_upcoming': total_upcoming,
            'total_matches': total_matches,
            'schedules_without_matches': schedules_without_matches,
            'match_percentage': (total_matches / (total_upcoming or 1)) * 100,
        })
        
        return super().changelist_view(request, extra_context=extra_context)



@admin.register(TeacherInterview)
class TeacherInterviewAdmin(admin.ModelAdmin):
    list_display = ['application', 'scheduled_date', 'outcome', 'recorded_at']
    list_filter = ['outcome']
    search_fields = ['application__full_name', 'application__email']
    autocomplete_fields = ['application']


@admin.register(TeacherPayroll)
class TeacherPayrollAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'month', 'total_lessons', 'amount_paid', 'paid_on']
    list_filter = ['month']
    search_fields = ['teacher__full_name']
    actions = ['export_as_csv', 'export_as_pdf']

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=teacher_payroll.csv'
        writer = csv.writer(response)
        writer.writerow(['Teacher', 'Month', 'Total Lessons', 'Amount Paid', 'Paid On'])

        for payroll in queryset:
            writer.writerow([
                payroll.teacher.full_name,
                payroll.month.strftime('%B %Y'),
                payroll.total_lessons,
                payroll.amount_paid,
                payroll.paid_on.strftime('%Y-%m-%d %H:%M')
            ])
        return response

    export_as_csv.short_description = "Export Selected Payroll as CSV"

    def export_as_pdf(self, request, queryset):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Teacher Payroll Report")
        y -= 30

        p.setFont("Helvetica", 12)
        for payroll in queryset:
            if y < 80:
                p.showPage()
                y = height - 50

            p.drawString(50, y, f"Teacher: {payroll.teacher.full_name}")
            p.drawString(50, y - 15, f"Month: {payroll.month.strftime('%B %Y')}")
            p.drawString(50, y - 30, f"Lessons Taken: {payroll.total_lessons}")
            p.drawString(50, y - 45, f"Amount Paid: ₦{payroll.amount_paid}")
            p.drawString(50, y - 60, f"Paid On: {payroll.paid_on.strftime('%Y-%m-%d %H:%M')}")
            y -= 90

        p.showPage()
        p.save()

        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

    export_as_pdf.short_description = "Export Selected Payroll as PDF"


@admin.register(OleLessonPlan)
class OleLessonPlanAdmin(admin.ModelAdmin):
    list_display = ('topic', 'get_subject', 'get_class_level')

    def get_subject(self, obj):
        return obj.topic.subject.name
    get_subject.short_description = 'Subject'

    def get_class_level(self, obj):
        return obj.topic.class_level.name
    get_class_level.short_description = 'Class Level'


class TeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherAssignment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = CustomUser.objects.filter(role='teacher')

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    form = TeacherAssignmentForm
    list_display = ('teacher', 'subject', 'class_level')
    list_filter = ('subject', 'class_level')
    search_fields = ('teacher__email', 'teacher__full_name')
    actions = ['auto_match_students']
    
    def auto_match_students(self, request, queryset):
        """Manually trigger student matching for selected assignments"""
        matched_total = 0
        
        for assignment in queryset:
            students = CustomUser.objects.filter(
                role='ole_student',
                ole_class_level=assignment.class_level,
                ole_subjects=assignment.subject
            )
            
            # Find or create a schedule
            tomorrow = timezone.localdate() + timedelta(days=1)
            schedule, created = LiveClassSchedule.objects.get_or_create(
                teacher=assignment.teacher,
                subject=assignment.subject,
                class_level=assignment.class_level,
                date=tomorrow,
                defaults={
                    'start_time': timezone.datetime.strptime('10:00', '%H:%M').time(),
                    'end_time': timezone.datetime.strptime('11:00', '%H:%M').time(),
                }
            )
            
            for student in students:
                match, created = OleStudentMatch.objects.get_or_create(
                    student=student,
                    schedule=schedule
                )
                if created:
                    matched_total += 1
        
        self.message_user(
            request, 
            f"✅ Matched {matched_total} students to their teachers!",
            level=messages.SUCCESS
        )
    
    auto_match_students.short_description = "Auto-match students to these teacher assignments"


# Register remaining models with default admin behavior
admin.site.register(OleSubject)
admin.site.register(OleClassLevel)
admin.site.register(OleTopic)
admin.site.register(LiveClassSession)


