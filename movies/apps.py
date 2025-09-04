from django.apps import AppConfig

class MoviesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movies"

    def ready(self):
        # Ensure post_save signals for UserProfile are registered
        import movies.signals  # noqa
