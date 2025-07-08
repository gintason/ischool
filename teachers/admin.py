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
    list_display = ['teacher_email', 'subject_name', 'class_level_name', 'start_time', 'end_time', 'total_matched_students']
    list_filter = ['class_level', 'subject', 'teacher']  # Will render as dropdowns
    search_fields = ['teacher__email', 'subject__name']
    actions = ['run_auto_scheduler']
    inlines = [OleStudentMatchInline]  # ✅ Add this line


    def subject_name(self, obj):
        return obj.subject.name
    subject_name.short_description = 'Subject'

    def class_level_name(self, obj):
        return obj.class_level.name
    class_level_name.short_description = 'Class Level'

    def teacher_email(self, obj):
        return obj.teacher.email
    teacher_email.short_description = 'Teacher Email'

    def total_matched_students(self, obj):
        return obj.matched_students.count()
    total_matched_students.short_description = 'Matched Students'

    def run_auto_scheduler(self, request, queryset):
        results = auto_schedule_classes(days=1)  # Adjust to your needs
        for msg in results:
            self.message_user(request, msg, messages.INFO)

    run_auto_scheduler.short_description = "📅 Auto-Schedule Classes (Today)"




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


# Register remaining models with default admin behavior
admin.site.register(OleSubject)
admin.site.register(OleClassLevel)
admin.site.register(OleTopic)
admin.site.register(LiveClassSession)


