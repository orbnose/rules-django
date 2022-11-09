from django.db import models

'''
Setup: One context_type per variable available to the rules. 
Dictionaries will be laid out like so:

property_dict = {
    "context_type" : [func1, func2, ..., funcM]
}
boolOperator_dict = {
    "context_type" : [jsonlogic_op1, jsonlogic_op2, ..., jsonlogic_opN]
}

Properties and operators will be created by running through the dictionaries and creating new objects for any 
entries in the list not yet represented by an object.
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
    jsonlogic_symbols = models.JSONField()
    num_conditions = models.PositiveIntegerField()

class Condition(models.Model):
    rule = models.ForeignKey(to=Rule, on_delete=models.CASCADE)
    operand_subject = models.ForeignKey(to=Property, on_delete=models.CASCADE)
    operand_object = models.ForeignKey(to=Property, on_delete=models.CASCADE)
    operator = models.ForeignKey(to=BoolOperator, on_delete=models.CASCADE)