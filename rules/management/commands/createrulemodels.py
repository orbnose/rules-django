import importlib

from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        for module in settings.RULES_MODELS_SETUP_MODULES:
            importlib.import_module(module)