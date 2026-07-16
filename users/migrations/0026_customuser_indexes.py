"""Add indexes on CustomUser hot filter columns (role, subscription, group)."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0025_studentslot_password_blank"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="customuser",
            index=models.Index(fields=["role"], name="user_role_idx"),
        ),
        migrations.AddIndex(
            model_name="customuser",
            index=models.Index(fields=["subscription_expires_on"], name="user_sub_expires_idx"),
        ),
        migrations.AddIndex(
            model_name="customuser",
            index=models.Index(fields=["registration_group"], name="user_reg_group_idx"),
        ),
    ]
