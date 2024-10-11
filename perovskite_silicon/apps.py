from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'perovskite_silicon'  # Replace 'myapp' with your actual app name

    def ready(self):
        # Import and execute your Python file here
        from . import custom_materials
        custom_materials.run()