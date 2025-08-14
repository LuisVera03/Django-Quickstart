from django.apps import AppConfig


class RestBasicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rest'

    def ready(self):
        import rest.signals