"""create_review_accounts: each role's review account can log in from the app."""
from io import StringIO

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from teachers.models import OleClassLevel, OleSubject, TeacherApplication
from users.models import CustomUser

PASSWORD = 'Review@2026'


class ReviewAccountsTests(TestCase):
    def setUp(self):
        cache.clear()
        OleClassLevel.objects.create(name='JSS1')
        OleSubject.objects.create(name='Mathematics')
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
