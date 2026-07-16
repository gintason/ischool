"""
Remove the duplicate "SSS2" class level, keeping "SS2" as the single record.

"SS2" and "SSS2" refer to the same class. Any records attached to SSS2 are first
reassigned to SS2, then SSS2 is deleted. Written defensively so it's safe to run
whether or not either level exists, and whether or not anything is attached —
the audit at authoring time showed both empty, but production may differ.
"""
from django.db import migrations

KEEP = "SS2"
DROP = "SSS2"


def merge_sss2_into_ss2(apps, schema_editor):
    OleClassLevel = apps.get_model("teachers", "OleClassLevel")

    keep = OleClassLevel.objects.filter(name=KEEP).first()
    drop = OleClassLevel.objects.filter(name=DROP).first()

    if drop is None:
        return  # nothing to do
    if keep is None:
        # No SS2 to merge into — just rename SSS2 to SS2 and finish.
        drop.name = KEEP
        drop.save()
        return

    # Reassign every FK that points at the class level. Model names are resolved
    # via the historical app registry so this stays correct over time.
    fk_targets = [
        ("teachers", "OleTopic", "class_level"),
        ("teachers", "TeacherAssignment", "class_level"),
        ("teachers", "LiveClassSchedule", "class_level"),
        ("teachers", "OleLessonPlan", "class_level"),
        ("teachers", "OleMaterial", "class_level"),
        ("teachers", "OleLesson", "class_level"),
        ("users", "OleStudentProfile", "class_level"),
    ]
    for app_label, model_name, field in fk_targets:
        try:
            Model = apps.get_model(app_label, model_name)
        except LookupError:
            continue
        Model.objects.filter(**{field: drop}).update(**{field: keep})

    drop.delete()


def reverse(apps, schema_editor):
    """Recreate an empty SSS2 so the migration is reversible (records aren't split back)."""
    OleClassLevel = apps.get_model("teachers", "OleClassLevel")
    OleClassLevel.objects.get_or_create(name=DROP)


class Migration(migrations.Migration):

    dependencies = [
        ("teachers", "0012_remove_olestudentmatch_unique_schedule_student_match_and_more"),
    ]

    operations = [
        migrations.RunPython(merge_sss2_into_ss2, reverse),
    ]
