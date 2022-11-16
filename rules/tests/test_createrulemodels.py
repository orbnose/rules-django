from django.core.management import call_command
from django.test import TestCase, override_settings

from ..models import Property, Action, BoolOperator

class TestCreateRuleModels(TestCase):
    
    @override_settings(RULES_MODELS_SETUP_MODULES=["rules.tests.trafficlightrules"])
    def setUp(self):
        call_command('createrulemodels')

    def test_createrulemodels(self):
        self.assertEquals(
            Property.objects.get(function_name="get_trafficlight_color").context_type,
            "trafficlight_color"
        )
        self.assertEquals(
            Property.objects.get(function_name="get_trafficlight_counter").context_type,
            "trafficlight_counter"
        )
        self.assertEquals(
            sorted([boolop.jsonlogic_operator for boolop in BoolOperator.objects.filter(context_type="trafficlight_counter")]),
            sorted(["==",">"])
        )
        self.assertEquals(
            BoolOperator.objects.get(context_type="trafficlight_color").jsonlogic_operator,
            "=="
        )
        self.assertEquals(
            Action.objects.get(function_name="set_color_to_green").context_type,
            "trafficlight"
        )
        self.assertEquals(
            Action.objects.get(function_name="set_color_to_yellow").context_type,
            "trafficlight"
        )
        self.assertEquals(
            Action.objects.get(function_name="set_color_to_red").context_type,
            "trafficlight"
        )
        self.assertEquals(
            Action.objects.get(function_name="increment_counter").context_type,
            "trafficlight"
        )
        self.assertEquals(
            Action.objects.get(function_name="reset_counter").context_type,
            "trafficlight"
        )