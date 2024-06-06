from django.apps import AppConfig
from django.core.signals import request_finished

class MainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_app'
    verbose_name = 'Основной модуль'

    def ready(self):
        from . import signals