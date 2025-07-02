from django.apps import AppConfig


class RestBasicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rest_basic'

    def ready(self):
        import rest_basic.signals