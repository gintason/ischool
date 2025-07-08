from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from django.db.models import Count

from teachers.models import AttendanceLog, LiveClassSession, StudentAttendanceSummary, TeacherLessonSummary
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Generate weekly attendance and lesson summaries'

    def handle(self, *args, **kwargs):
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Student attendance summary
        student_logs = AttendanceLog.objects.filter(
            joined_at__date__range=(start_of_week, end_of_week)
        ).values('student').annotate(
            total=Count('id')
        )

        for record in student_logs:
            StudentAttendanceSummary.objects.update_or_create(
                student_id=record['student'],
                week_start=start_of_week,
                defaults={
                    'week_end': end_of_week,
                    'total_classes_attended': record['total'],
                }
            )

        # Teacher lesson summary
        teacher_logs = LiveClassSession.objects.filter(
            started_at__date__range=(start_of_week, end_of_week)
        ).values('schedule__teacher').annotate(
            total=Count('id')
        )

        for record in teacher_logs:
            TeacherLessonSummary.objects.update_or_create(
                teacher_id=record['schedule__teacher'],
                week_start=start_of_week,
                defaults={
                    'week_end': end_of_week,
                    'total_lessons_taken': record['total'],
                }
            )

        self.stdout.write(self.style.SUCCESS("Weekly summaries generated."))
