from teachers.models import TeacherAssignment, OleSubject, OleClassLevel
from users.models import CustomUser

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
    # Add more assignments here
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

        print(f"✅ Assigned {teacher.full_name} to {subject.name} - {level.name}")
    except Exception as e:
        print(f"❌ Error: {e}")
