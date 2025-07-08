from django.core.management.base import BaseCommand
from teachers.models import TeacherAssignment, OleSubject, OleClassLevel
from users.models import CustomUser

class Command(BaseCommand):
    help = "Assigns teachers to class levels and subjects"

    def handle(self, *args, **kwargs):
        teacher_assignments = [
            {
                "email": "teacher1@example.com",
                "subject": "Mathematics",
                "class_level": "JSS1"
            },
            {
                "email": "teacher2@example.com",
                "subject": "English Language",
                "class_level": "JSS1"
            },
            # Add more as needed
        ]

        for assign in teacher_assignments:
            try:
                teacher = CustomUser.objects.get(email=assign["email"])
                subject = OleSubject.objects.get(name=assign["subject"])
                level = OleClassLevel.objects.get(name=assign["class_level"])

                TeacherAssignment.objects.get_or_create(
                    teacher=teacher,
                    subject=subject,
                    class_level=level
                )

                self.stdout.write(self.style.SUCCESS(
                    f"✅ Assigned {teacher.full_name} to {subject.name} - {level.name}"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
