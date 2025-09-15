from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from difflib import SequenceMatcher
import os
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import TestSerializer
from django.db.models import Q
from rest_framework.permissions import AllowAny
import logging
logger = logging.getLogger(__name__)
from io import BytesIO
from xhtml2pdf import pisa
from datetime import datetime
import random
from emails.sendgrid_email import send_email
from .models import Question, TestSession, TestResult, StudentAnswer, Test
from .serializers import StartTestSerializer, SubmitTestSerializer, QuestionSerializer
from . grading.gpt_grader import grade_theory_answer
import openai
from openai import OpenAI
import json
from django.core.mail import send_mail
from django.contrib import messages
from django.core.mail import EmailMessage
import threading


logo_relative_path = 'img/logo.png'  # Relative to 'static/'
logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png')
logo_path = os.path.join(settings.BASE_DIR, 'static', logo_relative_path)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tests(request):
    tests = Test.objects.all()
    serializer = TestSerializer(tests, many=True)
    return Response(serializer.data)


class StartTestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = StartTestSerializer(data=request.data)
        if serializer.is_valid():
            class_level = serializer.validated_data['class_level']
            subject = serializer.validated_data['subject']
            topic = serializer.validated_data['topic']

            # Fetch questions
            questions = Question.objects.filter(
                test__class_level=class_level,
                test__subject=subject,
                test__topic=topic,
            )

            selected_questions = random.sample(list(questions), min(10, len(questions)))

            # Create test session
            session = TestSession.objects.create(
                student=request.user,
                class_level=class_level,
                subject=subject,
                topic=topic
            )

            # Serialize questions using updated QuestionSerializer
            question_data = QuestionSerializer(selected_questions, many=True).data

            return Response({
                "session_id": str(session.id),
                "questions": question_data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_test_detail(request, id):
    try:
        test = Test.objects.get(id=id)
    except Test.DoesNotExist:
        return Response({'error': 'Test not found'}, status=404)

    questions = Question.objects.filter(

         test__class_level=test.class_level,
        test__subject=test.subject,
        test__topic=test.topic,
        question_type='mcq'
        
    )

    return Response({
        "id": test.id,
        "title": test.topic,
        "duration": 20,  # or test.duration if it's stored
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "options": [
                    {"id": "A", "text": q.option_a},
                    {"id": "B", "text": q.option_b},
                    {"id": "C", "text": q.option_c},
                    {"id": "D", "text": q.option_d},
                ]
            } for q in questions
        ]
    })


class SubmitTestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SubmitTestSerializer(data=request.data)
        if serializer.is_valid():
            session_id = serializer.validated_data["session_id"]
            answers = serializer.validated_data["answers"]

            try:
                session = TestSession.objects.get(id=session_id, student=request.user)
            except TestSession.DoesNotExist:
                return Response({"detail": "Test session not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # ✅ Time check: ensure submission is within 10 minutes
            time_elapsed = timezone.now() - session.started_at
            if time_elapsed > timedelta(minutes=10):
                return Response({"detail": "Test submission time exceeded the 10-minute limit."}, status=status.HTTP_400_BAD_REQUEST)

            # 🚫 Prevent double submission
            if session.completed:
                return Response({"detail": "This test has already been submitted."}, status=status.HTTP_400_BAD_REQUEST)

            correct_mcq = 0
            total_mcq = 0
            theory_scores = []
            detailed_answers = []

            test_result = TestResult.objects.create(student=request.user, subject=session.subject, test_session=session)
            test_result.total_questions = total_mcq + len(theory_scores)
            test_result.save()

            for ans in answers:
                question_id = ans["question_id"]
                student_response = ans["answer"]

                try:
                    question = Question.objects.get(id=question_id)
                except Question.DoesNotExist:
                    continue

                is_correct = None
                theory_score = None

                if question.question_type == "mcq":
                    is_correct = student_response == question.correct_answer
                    if is_correct:
                        correct_mcq += 1
                    total_mcq += 1


                elif question.question_type == "theory":
                    expected = question.correct_answer or "No expected answer provided."
                    grading_result = grade_theory_answer(
                        question_text=question.text,
                        expected_answer=expected,
                        student_answer=student_response
                    )
                    theory_score = grading_result.get("score", 0)
                    if not isinstance(theory_score, (int, float)):
                        theory_score = 0

                    theory_scores.append(theory_score)


                StudentAnswer.objects.create(
                    result=test_result,
                    question=question,
                    selected_option=student_response if question.question_type == "mcq" else None,
                    is_correct=is_correct,
                    theory_answer=student_response if question.question_type == "theory" else None,
                    theory_match_percentage=theory_score
                )

                detailed_answers.append({
                    "question": question.text,
                    "student_answer": student_response,
                    "correct_answer": question.correct_answer if question.question_type == "mcq" else question.correct_answer,
                    "is_mcq": question.question_type == "mcq",
                    "is_correct": is_correct,
                    "theory_score": theory_score
                })

            session.submitted_at = timezone.now()
            session.completed = True

            # ⏱️ Calculate duration of the test
            if session.started_at and session.submitted_at:
                duration = (session.submitted_at - session.started_at).total_seconds()
                session.duration = duration  # Only if `duration` field exists

            session.save()

            # Final scoring
            score_percent = round((correct_mcq / total_mcq) * 100, 2) if total_mcq > 0 else 0
            avg_theory_score = round(sum(theory_scores) / len(theory_scores), 2) if theory_scores else 0
            combined_score = round((score_percent * 0.7 + avg_theory_score * 0.3), 2)

            test_result.score = combined_score
            test_result.save()

            # Generate PDF
            context = {
                "student_name": getattr(request.user, 'full_name', '') or request.user.email,
                "date": datetime.now(),
                "score": combined_score,
                "total_mcq": total_mcq,
                "correct_mcq": correct_mcq,
                "avg_theory_score": avg_theory_score,
                "answers": detailed_answers,
                "logo_path": logo_path,  # pass the full path
            }

            html_content = render_to_string("emails/test_result_report.html", context)
            pdf_file = BytesIO()
            result = pisa.CreatePDF(src=html_content, dest=pdf_file)
            if result.err:
                return Response({"detail": "PDF generation failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            pdf_file.seek(0)
            pdf_content = pdf_file.read()

            # Prepare email content
            email_subject = "iSchool Ola - Test Result"
            email_body = (
                f"Dear {context['student_name']},\n\n"
                "Please find attached your test result summary.\n\n"
                "Best regards,\niSchool Ola Team"
            )

            # Determine recipients
            student_email = request.user.email
            parent_email = getattr(request.user.registration_group, 'email', None)
            recipients = list(filter(None, [student_email, parent_email]))


           # ✅ Async email sending with threading (non-blocking)
            def _send_results():
                for recipient in recipients:
                    try:
                        email = EmailMessage(
                            subject=email_subject,
                            body=email_body,
                            from_email="noreply@ischool.ng",
                            to=[recipient],
                        )
                        email.attach("Test_Result.pdf", pdf_content, "application/pdf")
                        email.send(fail_silently=False)
                        logger.info(f"📨 Result email queued for {recipient}")
                    except Exception as e:
                        logger.error(f"❌ Failed to send result email to {recipient}: {e}")

            threading.Thread(target=_send_results, daemon=True).start()

            return Response({
                "message": "Test submitted. Result emailed.",
                "score": combined_score
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([AllowAny])  # 👈 make it public
def list_class_levels(request):
    class_levels = Test.objects.values_list('class_level', flat=True).distinct()
    return Response({'class_levels': list(class_levels)})


@api_view(['GET'])
@permission_classes([AllowAny])
def list_subjects(request):
    class_level = request.query_params.get('class_level')
    if not class_level:
        return Response({'error': 'class_level parameter is required.'}, status=400)
    subjects = Test.objects.filter(class_level=class_level).values_list('subject', flat=True).distinct()
    return Response({'subjects': list(subjects)})


@api_view(['GET'])
@permission_classes([AllowAny])
def list_topics(request):
    class_level = request.query_params.get('class_level')
    subject = request.query_params.get('subject')
    if not class_level or not subject:
        return Response({'error': 'class_level and subject parameters are required.'}, status=400)
    topics = Test.objects.filter(class_level=class_level, subject=subject).values_list('topic', flat=True).distinct()
    return Response({'topics': list(topics)})


class SubjectListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        class_level = request.query_params.get('class_level')
        if not class_level:
            return Response({"error": "class_level query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        subjects = Question.objects.filter(class_level=class_level).values_list('subject', flat=True).distinct()
        return Response(list(subjects), status=status.HTTP_200_OK)


class TopicListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        class_level = request.query_params.get('class_level')
        subject = request.query_params.get('subject')

        if not class_level or not subject:
            return Response({"error": "class_level and subject query parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

        topics = Question.objects.filter(
            class_level=class_level,
            subject=subject
        ).values_list('topic', flat=True).distinct()
        return Response(list(topics), status=status.HTTP_200_OK)


class TestFilterOptionsAPIView(APIView):
    def get(self, request):
        class_levels = list(dict(Question.CLASS_CHOICES).keys())
        subjects = Question.objects.values_list('subject', flat=True).distinct()
        topics = Question.objects.values_list('topic', flat=True).distinct()
        
        return Response({
            'class_levels': class_levels,
            'subjects': list(subjects),
            'topics': list(topics),
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subjects(request):
    class_level = request.GET.get('class_level')
    subjects = Question.objects.filter(class_level=class_level).values_list('subject', flat=True).distinct()
    return Response(list(subjects))


# URL: /api/topics/?class_level=JSS1&subject=Math
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_topics(request):
    class_level = request.GET.get('class_level')
    subject = request.GET.get('subject')
    topics = Question.objects.filter(class_level=class_level, subject=subject).values_list('topic', flat=True).distinct()
    return Response(list(topics))


@api_view(['GET'])
def list_questions(request):
    topic = request.GET.get('topic')
    if not topic:
        return Response({"error": "Topic parameter is required."}, status=400)
    
    # Find tests with matching topic
    tests = Test.objects.filter(topic=topic)
    
    # Get all questions for these tests
    questions = Question.objects.filter(test__in=tests)
    
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)

