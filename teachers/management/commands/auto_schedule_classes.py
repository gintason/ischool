from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time, datetime
from teachers.models import OleSubject, OleClassLevel, LiveClassSchedule, OleStudentMatch, TeacherAssignment
from users.models import CustomUser
from django.db import transaction, IntegrityError

# ✅ New: Weekly limit enforcement function
def weekly_schedule_limit_reached(teacher, subject, class_level, date, limit=3):
    week_start = date - timedelta(days=date.weekday())
    week_end = week_start + timedelta(days=6)
    return LiveClassSchedule.objects.filter(
        teacher=teacher,
        subject=subject,
        class_level=class_level,
        date__range=(week_start, week_end)
    ).count() >= limit

class Command(BaseCommand):
    help = 'Auto-schedules live classes for teachers and students (8am–6pm, max 10 per day).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--week',
            action='store_true',
            help='Schedule classes for 7 days starting from today.'
        )

    def handle(self, *args, **options):
        start_day = timezone.localdate()
        num_days = 7 if options['week'] else 1

        start_hour = 8
        end_hour = 18
        max_classes_per_day = 10
        total_scheduled = 0

        for day_offset in range(num_days):
            date = start_day + timedelta(days=day_offset)
            scheduled_count = 0

            self.stdout.write(self.style.SUCCESS(f"\n📅 Scheduling for: {date}"))

            class_levels = OleClassLevel.objects.all()
            subjects = OleSubject.objects.all()

            for class_level in class_levels:
                for subject in subjects:
                    assignment = TeacherAssignment.objects.filter(
                        subject=subject,
                        class_level=class_level
                    ).select_related('teacher').first()

                    if not assignment or not assignment.teacher:
                        self.stdout.write(self.style.WARNING(
                            f"⛔ No teacher assigned for {subject.name} - {class_level.name}"
                        ))
                        continue

                    teacher = assignment.teacher

                    if not teacher.ole_subjects.filter(id=subject.id).exists():
                        teacher.ole_subjects.add(subject)
                        self.stdout.write(self.style.WARNING(
                            f"🔄 Fixed teacher's ole_subjects M2M: {teacher.full_name} now linked to {subject.name}"
                        ))

                    if teacher.ole_class_level != class_level:
                        teacher.ole_class_level = class_level
                        teacher.save()
                        self.stdout.write(self.style.WARNING(
                            f"🔄 Fixed teacher's class level: {teacher.full_name} now linked to {class_level.name}"
                        ))

                    students = CustomUser.objects.filter(
                        role='ole_student',
                        ole_class_level=class_level,
                        ole_subjects=subject
                    )

                    if not students.exists():
                        self.stdout.write(self.style.WARNING(
                            f"⚠️ No students for {subject.name} - {class_level.name}"
                        ))
                        continue

                    # ✅ Enforce weekly max (3 per subject/class/teacher)
                    if weekly_schedule_limit_reached(teacher, subject, class_level, date):
                        self.stdout.write(self.style.WARNING(
                            f"📆 Weekly limit reached for {teacher.full_name} - {subject.name} ({class_level.name})"
                        ))
                        continue

                    existing_schedule_qs = LiveClassSchedule.objects.filter(
                        teacher=teacher,
                        subject=subject,
                        class_level=class_level,
                        date=date
                    )

                    if existing_schedule_qs.exists():
                        self.stdout.write(f"⏭️ Already scheduled: {subject.name} - {class_level.name}")
                        schedule = existing_schedule_qs.first()

                        matched_count = 0
                        for student in students:
                            _, created = OleStudentMatch.objects.get_or_create(student=student, schedule=schedule)
                            if created:
                                matched_count += 1

                        self.stdout.write(self.style.SUCCESS(
                            f"🔁 Matched {matched_count} new student(s) to existing schedule."
                        ))
                        continue

                    existing_slots = LiveClassSchedule.objects.filter(
                        teacher=teacher,
                        date=date
                    ).order_by('start_time').values_list('start_time', flat=True)

                    scheduled_times = set(existing_slots)
                    time_slot = None

                    for hour in range(start_hour, end_hour):
                        start = time(hour, 0)
                        if start not in scheduled_times:
                            time_slot = start
                            break

                    if not time_slot:
                        self.stdout.write(self.style.WARNING(
                            f"⏰ No free slots left for {teacher.full_name}"
                        ))
                        continue

                    start_time = datetime.combine(date, time_slot)
                    end_time = start_time + timedelta(hours=1)

                    with transaction.atomic():
                        schedule = LiveClassSchedule.objects.create(
                            teacher=teacher,
                            subject=subject,
                            class_level=class_level,
                            date=date,
                            start_time=start_time.time(),
                            end_time=end_time.time()
                        )

                        for student in students:
                            try:
                                OleStudentMatch.objects.get_or_create(student=student, schedule=schedule)
                            except IntegrityError:
                                continue

                    scheduled_count += 1
                    total_scheduled += 1

                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Scheduled: {subject.name} - {class_level.name} at {start_time.time()}"
                    ))

                    if scheduled_count >= max_classes_per_day:
                        self.stdout.write(self.style.WARNING("📈 Daily limit reached (10 classes)"))
                        break

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Done. {total_scheduled} classes scheduled across {num_days} day(s)."
        ))
