# in teachers/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from teachers.models import LiveClassSchedule
from .utils.scheduler import auto_match_students_to_schedule

@receiver(post_save, sender=LiveClassSchedule)
def match_students_on_schedule_create(sender, instance, created, **kwargs):
    if created:
        matched = auto_match_students_to_schedule(instance)
        print(f"[AUTO MATCH] {matched} students matched to schedule #{instance.id}")
