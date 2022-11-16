'''
Setup: One context_type per variable available to the rules. 
Property and Operator and Action dictionaries will be laid out like so:

context_types = ["context_type1", "context_type2", ... , "context_typeN"]

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

TODO:
Create function/script to create new Property/BoolOperator objects and tie a command into the available Django manage.py commands.
Build the GUI
'''

from json_logic import jsonLogic

from .models import Property, Action, BoolOperator, Rule, RuleActionPair

class RuleManager():

    def __init__(self, property_function_dict, action_function_dict, boolOperator_string_dict, context_types):
        self.property_function_dict = property_function_dict
        self.action_function_dict = action_function_dict
        self.boolOperator_string_dict = boolOperator_string_dict
        self.context_types = context_types
        self.function_translations = {}

        self._validate_input_dictionaries()
        self._create_function_translations()
        self._create_properties()
        self._create_actions()
        self._create_boolOperators()

    def _validate_input_dictionaries(self):
        self._validate_dictionary(self.property_function_dict, callable)
        self._validate_dictionary(self.action_function_dict, callable)
        self._validate_dictionary(self.boolOperator_string_dict, _isstr)

    
    def _validate_dictionary(self, input_dict, input_type_check_func):
        for context_type_key in input_dict:
            if context_type_key not in self.context_types:
                raise ValueError('invalid context type key in dictionary')
            value_list = input_dict[context_type_key]
            for func_or_op in value_list:
                if not input_type_check_func(func_or_op):
                    raise ValueError('invalid function or operator in dictionary')

    def _create_function_translations(self):
        self._create_function_translation_dictionary(self.property_function_dict)
        self._create_function_translation_dictionary(self.action_function_dict)

    def _create_function_translation_dictionary(self, input_dict):
        for key in input_dict:
            function_list = input_dict[key]
            for function in function_list:
                self.function_translations[function.__name__] = function

    def _create_properties(self):
        self._create_models(self.property_function_dict, Property)

    def _create_actions(self):
        self._create_models(self.action_function_dict, Action)
    
    def _create_boolOperators(self):
        self._create_models(self.boolOperator_string_dict, BoolOperator)
    
    def _create_models(self, input_dict, modelClass):
        for context_type_key in input_dict:
            function_or_op_list = input_dict[context_type_key]
            for function_or_op in function_or_op_list:
                function_or_op_name = _get_string_name(function_or_op)
                _create_model(modelClass, context_type_key, function_or_op_name)

    def eval_first_true_rule(self, *rule_names, **context_type_vars):
        results_dict = {}
        for rule_name in rule_names:
            if self.eval_rule(results_dict, rule_name, **context_type_vars):
                return results_dict
        return results_dict

    def eval_all_rules(self, *rule_names, **context_type_vars):
        results_dict = {}
        for rule_name in rule_names:
            self.eval_rule(results_dict, rule_name, **context_type_vars)
        return results_dict

    def eval_rule(self, results_dict, rule_name, **context_type_vars):
        rule = Rule.objects.get(name=rule_name)
        rule_action_pair = RuleActionPair.objects.get(rule=rule)
        jsonlogic_if_statement = self._replace_func_names_with_func_results_recur(rule_action_pair.jsonlogic_if_statement, **context_type_vars)
        result_action_str = jsonLogic(jsonlogic_if_statement)
        if result_action_str == 'do_nothing':
            return False
            
        action_model = Action.objects.get(function_name = result_action_str)
        context_type_str = action_model.context_type
        context_var = context_type_vars[context_type_str]
        action_function = self.function_translations[result_action_str]
        result = action_function(context_var)
        results_dict[context_type_str] = result
        return True

    def _replace_func_names_with_func_results_recur(self, jsonlogic, **context_type_vars):
        if type(jsonlogic) == dict:
            # There should only be 1 key per logic string dictionary (one of 'and', 'or', '!').
            key = list(jsonlogic.keys())[0]
            value = list(jsonlogic.values())[0]

            # replace/iterate
            jsonlogic = { key : self._replace_func_names_with_func_results_recur(value) }
        
        elif type(jsonlogic) == list:
            for index, entry in jsonlogic:
                if type(entry) == str:
                    property_model = Property.objects.get(function_name=entry)
                    context_type_str = property_model.context_type
                    context_var = context_type_vars[context_type_str]
                    prop_function = self.function_translations[entry]
                    property_result = prop_function(context_var)
                    jsonlogic[index] = property_result
                else: #dict
                    jsonlogic[index] = self._replace_func_names_with_func_results_recur(entry)
        
        return jsonlogic

def _isstr(input_obj):
        return type(input_obj) == str

def _get_string_name(function_or_string):
    if type(function_or_string) == str:
        return function_or_string
    return function_or_string.__name__

def _create_model(modelClass, context_type_key, function_or_op_name):
    if modelClass == Property:
        try:
            model = Property.objects.get(function_name = function_or_op_name, context_type=context_type_key)
            return model
        except Property.DoesNotExist:
            model = Property(
                function_name = function_or_op_name,
                is_free_text = False,
                context_type = context_type_key,
            )
    elif modelClass == Action:
        try:
            model = Action.objects.get(function_name = function_or_op_name, context_type=context_type_key)
            return model
        except Action.DoesNotExist:
            model = Action(
                function_name = function_or_op_name,
                context_type = context_type_key,
            )
    elif modelClass == BoolOperator:
        try:
            model = BoolOperator.objects.get(jsonlogic_operator = function_or_op_name, context_type=context_type_key)
            return model
        except BoolOperator.DoesNotExist:
            model = BoolOperator(
                jsonlogic_operator = function_or_op_name,
                context_type = context_type_key,
            )
    model.save()
    return model