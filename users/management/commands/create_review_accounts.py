"""
Create (or refresh) the demo accounts app-store reviewers use.

Google Play and Apple reviewers cannot fill in sign-up forms, pay, receive
emails or be "hired", so each role gets a ready-made, paid-up account with a
fixed password:

    python manage.py create_review_accounts --password 'Review@2026'

Safe to run again: it updates the same three accounts and pushes their
subscriptions forward.

The review teacher and review student only ever see each other: the live-class
auto-matching signals are switched off while this runs, and the teacher is
never given a TeacherAssignment (which would pull real students into its
classes). Real students and teachers are never matched to review accounts.
"""
from contextlib import contextmanager
from datetime import time, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models.signals import post_save
from django.utils import timezone

from teachers import signals as match_signals
from teachers.models import (
    ApplicationStatus, LiveClassSchedule, OleClassLevel, OleStudentMatch, OleSubject,
    TeacherApplication, TeacherAssignment,
)
from users.models import (
    CustomUser, OleStudentProfile, OleStudentSubjectAccess, OleStudentSubscription,
    RegistrationGroup,
)

VALID_YEARS = 3
REVIEW_CLASS_DAYS = 14  # one demo class a day, so reviewers always see an upcoming lesson

_MATCH_RECEIVERS = [
    (match_signals.match_students_on_schedule_create, LiveClassSchedule),
    (match_signals.auto_match_students_on_teacher_assignment, TeacherAssignment),
    (match_signals.auto_match_teacher_on_student_enrollment, CustomUser),
    (match_signals.auto_create_matches_for_existing_student_update, CustomUser),
]


@contextmanager
def auto_matching_disabled():
    for receiver, sender in _MATCH_RECEIVERS:
        post_save.disconnect(receiver, sender=sender)
    try:
        yield
    finally:
        for receiver, sender in _MATCH_RECEIVERS:
            post_save.connect(receiver, sender=sender)

ACCOUNTS = {
    'ola': {
        'email': 'ola.review@ischool.ng', 'username': 'ola_review',
        'full_name': 'Play Review (Ola Student)', 'role': 'student',
    },
    'ole': {
        'email': 'ole.review@ischool.ng', 'username': 'ole_review',
        'full_name': 'Play Review (Ole Student)', 'role': 'ole_student',
    },
    'teacher': {
        'email': 'teacher.review@ischool.ng', 'username': 'teacher_review',
        'full_name': 'Play Review (Ole Teacher)', 'role': 'teacher',
    },
}


class Command(BaseCommand):
    help = 'Create or refresh the Ola student, Ole student and Ole teacher review accounts.'

    def add_arguments(self, parser):
        parser.add_argument('--password', required=True,
                            help='Password for all three review accounts (8+ characters).')

    def _user(self, spec, password):
        user = (CustomUser.objects.filter(email=spec['email']).first()
                or CustomUser.objects.filter(username=spec['username']).first()
                or CustomUser(email=spec['email']))
        user.email = spec['email']
        user.username = spec['username']
        user.full_name = spec['full_name']
        user.role = spec['role']
        user.is_active = True
        user.set_password(password)
        user.save()
        return user

    def handle(self, *args, **options):
        password = options['password']
        if len(password) < 8:
            raise CommandError('Use a password of at least 8 characters.')
        with auto_matching_disabled(), transaction.atomic():
            self._create(password)

    def _create(self, password):

        expires = timezone.now() + timedelta(days=365 * VALID_YEARS)
        class_level = OleClassLevel.objects.order_by('id').first()
        subjects = list(OleSubject.objects.order_by('id'))

        # Ola student: logs in with username + password, needs a paid group.
        ola = self._user(ACCOUNTS['ola'], password)
        group = ola.registration_group or RegistrationGroup()
        group.account_type = 'home'
        group.name = 'Google Play Review'
        group.email = ola.email
        group.slots_applied = max(group.slots_applied or 0, 1)
        group.slots_remaining = max(group.slots_remaining or 0, 0)
        group.subscription_expires = expires.date()
        group.save()
        ola.registration_group = group
        ola.subscription_expires_on = expires.date()
        ola.save()

        # Ole student: logs in with email + password, needs an active subscription.
        ole = self._user(ACCOUNTS['ole'], password)
        if class_level:
            ole.ole_class_level = class_level
            ole.save()
        if subjects:
            ole.ole_subjects.set(subjects)
        profile, _ = OleStudentProfile.objects.get_or_create(user=ole)
        if class_level:
            profile.class_level = class_level
            profile.save()
            if subjects:
                profile.subjects.set(subjects)
                access, _ = OleStudentSubjectAccess.objects.get_or_create(
                    ole_student=ole, ole_class_level=class_level)
                access.ole_subjects.set(subjects)
        OleStudentSubscription.objects.update_or_create(
            user=ole, defaults={'plan_type': 'yearly', 'end_date': expires})

        # Ole teacher: logs in with email + password once hired.
        teacher = self._user(ACCOUNTS['teacher'], password)
        TeacherApplication.objects.update_or_create(
            email=teacher.email,
            defaults={
                'full_name': teacher.full_name, 'phone': '08000000000',
                'subjects': ', '.join(s.name for s in subjects[:3]) or 'Mathematics',
                'availability': 'Weekdays', 'status': ApplicationStatus.HIRED,
            },
        )

        # Undo anything an earlier version of this command (or the matching
        # signals) linked to the review accounts, including real students
        # matched into the review teacher's classes.
        TeacherAssignment.objects.filter(teacher=teacher).delete()
        LiveClassSchedule.objects.filter(teacher=teacher).delete()
        OleStudentMatch.objects.filter(student=ole).delete()

        # Private demo classes: review teacher + review student only.
        if class_level and subjects:
            today = timezone.localdate()
            for offset in range(1, REVIEW_CLASS_DAYS + 1):
                schedule = LiveClassSchedule.objects.create(
                    teacher=teacher, subject=subjects[0], class_level=class_level,
                    date=today + timedelta(days=offset),
                    start_time=time(10, 0), end_time=time(11, 0),
                )
                OleStudentMatch.objects.create(student=ole, schedule=schedule)

        self.stdout.write(self.style.SUCCESS('Review accounts ready (valid until %s):' % expires.date()))
        if class_level and subjects:
            self.stdout.write('  Demo classes: %s %s, 10:00 daily for the next %d days '
                              '(review accounts only - re-run to extend)'
                              % (subjects[0].name, class_level.name, REVIEW_CLASS_DAYS))
        self.stdout.write('  Ola student  - username: %s  password: %s' % (ola.username, password))
        self.stdout.write('  Ole student  - email:    %s  password: %s' % (ole.email, password))
        self.stdout.write('  Ole teacher  - email:    %s  password: %s' % (teacher.email, password))
        if not class_level or not subjects:
            self.stdout.write(self.style.WARNING(
                'No Ole class levels/subjects exist yet, so the Ole accounts have none assigned.'))
