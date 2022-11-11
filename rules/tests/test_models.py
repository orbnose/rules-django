from django.test import TestCase

from ..models import Rule, Condition, Property, BoolOperator

class TestCondition(TestCase):
    def setUp(self):
        self.num_spoons = Property(
            function_name = "number_of_spoons",
            is_free_text = False,
            context_type = "number",
        )
        self.num_forks = Property(
            function_name = "number_of_forks",
            is_free_text = False,
            context_type = "number",
        )
        self.gt_op = BoolOperator(
            jsonlogic_operator = '>',
            context_type = "number",
        )
        self.simple_rule = Rule(
            name = "Simple Test Rule",
            logic_string = "@1",
            num_conditions = 1,
        )
        self.simple_condition = Condition(
            rule = self.simple_rule,
            rule_index = 1,
            operand_subject = self.num_spoons,
            operand_object = self.num_forks,
            operator = self.gt_op,
        )