from django.apps import AppConfig


class ConflictReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.conflict_reports'
    verbose_name = 'Conflict Reports'

    def ready(self):
        pass
