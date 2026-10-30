"""
Load the starter Ola question bank (test_app/question_bank.py): Mathematics
and English Language for JSS1-SSS3, ten multiple-choice questions each.

    python manage.py seed_ola_questions

Safe to run again: existing subjects, topics, tests and questions are reused,
never duplicated, and questions you uploaded yourself are left alone.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from test_app.models import Question, Subject, Test, Topic
from test_app.question_bank import STARTER_QUESTIONS


class Command(BaseCommand):
    help = 'Add the starter Ola questions for every class level.'

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        author = (User.objects.filter(is_superuser=True).order_by('id').first()
                  or User.objects.filter(is_staff=True).order_by('id').first())
        if author is None:
            raise CommandError('Create a superuser first; tests need an author.')

        added = 0
        for class_level, subject_name, topic_name, questions in STARTER_QUESTIONS:
            subject, _ = Subject.objects.get_or_create(name=subject_name, class_level=class_level)
            topic, _ = Topic.objects.get_or_create(name=topic_name, subject=subject)
            test, _ = Test.objects.get_or_create(
                class_level=class_level, subject_fk=subject, topic_fk=topic,
                defaults={'subject': subject_name, 'topic': topic_name, 'created_by': author},
            )
            for text, a, b, c, d, answer in questions:
                _, created = Question.objects.get_or_create(
                    test=test, text=text,
                    defaults={'question_type': 'mcq', 'option_a': a, 'option_b': b,
                              'option_c': c, 'option_d': d, 'correct_answer': answer},
                )
                added += created
            self.stdout.write('  %s  %-17s %-42s %d questions' % (
                class_level, subject_name, topic_name, test.questions.count()))

        self.stdout.write(self.style.SUCCESS('Done: %d new questions added.' % added))
