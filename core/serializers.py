from rest_framework import serializers
from .models import RegistrationSource, StudentSlot, ContactOleMessage,  ContactOla
from django.conf import settings

class RegistrationSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationSource
        fields = '__all__'


class StudentSlotSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = StudentSlot
        fields = ['id', 'registration_source', 'user', 'user_email', 'serial_number']


class ContactOleMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactOleMessage
        fields = ['id', 'full_name', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class ContactOlaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactOla
        fields = ['id', 'full_name', 'email', 'message', 'submitted_at']