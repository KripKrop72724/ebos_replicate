from django.apps import AppConfig


class Ebos2206Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ebos2206"
    verbose_name = "M06-Payroll"

    def ready(self):
        import ebos2206.signals
