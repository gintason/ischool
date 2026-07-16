"""
Make StudentSlot.password blank-by-default and purge existing raw values.

StudentSlot is bookkeeping, not a login account — real credentials live on
CustomUser (hashed). Storing a usable password here (previously equal to the
username) was both pointless and a data-exposure risk, so existing values are
blanked out.
"""
from django.db import migrations, models


def blank_existing_passwords(apps, schema_editor):
    StudentSlot = apps.get_model("users", "StudentSlot")
    StudentSlot.objects.exclude(password="").update(password="")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0024_customuser_phone_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studentslot",
            name="password",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.RunPython(blank_existing_passwords, noop),
    ]
