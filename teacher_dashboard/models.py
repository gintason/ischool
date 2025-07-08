from django.db import models

from django.db import models
from users.models import CustomUser

class TeacherProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return self.user.full_name

