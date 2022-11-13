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

TODO:
Create function/script to create new Property/BoolOperator objects and tie a command into the available Django manage.py commands.
Build the GUI
'''
