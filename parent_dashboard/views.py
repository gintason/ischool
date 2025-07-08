from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from users.permissions import IsParentUser
from .models import ParentProfile
from .serializers import ParentProfileSerializer

class ParentDashboardView(APIView):
    permission_classes = [IsParentUser]

    def get(self, request):
        try:
            profile = ParentProfile.objects.get(user=request.user)
            serializer = ParentProfileSerializer(profile)
            return Response({"message": "Welcome Parent!", "data": serializer.data})
        except ParentProfile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=404)


