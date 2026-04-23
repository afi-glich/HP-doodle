from django.apps import AppConfig

class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'
    verbose_name = 'Doodle Events'
    
    def ready(self):
        """Initialize app"""
        from .env import init_db
        # Uncomment to auto-create tables on startup
        # init_db()