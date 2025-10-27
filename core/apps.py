from django.apps import AppConfig
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    def ready(self):
<<<<<<< HEAD
        import core.signals
=======
        import core.signals
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
