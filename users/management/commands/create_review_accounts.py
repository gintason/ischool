"""
Create (or refresh) the demo accounts app-store reviewers use.

Google Play and Apple reviewers cannot fill in sign-up forms, pay, receive
emails or be "hired", so each role gets a ready-made, paid-up account with a
fixed password:

    python manage.py create_review_accounts --password 'Review@2026'

Safe to run again: it updates the same three accounts and pushes their
subscriptions forward.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from teachers.models import (
    ApplicationStatus, OleClassLevel, OleSubject, TeacherApplication, TeacherAssignment,
)
from users.models import (
    CustomUser, OleStudentProfile, OleStudentSubjectAccess, OleStudentSubscription,
    RegistrationGroup,
)

VALID_YEARS = 3

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

    @transaction.atomic
    def handle(self, *args, **options):
        password = options['password']
        if len(password) < 8:
            raise CommandError('Use a password of at least 8 characters.')

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
        if class_level and subjects:
            TeacherAssignment.objects.get_or_create(
                teacher=teacher, subject=subjects[0], class_level=class_level)

        self.stdout.write(self.style.SUCCESS('Review accounts ready (valid until %s):' % expires.date()))
        self.stdout.write('  Ola student  - username: %s  password: %s' % (ola.username, password))
        self.stdout.write('  Ole student  - email:    %s  password: %s' % (ole.email, password))
        self.stdout.write('  Ole teacher  - email:    %s  password: %s' % (teacher.email, password))
        if not class_level or not subjects:
            self.stdout.write(self.style.WARNING(
                'No Ole class levels/subjects exist yet, so the Ole accounts have none assigned.'))
