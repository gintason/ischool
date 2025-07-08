from rest_framework import serializers
from .models import Question, CLASS_CHOICES, Test, TestResult



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
            "options",  # new field
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
        # Always remove internal fields from frontend response
        data.pop("option_a", None)
        data.pop("option_b", None)
        data.pop("option_c", None)
        data.pop("option_d", None)
        data.pop("correct_answer", None)  # Hide correct answer from frontend
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
    session_id = serializers.UUIDField()  # Fix this line
    answers = AnswerItemSerializer(many=True)


class TestResultSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ['subject', 'score', 'total_questions', 'created_at']
        read_only_fields = fields

    date_taken = serializers.DateTimeField(source='created_at', read_only=True)


# test_app/serializers.py

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'subject', 'topic', 'class_level', 'created_by', 'date_created']
        read_only_fields = ['id', 'created_by', 'date_created']

