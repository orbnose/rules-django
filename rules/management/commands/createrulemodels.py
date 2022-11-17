import importlib

from django.conf import settings
from django.core.management.base import BaseCommand

from ...rule_manager import RuleManager

class Command(BaseCommand):

    def handle(self, *args, **options):
        for module_name in settings.RULES_MODELS_SETUP_MODULES:
            module = importlib.import_module(module_name)
            for attr in dir(module):
                var = getattr(module, attr)
                if isinstance(var, RuleManager):
                    var.build_models()