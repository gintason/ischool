from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.utils import timezone
from collections import defaultdict
from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.generics import ListAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from rest_framework.generics import RetrieveAPIView
from .models import TeacherPayroll, LiveClassSession
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (
    OleSubject, OleClassLevel, TeacherApplication, LiveClassSchedule,
    OleStudentMatch, LiveClassSession, AttendanceLog, OleLessonPlan, 
    SessionReference, TeacherInterview,
    OleStudentTopicHistory, OleTopic, LiveClassSession
)
from users.models import CustomUser
from elibrary.models import ELibraryChapter

from .serializers import (
    TeacherApplicationSerializer, DailyTimetableSerializer,
    UpcomingSessionSerializer, GroupedScheduleSerializer, TeacherInterviewSerializer,
    LiveClassScheduleSerializer, UpcomingGroupedClassesSerializer,
    SimpleClassScheduleSerializer, OleLessonPlanSerializer, 
    OleClassLevelSerializer, OleSubjectSerializer, OleStudentTopicHistorySerializer, 
    OleTopicWithPlansSerializer, LiveClassSessionSerializer
)
from elibrary.serializers import ELibraryChapterSerializer
from users.serializers import OleStudentBasicSerializer
from .utils.password_generator import generate_password
from datetime import datetime
from django.utils.timezone import now
from .models import OleLesson
from rest_framework.authentication import TokenAuthentication
from users.serializers import LiveClassScheduleDetailSerializer
from django.core.mail import send_mail
from django.contrib import messages

import uuid
import logging

logger = logging.getLogger(__name__)

# Constants
VISIBLE_STUDENTS_PER_CLASS = 10

# ----------------------
# TEACHER APPLICATION FLOW
# ----------------------


class TeacherApplicationView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        print("🔥 Incoming Data:", request.data)
        serializer = TeacherApplicationSerializer(data=request.data)
        
        if serializer.is_valid():
            teacher_app = serializer.save()

            full_name = teacher_app.full_name
            email = teacher_app.email

            subject = "Application Received – iSchool Ole"
            message = (
                f"Hello {full_name},\n\n"
                f"We’ve received your teaching application.\n"
                f"Our team will review it and get back to you if you are shortlisted.\n\n"
                f"Thank you for your interest!\n\n"
                f"Best regards,\n"
                f"iSchool Ole Team"
            )

            try:
                send_mail(
                    subject,
                    message,
                    "noreply@ischool.ng",
                    [email],
                    fail_silently=False
                )
            except Exception as e:
                logger.error("❌ Email sending failed", exc_info=True)
                return Response(
                    {"error": f"Application saved, but email failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # ✅ Return success response
            return Response(
                {"message": "Application received successfully."},
                status=status.HTTP_201_CREATED
            )

        # ❌ Validation failed
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class HireTeacherView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, application_id):
        try:
            application = TeacherApplication.objects.get(id=application_id)
        except TeacherApplication.DoesNotExist:
            return Response({'error': 'Application not found'}, status=404)

        if application.status == 'hired':
            return Response({'error': 'Teacher already hired.'}, status=400)

        if CustomUser.objects.filter(email=application.email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=400)

        # Create teacher user
        password = generate_password()
        user = CustomUser.objects.create_user(
            email=application.email,
            full_name=application.full_name,
            password=password,
            role='teacher',
        )

        application.status = 'hired'
        application.save()

        send_mail(
             subject="Welcome to iSchool Ole – You're Hired!",
            message=f"Dear {user.full_name},\n\nYou’ve been hired as a teacher on iSchool Ole.\n\nLogin credentials:\nEmail: {user.email}\nPassword: {password}\n\nLogin to your dashboard and get started!\n\nRegards,\niSchool Ola Team",
            from_email="noreply@ischool.ng",
            recipient_list=[user.email]
                )

        return Response({'message': 'Teacher hired and account created.'}, status=201)


class TeacherApplicationListView(ListAPIView):
    queryset = TeacherApplication.objects.all().order_by('-applied_at')
    serializer_class = TeacherApplicationSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']


class UpdateTeacherStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, application_id):
        new_status = request.data.get('status')
        if new_status not in ['pending', 'shortlisted', 'hired', 'rejected']:
            return Response({'error': 'Invalid status'}, status=400)

        application = get_object_or_404(TeacherApplication, id=application_id)
        application.status = new_status
        application.save()

        return Response({'message': f'Status updated to {new_status}'})


class TeacherApplicationStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=400)

        try:
            application = TeacherApplication.objects.get(email=email)
        except TeacherApplication.DoesNotExist:
            return Response({'error': 'Application not found'}, status=404)

        serializer = TeacherApplicationSerializer(application)
        return Response(serializer.data)



# ----------------------
# AUTHENTICATION
# ----------------------

class TeacherLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']

            if user.role != 'teacher':
                return Response({'error': 'Not a teacher account.'}, status=status.HTTP_403_FORBIDDEN)

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user': {
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                }
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# ----------------------
# CLASS SCHEDULE / TIMETABLE
# ----------------------

class DailyTimetableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'teacher':
            return Response({'detail': 'Access denied.'}, status=403)

        today = timezone.localdate()
        schedules = LiveClassSchedule.objects.filter(teacher=user, date=today).order_by('start_time')
        serializer = DailyTimetableSerializer(schedules, many=True)
        return Response(serializer.data)


class UpcomingGroupedClassesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'teacher':
            return Response({'detail': 'Only teachers can access this'}, status=403)

        today = date.today()
        schedules = LiveClassSchedule.objects.filter(teacher=user, date__gte=today).order_by('date', 'start_time')

        grouped = defaultdict(list)
        for schedule in schedules:
            key = (schedule.subject.name, schedule.class_level.name)
            grouped[key].append(schedule)

        result = []
        for (subject, class_level), items in grouped.items():
            serializer = SimpleClassScheduleSerializer(items, many=True)
            result.append({
                "subject": subject,
                "class_level": class_level,
                "classes": serializer.data
            })

        final = UpcomingGroupedClassesSerializer(result, many=True)
        return Response(final.data)


class DailyScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        teacher = request.user
        today = date.today()
        schedule = LiveClassSchedule.objects.filter(teacher=teacher, date=today)
        serializer = LiveClassScheduleSerializer(schedule, many=True)
        return Response(serializer.data)


class StartLiveClassView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, schedule_id):
        user = request.user

        try:
            schedule = LiveClassSchedule.objects.get(id=schedule_id, teacher=user)
        except LiveClassSchedule.DoesNotExist:
            return Response({"error": "Schedule not found or not assigned to you."}, status=404)

        if not OleStudentMatch.objects.filter(schedule=schedule).exists():
            return Response({"error": "No students matched to this class yet."}, status=400)

        if LiveClassSession.objects.filter(schedule=schedule).exists():
            return Response({"error": "Class session already started."}, status=400)

        # ✅ Safe room name with lowercase, no spaces or special chars
        timestamp = int(datetime.now().timestamp())
        safe_room_name = f"oleclass2025-{schedule.id}-{uuid.uuid4().hex[:6]}"
        jitsi_url = f"https://meet.jit.si/{safe_room_name}"

        session = LiveClassSession.objects.create(
            schedule=schedule,
            meeting_link=jitsi_url
        )

        return Response({
            "message": "Session started.",
            "meeting_link": jitsi_url,
            "session_id": session.id
        }, status=201)

    
class LiveClassSessionDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = LiveClassSession.objects.all()
    serializer_class = LiveClassSessionSerializer

    def get_queryset(self):
        # Optional: limit sessions to the teacher requesting
        return self.queryset.filter(schedule__teacher=self.request.user)


# ----------------------
# LESSON PLAN / E-LIBRARY
# ----------------------

class LessonPlanListView(generics.ListAPIView):
    serializer_class = OleLessonPlanSerializer
    permission_classes = [IsAuthenticated]
    queryset = OleLessonPlan.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['subject', 'class_level']


class SetLessonPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(LiveClassSession, id=session_id, schedule__teacher=request.user)
        lesson_plan = get_object_or_404(OleLessonPlan, id=request.data.get("lesson_plan_id"))

        session.lesson_plan = lesson_plan
        session.save()

        return Response({
            "message": "Lesson plan assigned.",
            "lesson_plan": OleLessonPlanSerializer(lesson_plan).data
        })


class AssignChapterToSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(LiveClassSession, id=session_id, schedule__teacher=request.user)
        chapter = get_object_or_404(ELibraryChapter, id=request.data.get("chapter_id"))

        SessionReference.objects.update_or_create(session=session, defaults={'chapter': chapter})

        return Response({
            "message": "Chapter assigned.",
            "chapter": ELibraryChapterSerializer(chapter).data
        })


# ----------------------
# ATTENDANCE & ANALYTICS
# ----------------------

class LatestAttendanceLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'teacher':
            return Response({'detail': 'Access denied.'}, status=403)

        logs = AttendanceLog.objects.filter(
            session__schedule__teacher=user
        ).select_related('student', 'session__schedule__subject', 'session__schedule__class_level').order_by('-joined_at')[:10]

        data = [
            {
                "student": log.student.full_name,
                "subject": log.session.schedule.subject.name,
                "class_level": log.session.schedule.class_level.name,
                "joined_at": log.joined_at,
            }
            for log in logs
        ]
        return Response(data)


class WeeklySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'teacher':
            return Response({'detail': 'Access denied.'}, status=403)

        today = timezone.localdate()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)

        sessions = LiveClassSession.objects.filter(
            schedule__teacher=user,
            schedule__date__range=[start_week, end_week]
        )

        total_classes = sessions.count()
        total_students = AttendanceLog.objects.filter(session__in=sessions).count()

        return Response({
            "week_range": f"{start_week} to {end_week}",
            "total_classes_held": total_classes,
            "total_students_attended": total_students
        })
    

