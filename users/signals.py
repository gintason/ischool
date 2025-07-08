from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, OleStudentProfile

@receiver(post_save, sender=CustomUser)
def create_ole_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == "ole_student":
        OleStudentProfile.objects.get_or_create(user=instance)