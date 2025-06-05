from django.apps import AppConfig


class KistrecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kistrecords'
    
    def ready(self):
        import kistrecords.signals
