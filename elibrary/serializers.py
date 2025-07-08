from rest_framework import serializers
from .models import ELibraryChapter

class ELibraryChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ELibraryChapter
        fields = '__all__'
