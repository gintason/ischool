from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from users.permissions import IsTeacherUser
from .serializers import TeacherSerializer

class TeacherDashboardView(APIView):
    permission_classes = [IsTeacherUser]

    def get(self, request):
        serializer = TeacherSerializer(request.user)
        return Response({"message": "Welcome Teacher!", "data": serializer.data})

