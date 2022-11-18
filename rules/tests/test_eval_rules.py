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
        build_turn_yellow_on_counter()
        build_turn_red_on_counter()
        build_turn_green_on_counter()
        build_reset_counter_rule()
        build_inc_counter_rule()
        
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

    def test_eval_all_rules(self):
        tl = Trafficlight()
        rules = ['count-turn-yellow', 'count-turn-red', 'count-turn-green', 'reset_counter_rule', 'inc_counter_rule']
        
        for i in range(5):
            rule_results = TrafficLightRuleManager.eval_all_rules(
                *rules,
                trafficlight=tl,
                trafficlight_color=tl.color,
                trafficlight_counter=tl.counter)
            tl = rule_results["trafficlight"]
            self.assertEqual(
                tl.color,
                'green'
            )
        for i in range(6):
            rule_results = TrafficLightRuleManager.eval_all_rules(
                *rules,
                trafficlight=tl,
                trafficlight_color=tl.color,
                trafficlight_counter=tl.counter)
            tl = rule_results["trafficlight"]
            self.assertEqual(
                tl.color,
                'yellow'
            )
        for i in range(6):
            rule_results = TrafficLightRuleManager.eval_all_rules(
                *rules,
                trafficlight=tl,
                trafficlight_color=tl.color,
                trafficlight_counter=tl.counter)
            tl = rule_results["trafficlight"]
            self.assertEqual(
                tl.color,
                'red'
            )
        for i in range(6):
            rule_results = TrafficLightRuleManager.eval_all_rules(
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

def build_turn_yellow_on_counter():
    build_turn_on_counter_rule('yellow', 'green')

def build_turn_red_on_counter():
    build_turn_on_counter_rule('red', 'yellow')

def build_turn_green_on_counter():
    build_turn_on_counter_rule('green', 'red')

def build_turn_on_counter_rule(color, prev_color):
    turn_color_rule = Rule(
        name = str("count-turn-" + color),
        logic_string = "1 AND 2",
        jsonlogic_only_boolean_symbols = {},
        jsonlogic_full_conditions = {},
        num_conditions = 2
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
    cond2 = Condition(
        rule = turn_color_rule,
        rule_index = 2,
        operand_subject = Property.objects.get(function_name="get_trafficlight_counter", context_type="trafficlight_counter"),
        operand_object = Property.objects.get(function_name="freetext", context_type="trafficlight_counter"),
        freetext_object = 4,
        operator = BoolOperator.objects.get(jsonlogic_operator=">", context_type="trafficlight_counter"),
        jsonlogic_condition = {},
    )
    cond2.save()
    rap = RuleActionPair(
        jsonlogic_if_statement = {},
        rule = turn_color_rule,
        action = Action.objects.get(function_name=str("set_color_to_" + color))
    )
    rap.set_jsonlogic_if_statement()
    rap.save()

def build_reset_counter_rule():
    reset_counter_rule = Rule(
        name = "reset_counter_rule",
        logic_string = "1",
        num_conditions = 1,
        jsonlogic_only_boolean_symbols = {},
        jsonlogic_full_conditions = {},
    )
    reset_counter_rule.save()
    cond = Condition(
        rule = reset_counter_rule,
        rule_index = 1,
        operand_subject = Property.objects.get(function_name="get_trafficlight_counter", context_type="trafficlight_counter"),
        operand_object = Property.objects.get(function_name="freetext", context_type="trafficlight_counter"),
        freetext_object = 4,
        operator = BoolOperator.objects.get(jsonlogic_operator=">", context_type="trafficlight_counter"),
        jsonlogic_condition = {},
    )
    cond.save()
    rap = RuleActionPair(
        jsonlogic_if_statement = {},
        rule = reset_counter_rule,
        action = Action.objects.get(function_name='reset_counter')
    )
    rap.set_jsonlogic_if_statement()
    rap.save()

def build_inc_counter_rule():
    inc_counter_rule = Rule(
        name = "inc_counter_rule",
        logic_string = "1",
        num_conditions = 1,
        jsonlogic_only_boolean_symbols = {},
        jsonlogic_full_conditions = {},
    )
    inc_counter_rule.save()
    cond = Condition(
        rule = inc_counter_rule,
        rule_index = 1,
        operand_subject = Property.objects.get(function_name="get_trafficlight_counter", context_type="trafficlight_counter"),
        operand_object = Property.objects.get(function_name="freetext", context_type="trafficlight_counter"),
        freetext_object = 5,
        operator = BoolOperator.objects.get(jsonlogic_operator="<", context_type="trafficlight_counter"),
        jsonlogic_condition = {},
    )
    cond.save()
    rap = RuleActionPair(
        jsonlogic_if_statement = {},
        rule = inc_counter_rule,
        action = Action.objects.get(function_name='increment_counter')
    )
    rap.set_jsonlogic_if_statement()
    rap.save()