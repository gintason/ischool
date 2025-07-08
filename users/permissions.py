
from rest_framework.permissions import BasePermission



class IsStudentUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsParentUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'parent'
    
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsTeacherUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'teacher'

class IsOleStudentUser(BasePermission):  # ✅ New role-specific permission
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ole_student'
