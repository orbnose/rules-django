from django.core.management import call_command
from django.test import TestCase, override_settings

from ..models import Rule, RuleActionPair, Condition, BoolOperator, Property, Action
from ._trafficlightrules import TrafficLightRuleManager, Trafficlight

class TestEvalRules(TestCase):
    
    @override_settings(RULES_MODELS_SETUP_MODULES=["rules.tests._trafficlightrules"])
    def setUp(self):
        call_command('createrulemodels')
        build_turn_yellow_rule()
        build_turn_red_rule()
        build_turn_green_rule()
        
    def test_check_rule_action_pair_jsonlogic_if_statement_with_prepopulated_properties(self):
        rule = Rule.objects.get(name="turn-yellow")
        rap = RuleActionPair.objects.get(rule=rule)
        self.assertEqual(
            rap.jsonlogic_if_statement,
            { "if": [
                { "==" : [
                    {"var" : "get_trafficlight_color" },
                    'green'
                ]},
                "set_color_to_yellow",
                "do_nothing"
            ]}
        )
    
    def test_eval_first_true_rule(self):
        tl = Trafficlight()
        rules = ["turn-yellow", "turn-green", "turn-red"]
        
        #turn yellow
        rule_results = TrafficLightRuleManager.eval_first_true_rule(
            *rules,
            trafficlight=tl,
            trafficlight_color=tl.color,
            trafficlight_counter=tl.counter)
        tl = rule_results["trafficlight"]
        self.assertEqual(
            tl.color,
            'yellow'
        )

        #turn red
        rule_results = TrafficLightRuleManager.eval_first_true_rule(
            *rules,
            trafficlight=tl,
            trafficlight_color=tl.color,
            trafficlight_counter=tl.counter)
        tl = rule_results["trafficlight"]
        self.assertEqual(
            tl.color,
            'red'
        )

        #turn green
        rule_results = TrafficLightRuleManager.eval_first_true_rule(
            *rules,
            trafficlight=tl,
            trafficlight_color=tl.color,
            trafficlight_counter=tl.counter)
        tl = rule_results["trafficlight"]
        self.assertEqual(
            tl.color,
            'green'
        )
        

def build_turn_yellow_rule():
    build_turn_color_rule(color="yellow", prev_color="green")

def build_turn_red_rule():
    build_turn_color_rule(color="red", prev_color="yellow")

def build_turn_green_rule():
    build_turn_color_rule(color="green", prev_color="red")

def build_turn_color_rule(color, prev_color):
    turn_color_rule = Rule(
            name = str("turn-" + color),
            logic_string = "1",
            jsonlogic_only_boolean_symbols = {},
            jsonlogic_full_conditions = {},
            num_conditions = 1,
        )
    turn_color_rule.save()
    cond = Condition(
        rule = turn_color_rule,
        rule_index = 1,
        operand_subject = Property.objects.get(function_name="get_trafficlight_color", context_type="trafficlight_color"),
        operand_object = Property.objects.get(function_name="freetext", context_type="trafficlight_color"),
        freetext_object = prev_color,
        operator = BoolOperator.objects.get(jsonlogic_operator="==", context_type="trafficlight_color"),
        jsonlogic_condition = {},
    )
    cond.save()
    rap = RuleActionPair(
        jsonlogic_if_statement = {},
        rule = turn_color_rule,
        action = Action.objects.get( function_name=str("set_color_to_" + color) ),
    )
    rap.set_jsonlogic_if_statement()
    rap.save()
