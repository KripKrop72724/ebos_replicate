from django.apps import AppConfig


class Ebos2210Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ebos2210"
    verbose_name = "M10-Finance"

    def ready(self):
        import ebos2210.signals
