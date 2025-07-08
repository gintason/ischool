from rest_framework import serializers
from users.models import CustomUser

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'role']
