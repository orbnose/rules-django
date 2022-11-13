import copy, re

from django.db import models

from .logic import get_jsonlogic, jsonlogic_has_single_condition
'''
Setup: One context_type per variable available to the rules. 
Property and Operator and Action dictionaries will be laid out like so:

property_function_dict = {
    "context_type1" : [propfunc11, propfunc12, ..., propfunc1M],
    "context_type2" : [propfunc21, propfunc22, ..., propfunc2K],
    ...
}
action_function_dict = {
   "context_type1" : [actfunc11, actfunc12, ..., actfunc1M],
   "context_type2" : [actfunc21, actfunc22, ..., actfunc2K],
    ...
}
boolOperator_string_dict = {
    "context_type1" : [jsonlogic_op11, jsonlogic_op21, ..., jsonlogic_op1N],
    "context_type2" : [jsonlogic_op21, jsonlogic_op22, ..., jsonlogc_op2L],
    ...
}

Properties and operators will be created by running through theses dictionaries and creating new objects for any 
entries in the list not yet represented by an object. The property string name can be extracted with funcMK.__name__.
The operator entries should already be strings.

Each time a rule is to be evaluated, the context and function dictionaries must be laid out like so:
context_dict = {
    "context_type1" : context_var1,
    "context_type2" : context_var2,
    ...
}
function_dict = {
    "propfunc11": propfunc11,
    "actfunc11" : actfunc11,
    ...
}
'''

'''
TODO:
Create function/script to create new Property/BoolOperator objects and tie a command into the available Django manage.py commands.
Build the GUI
'''



class Rule(models.Model):

    name = models.CharField(max_length = 200)
    logic_string = models.CharField(max_length = 200)
    jsonlogic_only_boolean_symbols = models.JSONField(blank=True)
    jsonlogic_full_conditions = models.JSONField(blank=True)
    num_conditions = models.PositiveIntegerField()

    def set_jsonlogic_conditions(self):

        self.set_jsonlogic_only_boolean_symbols()

        for condition in self.condition_set.all():
            condition.set_jsonlogic_condition_and_save()
        
        self.jsonlogic_full_conditions = self.replace_jsonlogic_symbols_recur( copy.deepcopy(self.jsonlogic_only_boolean_symbols) )

    def set_jsonlogic_only_boolean_symbols(self):
        self.jsonlogic_only_boolean_symbols = get_jsonlogic(self.logic_string)

    def replace_jsonlogic_symbols_recur(self, jsonlogic):

        if type(jsonlogic) == dict:
            # There should only be 1 key per logic string dictionary (one of 'AND', 'OR', 'NOT').
            key = list(jsonlogic.keys())[0]
            value = list(jsonlogic.values())[0]

            if key == 'NOT':
                key = '!'
            else:
                key = key.lower()
            
            # replace/iterate
            jsonlogic = { key : self.replace_jsonlogic_symbols_recur(value) }

        elif type(jsonlogic) == list:
            for index, symbol in enumerate(jsonlogic):
                if type(symbol) == str:
                    condition_number_match = re.match(r"^@(\d)+$", symbol)
                    if not condition_number_match:
                        raise ValueError(symbol,' in ',jsonlogic,': improper condition argument')
                    # match.group(1) has the first sub-group, in this case the digit extraction
                    num = condition_number_match.group(1)
                    jsonlogic[index] = self.condition_set.get(rule_index=num).jsonlogic_condition
                else: # dict
                    jsonlogic[index] = self.replace_jsonlogic_symbols_recur(symbol)
        
        elif jsonlogic_has_single_condition(jsonlogic):
            jsonlogic = self.condition_set.get(rule_index=1).jsonlogic_condition

        return jsonlogic

class Action(models.Model):
    function_name = models.CharField(max_length = 200)
    context_type = models.CharField(max_length = 200)

class RuleActionPair(models.Model):

    jsonlogic_if_statement = models.JSONField()
    rule = models.ForeignKey(to=Rule, on_delete=models.CASCADE)
    action = models.ForeignKey(to=Action, on_delete=models.CASCADE)

    def set_jsonlogic_if_statement(self):
        self.rule.set_jsonlogic_conditions()
        
        self.jsonlogic_if_statement = { 
            "if" : [
                self.rule.jsonlogic_full_conditions,
                self.action.function_name, 
                self.get_do_nothing_function_name(),
            ]
        }

    def get_do_nothing_function_name(self):
        return "do_nothing"

class Property(models.Model):
    function_name = models.CharField(max_length = 200)
    is_free_text = models.BooleanField(default = False)
    context_type = models.CharField(max_length = 200)

class BoolOperator(models.Model):

    jsonlogic_op_list = [
        ('==', 'equals'),
        ('!=', 'does not equal'),
        ('>',  'greater than'),
        ('>=', 'greater than or equal to'),
        ('<',  'less than'),
        ('<=', 'less than or equal to'),
        ('in', 'in (substring or subset of)')
    ]

    jsonlogic_operator = models.CharField(max_length=2, choices=jsonlogic_op_list)
    context_type = models.CharField(max_length = 200)

class Condition(models.Model):

    # note: the context type of a condition can be checked via condition.operand_subject.context_type

    rule = models.ForeignKey(to=Rule, on_delete=models.CASCADE)
    rule_index = models.PositiveIntegerField() # position within the rule, starting at 1
    operand_subject = models.ForeignKey(to=Property, on_delete=models.CASCADE, related_name="+")
    freetext_subject = models.CharField(max_length=200, blank=True)
    operand_object = models.ForeignKey(to=Property, on_delete=models.CASCADE, related_name="+")
    freetext_object = models.CharField(max_length=200, blank=True)
    operator = models.ForeignKey(to=BoolOperator, on_delete=models.CASCADE)
    jsonlogic_condition = models.JSONField()

    def set_jsonlogic_condition_and_save(self):
        if not self.operand_object or not self.operand_object or not self.operator:
            return ValueError('missing condition components')

        self.jsonlogic_condition = (
            { self.operator.jsonlogic_operator : [self.get_subject_json(), self.get_object_json()] }
        )
        self.save()

    def get_subject_json(self):
        return self.get_freetext_or_property_json(self.freetext_subject, self.operand_subject.function_name)
    
    def get_object_json(self):
        return self.get_freetext_or_property_json(self.freetext_object, self.operand_object.function_name)

    def get_freetext_or_property_json(self, freetext_attr, func_name_attr):
        if freetext_attr:
            return freetext_attr
        return { "var" : func_name_attr}

