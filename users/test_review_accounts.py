"""create_review_accounts: each role's review account can log in from the app."""
from io import StringIO

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from teachers.models import (
    LiveClassSchedule, OleClassLevel, OleStudentMatch, OleSubject, TeacherApplication,
    TeacherAssignment,
)
from users.models import CustomUser

PASSWORD = 'Review@2026'


class ReviewAccountsTests(TestCase):
    def setUp(self):
        cache.clear()
        self.level = OleClassLevel.objects.create(name='JSS1')
        self.maths = OleSubject.objects.create(name='Mathematics')
        # A real paying student in the same class and subject.
        self.real = CustomUser.objects.create(
            email='real@student.ng', username='real1', full_name='Real Student',
            role='ole_student', ole_class_level=self.level)
        self.real.ole_subjects.set([self.maths])
        self.real_teacher = CustomUser.objects.create(
            email='real@teacher.ng', username='realt', full_name='Real Teacher', role='teacher')
        TeacherAssignment.objects.create(
            teacher=self.real_teacher, subject=self.maths, class_level=self.level)
        call_command('create_review_accounts', password=PASSWORD, stdout=StringIO())
        self.client = APIClient()

    def test_ola_student_login(self):
        res = self.client.post('/api/users/auth/login/',
                               {'username': 'ola_review', 'password': PASSWORD}, format='json')
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data['role'], 'student')

    def test_ole_student_login_and_active_subscription(self):
        res = self.client.post('/api/users/ole-student/login/',
                               {'email': 'ole.review@ischool.ng', 'password': PASSWORD}, format='json')
        self.assertEqual(res.status_code, 200, res.data)
        self.assertIn('key', res.data)
        self.assertTrue(CustomUser.objects.get(email='ole.review@ischool.ng').is_subscription_active())

    def test_teacher_login_on_mobile_url(self):
        res = self.client.post('/api/login/',
                               {'email': 'teacher.review@ischool.ng', 'password': PASSWORD}, format='json')
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data['user']['role'], 'teacher')
        self.assertEqual(TeacherApplication.objects.get(email='teacher.review@ischool.ng').status, 'hired')

    def test_rerun_keeps_same_accounts(self):
        call_command('create_review_accounts', password=PASSWORD, stdout=StringIO())
        self.assertEqual(CustomUser.objects.filter(email__endswith='review@ischool.ng').count(), 3)

    def test_real_students_are_never_matched_to_review_classes(self):
        teacher = CustomUser.objects.get(email='teacher.review@ischool.ng')
        ole = CustomUser.objects.get(email='ole.review@ischool.ng')
        self.assertFalse(TeacherAssignment.objects.filter(teacher=teacher).exists())
        self.assertEqual(LiveClassSchedule.objects.filter(teacher=teacher).count(), 14)
        self.assertFalse(OleStudentMatch.objects.filter(
            schedule__teacher=teacher).exclude(student=ole).exists())
        # ...and the review student is not placed in real teachers' classes.
        self.assertFalse(OleStudentMatch.objects.filter(student=ole).exclude(
            schedule__teacher=teacher).exists())

    def test_rerun_removes_earlier_leak(self):
        teacher = CustomUser.objects.get(email='teacher.review@ischool.ng')
        leaked = LiveClassSchedule.objects.filter(teacher=teacher).first()
        OleStudentMatch.objects.create(student=self.real, schedule=leaked)
        TeacherAssignment.objects.bulk_create([TeacherAssignment(
            teacher=teacher, subject=self.maths, class_level=self.level)])
        call_command('create_review_accounts', password=PASSWORD, stdout=StringIO())
        self.assertFalse(OleStudentMatch.objects.filter(
            student=self.real, schedule__teacher=teacher).exists())
        self.assertFalse(TeacherAssignment.objects.filter(teacher=teacher).exists())

    def test_matching_signals_still_work_afterwards(self):
        schedule = LiveClassSchedule.objects.create(
            teacher=self.real_teacher, subject=self.maths, class_level=self.level,
            date=LiveClassSchedule.objects.first().date, start_time='09:00', end_time='10:00')
        self.assertTrue(OleStudentMatch.objects.filter(student=self.real, schedule=schedule).exists())

    def test_upcoming_lessons_send_text_the_app_can_show(self):
        res = self.client.post('/api/users/ole-student/login/',
                               {'email': 'ole.review@ischool.ng', 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + res.data['key'])
        res = self.client.get('/api/teachers/ole-student/upcoming-lessons/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 14)
        lesson = res.data[0]
        self.assertEqual(lesson['subject'], 'Mathematics')
        self.assertEqual(lesson['teacher'], 'Play Review (Ole Teacher)')
        # Lesson detail keeps the nested shape its screens read (subject.name).
        detail = self.client.get('/api/users/ole-student/lesson/%d/' % lesson['id'])
        self.assertEqual(detail.status_code, 200, detail.data)
        self.assertEqual(detail.data['subject'], {'name': 'Mathematics'})
