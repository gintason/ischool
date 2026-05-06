# teachers/management/commands/auto_match_and_schedule.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time, datetime
from teachers.models import (
    OleSubject, OleClassLevel, LiveClassSchedule, 
    OleStudentMatch, TeacherAssignment, OleTopic
)
from users.models import CustomUser
from django.db import transaction, IntegrityError
from django.db.models import Q

class Command(BaseCommand):
    help = 'Auto-match students with teachers and schedule live classes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to schedule (default: 7)'
        )

    def handle(self, *args, **options):
        days_ahead = options['days']
        start_day = timezone.localdate()
        
        total_matches = 0
        total_scheduled = 0
        
        self.stdout.write(self.style.SUCCESS("🎯 Starting Auto-Match & Scheduling System\n"))
        
        # Step 1: Create student-teacher matches based on subject + class level
        self.stdout.write("📊 STEP 1: Auto-matching students to teachers...")
        
        # Get all active teacher assignments
        assignments = TeacherAssignment.objects.select_related('teacher', 'subject', 'class_level').all()
        
        for assignment in assignments:
            teacher = assignment.teacher
            subject = assignment.subject
            class_level = assignment.class_level
            
            # Find students who need this subject at this class level
            students = CustomUser.objects.filter(
                role='ole_student',
                ole_class_level=class_level,
                ole_subjects=subject
            )
            
            if not students.exists():
                self.stdout.write(self.style.WARNING(
                    f"⚠️ No students found for {subject.name} - {class_level.name}"
                ))
                continue
            
            # Create or get existing schedules for this teacher-subject-class
            self.stdout.write(self.style.SUCCESS(
                f"✅ Found {students.count()} students for {teacher.full_name} - {subject.name} ({class_level.name})"
            ))
            
            # Step 2: Schedule classes automatically
            scheduled_count = self.schedule_classes_for_assignment(
                assignment, students, start_day, days_ahead
            )
            total_scheduled += scheduled_count
            total_matches += students.count()
        
        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 COMPLETE! Matched {total_matches} students | Scheduled {total_scheduled} classes"
        ))
    
    def schedule_classes_for_assignment(self, assignment, students, start_day, days_ahead):
        """Schedule classes for a specific teacher-subject-class combination"""
        teacher = assignment.teacher
        subject = assignment.subject
        class_level = assignment.class_level
        
        scheduled_count = 0
        start_hour = 8
        end_hour = 18
        
        for day_offset in range(days_ahead):
            date = start_day + timedelta(days=day_offset)
            
            # Skip weekends (optional)
            if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                continue
            
            # Check if already scheduled for this date
            existing = LiveClassSchedule.objects.filter(
                teacher=teacher,
                subject=subject,
                class_level=class_level,
                date=date
            ).exists()
            
            if existing:
                continue
            
            # Find available time slot
            existing_slots = LiveClassSchedule.objects.filter(
                teacher=teacher,
                date=date
            ).values_list('start_time', flat=True)
            
            scheduled_times = set(existing_slots)
            time_slot = None
            
            for hour in range(start_hour, end_hour):
                start = time(hour, 0)
                if start not in scheduled_times:
                    time_slot = start
                    break
            
            if not time_slot:
                continue
            
            # Create the class schedule
            start_datetime = datetime.combine(date, time_slot)
            end_datetime = start_datetime + timedelta(hours=1)
            
            with transaction.atomic():
                schedule = LiveClassSchedule.objects.create(
                    teacher=teacher,
                    subject=subject,
                    class_level=class_level,
                    date=date,
                    start_time=start_datetime.time(),
                    end_time=end_datetime.time()
                )
                
                # Auto-match all students to this schedule
                matched_count = 0
                for student in students:
                    _, created = OleStudentMatch.objects.get_or_create(
                        student=student,
                        schedule=schedule
                    )
                    if created:
                        matched_count += 1
                
                scheduled_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  📅 Scheduled: {subject.name} ({class_level.name}) on {date} at {time_slot} → {matched_count} students matched"
                ))
        
        return scheduled_count