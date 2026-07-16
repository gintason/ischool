"""Add composite index on OleTopic(class_level, subject) for the subjects-by-level lookup."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teachers", "0013_merge_sss2_into_ss2"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="oletopic",
            index=models.Index(
                fields=["class_level", "subject"], name="oletopic_level_subject_idx"
            ),
        ),
    ]
