"""Ola CBT flow as the mobile app calls it (including its //api/ URLs)."""
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from test_app.models import Question, Test

LEVELS = ['JSS1', 'JSS2', 'JSS3', 'SSS1', 'SSS2', 'SSS3']


class _SyncThread:
    def __init__(self, target, daemon=None):
        self.target = target

    def start(self):
        self.target()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class OlaTestFlow(TestCase):
    def setUp(self):
        cache.clear()
        User = get_user_model()
        User.objects.create_superuser(email='admin@ischool.ng', password='x', role='admin',
                                      full_name='Admin', username='admin')
        call_command('seed_ola_questions', stdout=StringIO())
        self.student = User.objects.create_user(email='kid@example.com', password='pw12345!',
                                                role='student', full_name='Kid', username='kid1')
        self.client = APIClient()
        res = self.client.post('/api/users/auth/login/', {'username': 'kid1', 'password': 'pw12345!'},
                               format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + res.data['access'])

    def app_get(self, path, params):
        # The app requests https://www.ischool.ng//api/... ; send that raw path.
        return self.client.get('/', params, PATH_INFO=path)

    def app_post(self, path, data):
        return self.client.post('/', data, format='json', PATH_INFO=path)

    def test_all_class_levels_offered(self):
        res = self.client.get('/api/class-levels/')
        self.assertEqual(res.json()['class_levels'], LEVELS)

    def test_every_level_has_subjects_and_topics(self):
        for level in LEVELS:
            subjects = self.app_get('//api/subjects/', {'class_level': level}).json()['subjects']
            self.assertEqual(subjects, ['English Language', 'Mathematics'], level)
            topics = self.app_get('//api/topics/', {'class_level': level, 'subject': 'Mathematics'}).json()['topics']
            self.assertEqual(len(topics), 1, level)

    def test_take_test_and_result_is_emailed(self):
        topic = self.app_get('//api/topics/', {'class_level': 'JSS2', 'subject': 'Mathematics'}).json()['topics'][0]
        res = self.app_post('//api/start/', {'class_level': 'JSS2', 'subject': 'Mathematics', 'topic': topic})
        self.assertEqual(res.status_code, 200, res.content[:300])
        questions = res.json()['questions']
        self.assertEqual(len(questions), 10)
        self.assertTrue(all('correct_answer' not in q for q in questions))

        answers = [{'question_id': q['id'], 'answer': Question.objects.get(id=q['id']).correct_answer}
                   for q in questions]
        with mock.patch('test_app.views.threading.Thread', _SyncThread):
            res = self.app_post('//api/submit/', {'session_id': res.json()['session_id'], 'answers': answers})
        self.assertEqual(res.status_code, 200, res.content[:300])
        self.assertEqual(res.json()['score'], 100.0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['kid@example.com'])
        self.assertEqual(mail.outbox[0].attachments[0][0], 'Test_Result.pdf')

    def test_older_text_only_tests_are_found(self):
        test = Test.objects.create(class_level='JSS1', subject='Basic Science', topic='Living Things',
                                   created_by=self.student)
        Question.objects.create(test=test, question_type='mcq', text='Q?', option_a='a', option_b='b',
                                option_c='c', option_d='d', correct_answer='A')
        self.assertIn('Basic Science',
                      self.client.get('/api/subjects/', {'class_level': 'JSS1'}).json()['subjects'])
        res = self.client.post('/api/start/', {'class_level': 'JSS1', 'subject': 'Basic Science',
                                               'topic': 'Living Things'}, format='json')
        self.assertEqual(len(res.json()['questions']), 1)

    def test_topic_without_questions_gives_clear_error(self):
        res = self.client.post('/api/start/', {'class_level': 'JSS1', 'subject': 'Physics', 'topic': 'Motion'},
                               format='json')
        self.assertEqual(res.status_code, 404)

    def test_seed_is_idempotent(self):
        out = StringIO()
        call_command('seed_ola_questions', stdout=out)
        self.assertIn('0 new questions', out.getvalue())
        self.assertEqual(Question.objects.count(), 120)
