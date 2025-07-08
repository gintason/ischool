# teachers/serializers.py
from rest_framework import serializers
from .models import TeacherApplication

from .models import (LiveClassSchedule, OleSubject, OleClassLevel, OleTopic,  
                     OleStudentMatch, TeacherLessonSummary, 
                     AttendanceLog, TeacherInterview, OleStudentTopicHistory,
                     OleLessonPlan, LiveClassSession)

from users.models import CustomUser
from .models import SessionReference
from elibrary.serializers import ELibraryChapterSerializer
from rest_framework import serializers

class TeacherApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherApplication
        fields = '__all__'
        read_only_fields = ['status', 'applied_at']

    def validate_email(self, value):
        if TeacherApplication.objects.filter(email=value).exists():
            raise serializers.ValidationError("An application with this email already exists.")
        return value
    

class DailyTimetableSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField()
    class_level = serializers.StringRelatedField()

    class Meta:
        model = LiveClassSchedule
        fields = ['id', 'subject', 'class_level', 'date', 'start_time', 'end_time']


class UpcomingSessionSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    class Meta:
        model = LiveClassSchedule
        fields = ['id', 'date', 'start_time', 'end_time']


class GroupedScheduleSerializer(serializers.Serializer):
    subject = serializers.CharField()
    class_level = serializers.CharField()
    sessions = UpcomingSessionSerializer(many=True)


class UpcomingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveClassSchedule
        fields = ['id', 'date', 'start_time', 'end_time']


class VisibleStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email']


class UpcomingSessionSerializer(serializers.ModelSerializer):
    visible_students = serializers.SerializerMethodField()

    class Meta:
        model = LiveClassSchedule
        fields = ['id', 'subject', 'class_level', 'date', 'start_time', 'end_time', 'visible_students']

    def get_visible_students(self, obj):
        from .views import VISIBLE_STUDENTS_PER_CLASS  # import constant from views or a constants file
        matched = OleStudentMatch.objects.filter(schedule=obj).order_by('?')[:VISIBLE_STUDENTS_PER_CLASS]
        return VisibleStudentSerializer([match.student for match in matched], many=True).data
    

class SessionReferenceSerializer(serializers.ModelSerializer):
    chapter = ELibraryChapterSerializer()

    class Meta:
        model = SessionReference
        fields = ['id', 'session', 'chapter']
        


class LiveClassScheduleSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='subject.name')
    class_level = serializers.CharField(source='class_level.name')
    session = serializers.SerializerMethodField()

    class Meta:
        model = LiveClassSchedule
        fields = ['id', 'subject', 'class_level', 'date', 'start_time', 'end_time', 'session']

    def get_session(self, obj):
        try:
            session = obj.liveclasssession  # one-to-one reverse relation
            return {
                'id': session.id,
                'meeting_link': session.meeting_link,
                'status': session.status,
            }
        except:
            return None



class SimpleClassScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveClassSchedule
        fields = ['id', 'date', 'start_time', 'end_time']


# Grouped serializer
class UpcomingGroupedClassesSerializer(serializers.Serializer):
    subject = serializers.CharField()
    class_level = serializers.CharField()
    classes = SimpleClassScheduleSerializer(many=True)

class TeacherLessonSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherLessonSummary
        fields = ['week_start', 'week_end', 'total_lessons_taken']


class AttendanceLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name')

    class Meta:
        model = AttendanceLog
        fields = ['student_name', 'joined_at']
        

class TeacherInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherInterview
        fields = '__all__'
        read_only_fields = ['recorded_at']


class OleClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OleClassLevel
        fields = ['id', 'name']

class OleSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = OleSubject
        fields = ['id', 'name']


class OleTopicSerializer(serializers.ModelSerializer):
    subject = OleSubjectSerializer()
    class_level = OleClassLevelSerializer()
    material_url = serializers.SerializerMethodField()

    class Meta:
        model = OleTopic
        fields = ['id', 'title', 'description', 'reference_material', 'material_url', 'subject', 'class_level']

    def get_material_url(self, obj):
        request = self.context.get('request')
        if obj.reference_material:
            return request.build_absolute_uri(obj.reference_material.url)
        return None


class OleStudentTopicHistorySerializer(serializers.ModelSerializer):
    topic = OleTopicSerializer()

    class Meta:
        model = OleStudentTopicHistory
        fields = ['id', 'topic', 'viewed_on']


class OleLessonPlanSerializer(serializers.ModelSerializer):
    topic = serializers.StringRelatedField()
    class_level = serializers.CharField(source='topic.class_level.name')
    subject = serializers.CharField(source='topic.subject.name')

    class Meta:
        model = OleLessonPlan
        fields = ['id', 'topic', 'subject', 'class_level', 'reference_material']


class OleTopicWithPlansSerializer(serializers.ModelSerializer):
    lesson_plans = OleLessonPlanSerializer(many=True, read_only=True)

    class Meta:
        model = OleTopic
        fields = ['id', 'title', 'description', 'reference_material', 'subject', 'class_level', 'lesson_plans']


class LiveClassSessionSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='schedule.subject.name')
    class_level = serializers.CharField(source='schedule.class_level.name')
    date = serializers.DateField(source='schedule.date')
    start_time = serializers.TimeField(source='schedule.start_time')
    end_time = serializers.TimeField(source='schedule.end_time')
    lesson_plan = serializers.SerializerMethodField()

    class Meta:
        model = LiveClassSession
        fields = ['id', 'subject', 'class_level', 'date', 'meeting_link', 'start_time', 'end_time', 'lesson_plan']

    def get_lesson_plan(self, obj):
        if obj.lesson_plan:
            return {
                "id": obj.lesson_plan.id,
                "topic": obj.lesson_plan.topic
            }
        return None