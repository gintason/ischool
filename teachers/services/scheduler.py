from django.utils import timezone
from datetime import timedelta, time, datetime
from teachers.models import OleSubject, OleClassLevel, LiveClassSchedule, OleStudentMatch
from users.models import CustomUser
from django.db import transaction, IntegrityError

# ✅ Weekly limit checker (newly added)
def weekly_schedule_limit_reached(teacher, subject, class_level, date, limit=3):
    week_start = date - timedelta(days=date.weekday())
    week_end = week_start + timedelta(days=6)
    return LiveClassSchedule.objects.filter(
        teacher=teacher,
        subject=subject,
        class_level=class_level,
        date__range=(week_start, week_end)
    ).count() >= limit

def auto_schedule_classes(days=1, max_classes_per_day=10):
    results = []
    start_day = timezone.localdate()

    for day_offset in range(days):
        date = start_day + timedelta(days=day_offset)
        scheduled_count = 0
        start_hour = 8
        end_hour = 18

        class_levels = OleClassLevel.objects.all()
        subjects = OleSubject.objects.all()

        for class_level in class_levels:
            for subject in subjects:
                teacher = CustomUser.objects.filter(
                    role='teacher',
                    ole_subjects=subject,
                    ole_class_level=class_level
                ).first()

                if not teacher:
                    results.append(f"⛔ No teacher for {subject.name} - {class_level.name} on {date}")
                    continue

                students = CustomUser.objects.filter(
                    role='ole_student',
                    ole_class_level=class_level,
                    ole_subjects=subject
                )

                if not students.exists():
                    results.append(f"⚠️ No students for {subject.name} - {class_level.name} on {date}")
                    continue

                # ✅ Enforce 3-per-week max schedule rule
                if weekly_schedule_limit_reached(teacher, subject, class_level, date):
                    results.append(
                        f"📆 Weekly limit reached for {teacher.full_name} - {subject.name} ({class_level.name}) on {date}"
                    )
                    continue

                if LiveClassSchedule.objects.filter(
                    teacher=teacher,
                    subject=subject,
                    class_level=class_level,
                    date=date
                ).exists():
                    results.append(f"⏭️ Already scheduled: {subject.name} - {class_level.name} on {date}")
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
                    results.append(f"⏰ No free slots left for {teacher.full_name} on {date}")
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
                            with transaction.atomic():
                                OleStudentMatch.objects.get_or_create(student=student, schedule=schedule)
                        except IntegrityError:
                            continue

                results.append(f"✅ Scheduled: {subject.name} - {class_level.name} at {start_time.time()} on {date}")
                scheduled_count += 1

                if scheduled_count >= max_classes_per_day:
                    results.append(f"📈 Limit reached: {teacher.full_name} ({max_classes_per_day}) on {date}")
                    break

    return results
