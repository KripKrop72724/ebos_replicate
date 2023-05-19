from django.apps import AppConfig


class ebos2201Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ebos2201"
    verbose_name = "M01-Foundation"

    def ready(self):
        import ebos2201.signals
