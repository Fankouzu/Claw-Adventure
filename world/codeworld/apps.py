from django.apps import AppConfig


class CodeworldConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "world.codeworld"
    label = "codeworld"
    verbose_name = "Code-defined world sync"
