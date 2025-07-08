from rest_framework import serializers
from .models import ParentProfile
from users.models import CustomUser

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'role']

class ParentProfileSerializer(serializers.ModelSerializer):
    user = ParentSerializer()

    class Meta:
        model = ParentProfile
        fields = ['user', 'phone_number']
