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
        condition.set_jsonlogic_condition_and_save()
        self.assertEqual(
            condition.jsonlogic_condition,
            { ">" : [{"var" : "number_of_spoons"}, {"var" : "number_of_forks"}] }
        )
    
    def test_freetext_condition_json(self):
        condition = Condition.objects.get(pk=2)
        condition.set_jsonlogic_condition_and_save()
        self.assertEqual(
            condition.jsonlogic_condition,
            {"==" : [{"var": "spoon_type"}, "Big"] }
        )

class TestRule(TestCase):
    def setUp(self):
        set_up_properties_and_ops()
        set_up_rule_with_2_conditions("test_rule_1", "1 AND 2")
        set_up_rule_with_2_conditions("test_rule_2", "NOT (2 OR (1 AND NOT 2))")
        set_up_rule_with_2_conditions("test_rule_3", "1")

    def test_jsonlogic_full_conditions_rule1(self):
        rule = Rule.objects.get(name="test_rule_1")
        rule.set_jsonlogic_conditions()
        self.assertEqual(
            rule.jsonlogic_full_conditions,
            { "and" : [
                { "==" : [
                    {"var" : "spoon_type"},
                    "Big"
                ]},
                { ">" : [
                    {"var" : "number_of_spoons"},
                    {"var" : "number_of_forks"}
                ]}
            ]},
        )
    
    def test_jsonlogic_full_conditions_rule2(self):
        rule = Rule.objects.get(name="test_rule_2")
        rule.set_jsonlogic_conditions()
        self.assertEqual(
            rule.jsonlogic_full_conditions,
            { "!" : [
                { "or" : [
                    { "and" : [
                        { "!" : [
                            { "==" : [
                                {"var" : "spoon_type"},
                                "Big"
                            ]}
                        ]},
                        { ">" : [
                            {"var" : "number_of_spoons"},
                            {"var" : "number_of_forks"}
                        ]}
                    ]},
                    { "==" : [
                        {"var" : "spoon_type"},
                        "Big"
                    ]}
                ]}
            ]}
        )

    def test_jsonlogic_full_conditions_rule3(self):
        rule = Rule.objects.get(name="test_rule_3")
        rule.set_jsonlogic_conditions()
        self.assertEqual(
            rule.jsonlogic_full_conditions,
            { ">" : [
                {"var" : "number_of_spoons"},
                {"var" : "number_of_forks"}
            ]}
        )

def set_up_floating_conditions():
    set_up_number_condition(rule_index=1, rule=get_shell_rule_with_shell_action_pair() )
    set_up_freetext_condition(rule_index=1, rule=get_shell_rule_with_shell_action_pair() )

def get_shell_rule_with_shell_action_pair():
    rap = RuleActionPair(
        jsonlogic_if_statement = {},
    )
    rap.save()
    shell_rule = Rule(
        name = "shell",
        logic_string = "",
        jsonlogic_only_boolean_symbols = {},
        jsonlogic_full_conditions = {},
        num_conditions = 1,
        rule_action_pair = rap,
    )
    shell_rule.save()
    return shell_rule

def set_up_rule_with_2_conditions(name, rule_logic_string):
    rule = get_2_condition_rule_with_shell_action_pair(name, rule_logic_string)
    _ = set_up_number_condition(rule_index=1, rule=rule)
    _ = set_up_freetext_condition(rule_index=2, rule=rule)

def get_2_condition_rule_with_shell_action_pair(name, rule_logic_string: str):
    rap = RuleActionPair(
        jsonlogic_if_statement = {},
    )
    rap.save()
    rule = Rule(
        name = name,
        logic_string = rule_logic_string,
        jsonlogic_only_boolean_symbols = {},
        jsonlogic_full_conditions = {},
        num_conditions = 2,
        rule_action_pair = rap,
    )
    rule.save()
    return rule

def set_up_number_condition(rule_index: int, rule: Rule):
    cond = Condition( # pk = 1
            operand_subject = Property.objects.get(function_name = "number_of_spoons"),
            operand_object = Property.objects.get(function_name = "number_of_forks"),
            operator = BoolOperator.objects.get(jsonlogic_operator = ">"),
            jsonlogic_condition = {},
            rule_index = rule_index,
            rule = rule
        )
    cond.save()
    return cond

def set_up_freetext_condition(rule_index, rule: Rule):
    cond = Condition( # pk = 2
            operand_subject = Property.objects.get(function_name = "spoon_type"),
            operand_object = Property.objects.get(function_name = "spoon free text"),
            freetext_object = "Big",
            operator = BoolOperator.objects.get(jsonlogic_operator = "=="),
            jsonlogic_condition = {},
            rule_index = rule_index,
            rule = rule
        )
    cond.save()
    return cond

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

