from django.test import TestCase

from ..models import RuleActionPair, Action, Rule, Condition, Property, BoolOperator

class TestCondition(TestCase):
    def setUp(self):
        set_up_properties_and_ops()
        set_up_floating_conditions()

    def test_number_condition_get_subject_json(self):
        self.assertEqual(
            Condition.objects.get(pk=1).get_subject_json(),
            {"var": "number_of_spoons"},
        )
    
    def test_freetext_condition_get_object_json(self):
        self.assertEqual(
            Condition.objects.get(pk=2).get_object_json(),
            "Big",
        )

    def test_number_condition_json(self):
        condition = Condition.objects.get(pk=1)
        condition.set_jsonlogic_condition()
        self.assertEqual(
            condition.jsonlogic_condition,
            { ">" : [{"var" : "number_of_spoons"}, {"var" : "number_of_forks"}] }
        )
    
    def test_freetext_condition_json(self):
        condition = Condition.objects.get(pk=2)
        condition.set_jsonlogic_condition()
        self.assertEqual(
            condition.jsonlogic_condition,
            {"==" : [{"var": "spoon_type"}, "Big"] }
        )

def set_up_floating_conditions():
    set_up_conditions( get_shell_rule_with_shell_action_pair(), get_shell_rule_with_shell_action_pair() )

def set_up_conditions(number_rule: Rule, freetext_rule: Rule):
#dependent on set_up_properties_and_ops()

    _ = Condition( # pk = 1
            operand_subject = Property.objects.get(function_name = "number_of_spoons"),
            operand_object = Property.objects.get(function_name = "number_of_forks"),
            operator = BoolOperator.objects.get(jsonlogic_operator = ">"),
            jsonlogic_condition = {},
            rule_index = 1,
            rule = number_rule
        )
    _.save()
    _ = Condition( # pk = 2
            operand_subject = Property.objects.get(function_name = "spoon_type"),
            operand_object = Property.objects.get(function_name = "spoon free text"),
            freetext_object = "Big",
            operator = BoolOperator.objects.get(jsonlogic_operator = "=="),
            jsonlogic_condition = {},
            rule_index = 1,
            rule = freetext_rule
        )
    _.save()

def get_shell_rule_with_shell_action_pair():
    rap = RuleActionPair(
        jsonlogic_if_statement = {},
    )
    rap.save()
    _ = Rule( # pk = 1
        name = "shell",
        logic_string = "",
        jsonlogic_only_boolean_symbols = {},
        jsonlogic_full_conditions = {},
        num_conditions = 1,
        rule_action_pair = rap,
    )
    _.save()
    return _

def set_up_properties_and_ops():
    _ = Property(
            function_name = "number_of_spoons",
            is_free_text = False,
            context_type = "number",
        )
    _.save()
    _ = Property(
            function_name = "number_of_forks",
            is_free_text = False,
            context_type = "number",
        )
    _.save()
    _ = Property(
            function_name = "spoon_type",
            is_free_text = False,
            context_type = "spoon_string"
        )
    _.save()
    _ = Property(
            function_name = "spoon free text",
            is_free_text = True,
            context_type = "spoon_string"
        )
    _.save()
    _ = BoolOperator(
            jsonlogic_operator = '>',
            context_type = "number",
        )
    _.save()
    _ = BoolOperator(
            jsonlogic_operator = '==',
            context_type = "number"
        )
    _.save()

