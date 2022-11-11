import copy, re

from django.db import models

'''
Setup: One context_type per variable available to the rules. 
Property and Operator dictionaries will be laid out like so:

property_dict = {
    "context_type1" : [func11, func12, ..., func1M],
    "context_type2" : [func21, func22, ..., func2K],
    ...
}
boolOperator_dict = {
    "context_type1" : [jsonlogic_op11, jsonlogic_op21, ..., jsonlogic_op1N],
    "context_type2" : [jsonlogic_op21, jsonlogic_op22, ..., jsonlogc_op2L],
    ...
}

Properties and operators will be created by running through theses dictionaries and creating new objects for any 
entries in the list not yet represented by an object.

Each time a rule is to be evaluated, the context dictionary will be laid out like so:
context_dict = {
    "context_type1" : context_var1,
    "context_type2" : context_var2,
    ...
}
'''

'''
TODO:
Create function/script to create new Property/BoolOperator objects and tie a command into the available Django manage.py commands.
Write function to convert symbolic jsonlogic string into one with complete conditions
Build the GUI
'''

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



class Rule(models.Model):

    name = models.CharField(max_length = 200)
    logic_string = models.CharField(max_length = 200)
    jsonlogic_symbols = models.JSONField(blank=True)
    jsonlogic_conditions = models.JSONField(blank=True)
    num_conditions = models.PositiveIntegerField()

    def replace_jsonlogic_symbols_iter(self, jsonlogic):

        if type(jsonlogic) == dict:
            # There should only be 1 key per logic string dictionary (one of 'AND', 'OR', 'NOT').
            key = jsonlogic.keys()[0]
            value = jsonlogic.values()[0]

            # Convert 'AND' 'OR' 'NOT'
            if key == 'NOT':
                key = '!'
            else:
                key = key.lower()
            
            # Iterate
            jsonlogic = {}
            jsonlogic[key] = self.replace_jsonlogic_symbols_iter(value)

        elif type(jsonlogic) == dict:
            for index, symbol in enumerate(jsonlogic):
                condition_number_match = re.search(r"^@(\d)+$", symbol)
                if not condition_number_match:
                    raise ValueError(symbol,' in ',jsonlogic,': improper condition argument')
                num = condition_number_match(0)
                jsonlogic[index] = self.condition_set.get(rule_index=num).jsonlogic_condition

        return jsonlogic

    def set_jsonlogic_conditions(self):

        for condition in self.condition_set:
            condition.set_jsonlogic_condition()
        
        self.jsonlogic_conditions = self.replace_jsonlogic_symbols_iter( copy.deepcopy(self.jsonlogic_symbols) )
        self.save()

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

    def get_subject(self):
        if self.freetext_subject:
            return self.freetext_subject
        return self.operand_subject.function_name
    
    def get_object(self):
        if self.freetext_object:
            return self.freetext_object
        return self.operand_object.function_name

    def set_jsonlogic_condition(self):
        if not self.operand_object or not self.operand_object or not self.operator:
            return ValueError('missing condition components')

        self.jsonlogic_condition = (
            { self.operator.jsonlogic_operator : [ { "var": self.get_subject}, { "var": self.get_object } ]}
        )
        self.save()
