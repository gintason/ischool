# teachers/utils/scheduler.py

from users.models import CustomUser
from teachers.models import OleStudentMatch, LiveClassSchedule, TeacherAssignment
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta, time


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


def auto_schedule_for_teacher_assignment(teacher_assignment, days_ahead=7):
    """
    Create schedules for a teacher assignment if there are enough students.
    
    Args:
        teacher_assignment: TeacherAssignment instance
        days_ahead: Number of days to look ahead for scheduling (default: 7)
    
    Returns:
        tuple: (schedule, matched_count) or (None, 0) if no schedule created
    """
    if not isinstance(teacher_assignment, TeacherAssignment):
        raise ValueError("teacher_assignment must be an instance of TeacherAssignment")
    
    # Find students who need this subject at this class level
    students = CustomUser.objects.filter(
        role='ole_student',
        ole_class_level=teacher_assignment.class_level,
        ole_subjects=teacher_assignment.subject
    )
    
    # Minimum 3 students to schedule a class (adjust as needed)
    MIN_STUDENTS_REQUIRED = 3
    
    if students.count() < MIN_STUDENTS_REQUIRED:
        return None, 0
    
    # Find next available weekday with free time slots
    start_date = timezone.localdate()
    days_offset = 0
    
    while days_offset < days_ahead:
        date = start_date + timedelta(days=days_offset)
        
        # Skip weekends (optional - 5=Saturday, 6=Sunday)
        if date.weekday() >= 5:
            days_offset += 1
            continue
        
        # Check teacher's existing classes for that day
        existing_classes = LiveClassSchedule.objects.filter(
            teacher=teacher_assignment.teacher,
            date=date
        ).count()
        
        MAX_CLASSES_PER_DAY = 5
        if existing_classes >= MAX_CLASSES_PER_DAY:
            days_offset += 1
            continue
        
        # Find an available time slot
        existing_slots = LiveClassSchedule.objects.filter(
            teacher=teacher_assignment.teacher,
            date=date
        ).values_list('start_time', flat=True)
        
        scheduled_times = set(existing_slots)
        time_slot = None
        
        # Try to find a free hour between 8 AM and 6 PM
        for hour in range(8, 18):  # 8 AM to 6 PM
            start = time(hour, 0)
            if start not in scheduled_times:
                time_slot = start
                break
        
        if not time_slot:
            days_offset += 1
            continue
        
        # Create the schedule
        schedule = LiveClassSchedule.objects.create(
            teacher=teacher_assignment.teacher,
            subject=teacher_assignment.subject,
            class_level=teacher_assignment.class_level,
            date=date,
            start_time=time_slot,
            end_time=time(hour + 1, 0) if time_slot.hour + 1 <= 18 else time(18, 0)
        )
        
        # Auto-match students to this schedule
        matched_count = auto_match_students_to_schedule(schedule)
        
        return schedule, matched_count
    
    return None, 0


def auto_match_student_to_teachers(student):
    """
    When a new student enrolls or updates subjects, match them to existing teacher schedules.
    
    Args:
        student: CustomUser instance with role='ole_student'
    
    Returns:
        int: Number of matches created
    """
    if student.role != 'ole_student':
        raise ValueError("User must be an OLE student")
    
    class_level = student.ole_class_level
    subjects = student.ole_subjects.all()
    
    if not subjects.exists():
        return 0
    
    total_matches = 0
    
    for subject in subjects:
        # Find teacher assignments for this subject and class level
        teacher_assignments = TeacherAssignment.objects.filter(
            subject=subject,
            class_level=class_level
        ).select_related('teacher')
        
        if not teacher_assignments.exists():
            continue
        
        # Find existing future schedules for these teachers
        for assignment in teacher_assignments:
            schedules = LiveClassSchedule.objects.filter(
                teacher=assignment.teacher,
                subject=subject,
                class_level=class_level,
                date__gte=timezone.localdate()
            )
            
            for schedule in schedules:
                try:
                    with transaction.atomic():
                        _, created = OleStudentMatch.objects.get_or_create(
                            student=student,
                            schedule=schedule
                        )
                        if created:
                            total_matches += 1
                except IntegrityError:
                    continue
    
    return total_matches


def bulk_auto_schedule_for_all_assignments(days_ahead=7):
    """
    Run auto-scheduling for all teacher assignments.
    Useful for cron jobs or manual triggering.
    
    Args:
        days_ahead: Number of days to look ahead for scheduling
    
    Returns:
        dict: Summary of scheduling results
    """
    assignments = TeacherAssignment.objects.select_related('teacher', 'subject', 'class_level').all()
    
    results = {
        'total_assignments': assignments.count(),
        'schedules_created': 0,
        'total_students_matched': 0,
        'errors': []
    }
    
    for assignment in assignments:
        try:
            schedule, matched_count = auto_schedule_for_teacher_assignment(assignment, days_ahead)
            if schedule:
                results['schedules_created'] += 1
                results['total_students_matched'] += matched_count
        except Exception as e:
            results['errors'].append(f"Error for {assignment}: {str(e)}")
    
    return results


def get_student_upcoming_classes(student, days=7):
    """
    Get all upcoming scheduled classes for a student.
    
    Args:
        student: CustomUser instance with role='ole_student'
        days: Number of days to look ahead
    
    Returns:
        QuerySet of LiveClassSchedule objects
    """
    if student.role != 'ole_student':
        raise ValueError("User must be an OLE student")
    
    today = timezone.localdate()
    end_date = today + timedelta(days=days)
    
    matches = OleStudentMatch.objects.filter(
        student=student,
        schedule__date__range=[today, end_date]
    ).select_related('schedule__subject', 'schedule__class_level', 'schedule__teacher')
    
    schedules = [match.schedule for match in matches]
    return sorted(schedules, key=lambda x: x.date)