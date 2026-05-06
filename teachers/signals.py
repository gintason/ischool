# teachers/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from teachers.models import (
    LiveClassSchedule, TeacherAssignment, OleStudentMatch
)
from users.models import CustomUser
from .utils.scheduler import auto_match_students_to_schedule

@receiver(post_save, sender=LiveClassSchedule)
def match_students_on_schedule_create(sender, instance, created, **kwargs):
    """When a schedule is created, automatically match students"""
    if created:
        matched = auto_match_students_to_schedule(instance)
        print(f"[AUTO MATCH] {matched} students matched to schedule #{instance.id}")

@receiver(post_save, sender=TeacherAssignment)
def auto_match_students_on_teacher_assignment(sender, instance, created, **kwargs):
    """
    When a teacher is assigned to a subject/class level,
    automatically find and match students who need that subject
    """
    if created:
        teacher = instance.teacher
        subject = instance.subject
        class_level = instance.class_level
        
        print(f"[AUTO MATCH] New teacher assignment: {teacher.full_name} -> {subject.name} ({class_level.name})")
        
        # Find students who need this subject at this class level
        students = CustomUser.objects.filter(
            role='ole_student',
            ole_class_level=class_level,
            ole_subjects=subject
        )
        
        if not students.exists():
            print(f"[AUTO MATCH] No students found for {subject.name} - {class_level.name}")
            return
        
        print(f"[AUTO MATCH] Found {students.count()} students for {subject.name} ({class_level.name})")
        
        # Find or create upcoming schedule for this teacher-subject-class
        tomorrow = timezone.localdate() + timedelta(days=1)
        
        # Check if there's already a schedule for tomorrow
        schedule, created = LiveClassSchedule.objects.get_or_create(
            teacher=teacher,
            subject=subject,
            class_level=class_level,
            date=tomorrow,
            defaults={
                'start_time': timezone.datetime.strptime('10:00', '%H:%M').time(),
                'end_time': timezone.datetime.strptime('11:00', '%H:%M').time(),
            }
        )
        
        if created:
            print(f"[AUTO MATCH] Created new schedule for tomorrow at 10:00 AM")
        
        # Match all students to this schedule
        matched_count = 0
        for student in students:
            match, match_created = OleStudentMatch.objects.get_or_create(
                student=student,
                schedule=schedule
            )
            if match_created:
                matched_count += 1
        
        print(f"[AUTO MATCH] Matched {matched_count} students to schedule #{schedule.id}")
        
        # If many students were matched, consider creating additional schedules
        if matched_count > 20:  # If more than 20 students, might need multiple classes
            print(f"[AUTO MATCH] Large class detected ({matched_count} students). Consider splitting into multiple sessions.")


@receiver(post_save, sender=CustomUser)
def auto_match_teacher_on_student_enrollment(sender, instance, created, **kwargs):
    """
    When a new student enrolls with subjects and class level,
    automatically match them to existing teacher schedules
    """
    if created and instance.role == 'ole_student':
        class_level = instance.ole_class_level
        subjects = instance.ole_subjects.all()
        
        if not subjects.exists():
            print(f"[AUTO MATCH] New student {instance.full_name} has no subjects assigned yet")
            return
        
        print(f"[AUTO MATCH] New student enrolled: {instance.full_name} - {class_level.name if class_level else 'No class level'}")
        
        total_matches = 0
        
        for subject in subjects:
            # Find teacher assignments for this subject and class level
            teacher_assignments = TeacherAssignment.objects.filter(
                subject=subject,
                class_level=class_level
            ).select_related('teacher')
            
            if not teacher_assignments.exists():
                print(f"[AUTO MATCH] No teacher assigned for {subject.name} ({class_level.name if class_level else 'N/A'})")
                continue
            
            print(f"[AUTO MATCH] Found {teacher_assignments.count()} teacher(s) for {subject.name}")
            
            # Find existing future schedules for these teachers
            for assignment in teacher_assignments:
                schedules = LiveClassSchedule.objects.filter(
                    teacher=assignment.teacher,
                    subject=subject,
                    class_level=class_level,
                    date__gte=timezone.localdate()
                )
                
                for schedule in schedules:
                    match, created = OleStudentMatch.objects.get_or_create(
                        student=instance,
                        schedule=schedule
                    )
                    if created:
                        total_matches += 1
                        print(f"[AUTO MATCH] Matched {instance.full_name} to {subject.name} class on {schedule.date}")
        
        print(f"[AUTO MATCH] Total new matches for {instance.full_name}: {total_matches}")


@receiver(post_save, sender=CustomUser)
def auto_create_matches_for_existing_student_update(sender, instance, **kwargs):
    """
    When an existing student's subjects or class level changes,
    automatically create new matches
    """
    if instance.role == 'ole_student':
        # This is for updates to existing students
        # Track if this is an update (not a new creation)
        if not kwargs.get('created', False):
            class_level = instance.ole_class_level
            subjects = instance.ole_subjects.all()
            
            if not subjects.exists():
                return
            
            new_matches = 0
            
            for subject in subjects:
                teacher_assignments = TeacherAssignment.objects.filter(
                    subject=subject,
                    class_level=class_level
                )
                
                for assignment in teacher_assignments:
                    schedules = LiveClassSchedule.objects.filter(
                        teacher=assignment.teacher,
                        subject=subject,
                        class_level=class_level,
                        date__gte=timezone.localdate()
                    )
                    
                    for schedule in schedules:
                        match, created = OleStudentMatch.objects.get_or_create(
                            student=instance,
                            schedule=schedule
                        )
                        if created:
                            new_matches += 1
            
            if new_matches > 0:
                print(f"[AUTO MATCH] Student {instance.full_name} updated - created {new_matches} new matches")