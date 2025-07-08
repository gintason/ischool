from django.shortcuts import render
# Create your views here.
from rest_framework import generics
from .models import ELibraryChapter
from .serializers import ELibraryChapterSerializer
from rest_framework.permissions import IsAuthenticated

class ELibraryChapterListView(generics.ListAPIView):
    queryset = ELibraryChapter.objects.all()
    serializer_class = ELibraryChapterSerializer
    permission_classes = [IsAuthenticated]
