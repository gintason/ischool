from django.apps import AppConfig


class IschoolOleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teachers"

    def ready(self):
        import teachers.signals

