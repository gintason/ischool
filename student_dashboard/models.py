from django.db import models
from users.models import CustomUser

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    grade_level = models.CharField(max_length=10)

    def __str__(self):
        return f"Student: {self.user.full_name}"


    
 