MAX_VISIBLE_STUDENTS = 10


class MatchedStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, schedule_id):
        schedule = get_object_or_404(LiveClassSchedule, id=schedule_id, teacher=request.user)

        matched = OleStudentMatch.objects.filter(schedule=schedule).select_related('student')[:MAX_VISIBLE_STUDENTS]
        students = [match.student for match in matched]

        serializer = OleStudentBasicSerializer(students, many=True)
        return Response(serializer.data)



class TeacherInterviewView(generics.GenericAPIView):
    serializer_class = TeacherInterviewSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, application_id):
        return TeacherInterview.objects.filter(application_id=application_id).first()

    def get(self, request, application_id):
        interview = self.get_object(application_id)
        if not interview:
            return Response({"detail": "Interview not found."}, status=404)
        return Response(TeacherInterviewSerializer(interview).data)

    def post(self, request, application_id):
        interview = self.get_object(application_id)
        data = request.data.copy()
        data['application'] = application_id
        serializer = self.serializer_class(instance=interview, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class OleClassLevelListView(APIView):
    permission_classes = [AllowAny]  # 👈 Add this
    def get(self, request):
        levels = OleClassLevel.objects.all()
        serializer = OleClassLevelSerializer(levels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class OleSubjectListView(APIView):
    permission_classes = [AllowAny]  # 👈 Add this
    def get(self, request):
        class_level_id = request.GET.get("class_level_id")
        subjects = OleSubject.objects.all()

        if class_level_id:
            from .models import OleTopic
            subject_ids = OleTopic.objects.filter(class_level_id=class_level_id).values_list("subject_id", flat=True).distinct()
            subjects = subjects.filter(id__in=subject_ids)

        serializer = OleSubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentUpcomingLessonsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.localdate()

        matches = OleStudentMatch.objects.filter(
            student=user,
            schedule__date__gte=now
        ).select_related('schedule__subject', 'schedule__class_level', 'schedule__teacher')

        lessons = [match.schedule for match in matches]
        serializer = LiveClassScheduleDetailSerializer(lessons, many=True)

        return Response(serializer.data)
    

class LessonHistoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        history = OleStudentTopicHistory.objects.filter(student=user).order_by('-viewed_on')
        serializer = OleStudentTopicHistorySerializer(history, many=True, context={'request': request})
        return Response(serializer.data)


class TeacherPayslipDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, year, month):
        user = request.user
        if user.role != 'teacher':
            return HttpResponse(status=403)

        try:
            payroll = TeacherPayroll.objects.get(
                teacher=user,
                month__year=year,
                month__month=month
            )
        except TeacherPayroll.DoesNotExist:
            raise Http404("Payslip not found")

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "iSchool Payslip")
        y -= 30

        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Teacher: {payroll.teacher.full_name}")
        p.drawString(50, y - 20, f"Month: {payroll.month.strftime('%B %Y')}")
        p.drawString(50, y - 40, f"Lessons Taken: {payroll.total_lessons}")
        p.drawString(50, y - 60, f"Amount Paid: ₦{payroll.amount_paid}")
        p.drawString(50, y - 80, f"Paid On: {payroll.paid_on.strftime('%Y-%m-%d')}")

        p.showPage()
        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf')


class TopicLessonPlanListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        subject_id = request.GET.get("subject_id")
        class_level_id = request.GET.get("class_level_id")

        topics = OleTopic.objects.all()
        if subject_id:
            topics = topics.filter(subject_id=subject_id)
        if class_level_id:
            topics = topics.filter(class_level_id=class_level_id)

        serializer = OleTopicWithPlansSerializer(topics, many=True)
        return Response(serializer.data)



class MarkLessonCompletedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        user = request.user

        try:
            lesson = OleLesson.objects.get(id=lesson_id, teacher=user)
        except OleLesson.DoesNotExist:
            return Response({"error": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)

        lesson.completed = True
        lesson.completed_at = now()
        lesson.save()

        return Response({"message": "Lesson marked as completed."}, status=status.HTTP_200_OK)


class ToggleLessonChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        try:
            lesson = OleLesson.objects.get(id=lesson_id, teacher=request.user)
        except OleLesson.DoesNotExist:
            return Response({"error": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)

        lesson.is_chat_enabled = not lesson.is_chat_enabled
        lesson.save()
        return Response({
            "message": "Chat toggled.",
            "is_chat_enabled": lesson.is_chat_enabled
        }, status=status.HTTP_200_OK)


class LeaveLessonView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        user = request.user
        try:
            attendance = AttendanceLog.objects.get(lesson_id=lesson_id, student=user)
        except AttendanceLog.DoesNotExist:
            return Response({"error": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)

        attendance.left_at = now()
        attendance.save()
        return Response({"message": "Left time logged."})
    

