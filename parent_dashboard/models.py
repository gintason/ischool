from django.db import models
from django.db import models
from users.models import CustomUser

class ParentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Parent: {self.user.full_name}"

