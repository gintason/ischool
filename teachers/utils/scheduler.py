from users.models import CustomUser
from teachers.models import OleStudentMatch, LiveClassSchedule
from django.db import IntegrityError, transaction

def auto_match_students_to_schedule(schedule):
    """
    Match students to a schedule based on class level and subject.
    Prevents duplicates and handles race conditions gracefully.
    """
    if not isinstance(schedule, LiveClassSchedule):
        raise ValueError("schedule must be an instance of LiveClassSchedule")

    students = CustomUser.objects.filter(
        role='ole_student',
        ole_class_level=schedule.class_level,
        ole_subjects=schedule.subject
    ).distinct()

    matched_count = 0
    for ole_student in students:
        try:
            with transaction.atomic():
                _, created = OleStudentMatch.objects.get_or_create(
                    student=ole_student,
                    schedule=schedule
                )
                if created:
                    matched_count += 1
        except IntegrityError:
            # Handle rare race condition: skip if already matched
            continue

    return matched_count
