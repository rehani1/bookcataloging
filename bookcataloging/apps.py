from django.apps import AppConfig


class BookcatalogingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookcataloging'

    def ready(self):
        import bookcataloging.signals
