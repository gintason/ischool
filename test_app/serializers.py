# test_app/serializers.py
from rest_framework import serializers
from .models import Question, CLASS_CHOICES, Test, TestResult, Subject, Topic

# NEW: Subject Serializer
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'class_level', 'description']

# NEW: Topic Serializer
class TopicSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Topic
        fields = ['id', 'name', 'subject', 'subject_name', 'description', 'order']

class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "question_type",
            "text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "options",
        ]

    def get_options(self, obj):
        if obj.question_type == "mcq":
            return {
                "A": obj.option_a,
                "B": obj.option_b,
                "C": obj.option_c,
                "D": obj.option_d,
            }
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("option_a", None)
        data.pop("option_b", None)
        data.pop("option_c", None)
        data.pop("option_d", None)
        data.pop("correct_answer", None)
        return data

class StartTestSerializer(serializers.Serializer):
    class_level = serializers.ChoiceField(choices=CLASS_CHOICES)
    subject = serializers.CharField()
    topic = serializers.CharField()

class AnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.CharField()

    def validate(self, data):
        try:
            question = Question.objects.get(id=data['question_id'])
        except Question.DoesNotExist:
            raise serializers.ValidationError("Invalid question ID.")

        if question.question_type == "mcq":
            if data['answer'] not in ['A', 'B', 'C', 'D']:
                raise serializers.ValidationError("Invalid MCQ option. Must be A, B, C, or D.")
        elif question.question_type == "theory":
            if not data['answer'].strip():
                raise serializers.ValidationError("Theory answer cannot be empty.")
        return data

class SubmitTestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    answers = AnswerItemSerializer(many=True)

class TestResultSummarySerializer(serializers.ModelSerializer):
    date_taken = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = TestResult
        fields = ['subject', 'score', 'total_questions', 'date_taken']
        read_only_fields = fields

# Updated Test Serializer
class TestSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    
    class Meta:
        model = Test
        fields = ['id', 'subject', 'subject_name', 'topic', 'topic_name', 'class_level', 'created_by', 'date_created']
        read_only_fields = ['id', 'created_by', 'date_created']

