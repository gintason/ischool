from django.utils.timezone import now, timedelta
from django.db.models import Sum
from teachers.models import TeacherLessonSummary, TeacherPayroll
from users.models import CustomUser
from celery import shared_task
from datetime import date
from celery import shared_task
from emails.sendgrid_email import send_email
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from teachers.management.commands.generate_weekly_attendance_summary import Command
from django.utils.timezone import now


@shared_task
def generate_weekly_attendance_summary():
    Command().handle()



LESSON_RATE = 500  # Set your fixed rate per lesson here (₦)


@shared_task
def generate_monthly_teacher_payroll():
    today = now().date()
    first_day = date(today.year, today.month, 1)
    last_day = today

    # Get all teachers
    teachers = CustomUser.objects.filter(role='teacher')

    for teacher in teachers:
        # Filter lesson summaries within this month
        total_lessons = TeacherLessonSummary.objects.filter(
            teacher=teacher,
            week_start__gte=first_day,
            week_start__lte=last_day
        ).aggregate(total=Sum('total_lessons_taken'))['total'] or 0

        amount = total_lessons * LESSON_RATE

        if total_lessons > 0:
            TeacherPayroll.objects.update_or_create(
                teacher=teacher,
                month=first_day,
                defaults={
                    'total_lessons': total_lessons,
                    'amount_paid': amount,
                }
            )


@shared_task
def send_teacher_payslips():
    current_month = now().replace(day=1)
    payrolls = TeacherPayroll.objects.filter(month=current_month)

    for payroll in payrolls:
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50

        # Payslip Header
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Payslip - iSchool")
        y -= 30

        # Teacher Info
        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Teacher: {payroll.teacher.full_name}")
        p.drawString(50, y - 20, f"Month: {payroll.month.strftime('%B %Y')}")
        p.drawString(50, y - 40, f"Lessons Taken: {payroll.total_lessons}")
        p.drawString(50, y - 60, f"Amount Paid: ₦{payroll.amount_paid}")
        p.drawString(50, y - 80, f"Paid On: {payroll.paid_on.strftime('%Y-%m-%d')}")

        p.showPage()
        p.save()
        buffer.seek(0)

        email = send_email(
            subject="Your Monthly Payslip",
            body="Attached is your payslip for this month. Thank you for your hard work!",
            from_email="admin@ischool.com",
            to=[payroll.teacher.email],
        )
        email.attach(f"Payslip_{payroll.month.strftime('%b_%Y')}.pdf", buffer.read(), "application/pdf")
        email.send()