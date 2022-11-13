import regex as re

def tokenize(logic_string:str ):
    return re.findall(r"(AND|OR|NOT|\d+|\(|\))", logic_string)

def is_value(token: str):
    return re.search(r"^\d+$", token)

def is_operator(string: str):
    if string == "AND" or string == "OR" or string == "NOT":
        return True
    return False

def get_operand_target(operator: str):
    targets = {
        "AND": 2,
        "OR": 2,
        "NOT": 1,
    }
    return targets[operator]

def peek(stack):
    return stack[-1] if stack else None

def get_shunting_yard_stack(logic_string:str):
    tokens = tokenize(logic_string)
    values = []
    operators = []
    for token in tokens:
        if is_value(token):
            values.append(token)
        elif token == "(":
            operators.append(token)
        elif token == ")":
            top = peek(operators)
            while top is not None and top != "(":
                values.append(operators.pop())
                top = peek(operators)
            if top is None:
                raise ValueError("imbalanced parentheses")
            operators.pop() # Discard '('
        else:
            # Operator
           
            if token == "NOT":  #  NOT takes precedence over AND and OR
                operators.append(token)
            else: # juggle AND and OR
                top = peek(operators)
                while top is not None and top != "(":
                    values.append(operators.pop())
                    top = peek(operators)
                operators.append(token)
    while peek(operators) is not None and peek(operators) != "(":
        values.append(operators.pop())
    if peek(operators) == "(":
        raise ValueError("imbalanced parentheses")

    return values

def pop_stack_iter(stack, logic_list, operand_target, operand_counter):

    if peek(stack) is not None:
        if operand_counter < operand_target:
            element = stack.pop()
            if is_operator(element):
                logic_list.append({element: []})
                # fill up slots for new operator
                logic_list[-1][element] = pop_stack_iter(stack, logic_list[-1][element], get_operand_target(element), 0)
            else:
                element = str('@' + element) #Denote substitution slot
                logic_list.append(element)
            
            logic_list = pop_stack_iter(stack, logic_list, operand_target, operand_counter+1)

    return logic_list

def get_jsonlogic(logic_string:str):

    if is_only_one_condition_in_logic_string(logic_string):
        return get_single_condition_placeholder_string()
    
    logic_list = []
    stack = get_shunting_yard_stack(logic_string)
    if peek(stack) is not None:
        # assume the first element will be an operator
        operator = stack.pop()
        logic_list.append({operator: []})
        logic_list[-1][operator] = pop_stack_iter(stack, logic_list[-1][operator], get_operand_target(operator), 0)
    if logic_list:
        return logic_list[0]

    return {} # Fallback empty value

def is_only_one_condition_in_logic_string(logic_string):
    return logic_string == "1"

def get_single_condition_placeholder_string():
    return "@1"

def jsonlogic_has_single_condition(jsonlogic):
    return jsonlogic == "@1"

# --- --- --- --- Regular expression functions for checking validity of the logic string before jsonlogic processing begins --- --- --- ---

def has_valid_tokens(logic_string: str):

    # valid tokens are 'AND', 'OR', 'NOT', '(', ')', [any group of one or more digits], [any group of zero or more spaces] 
    if re.fullmatch(r"^(AND|OR|NOT|\d+|\(|\)| *)+$", logic_string):
        return True
    
    return False

def has_valid_left_parens(logic_string: str):
# Taken from https://stackoverflow.com/questions/10964977/regular-expression-for-valid-boolean-expression/10964989#10964989
    
    # using pypi regex for variable look-behind.
    
    # Take out whitespace so I don't have to parse them after the regex look-behind.
    #  I was having trouble getting r"(?<!AND|OR|NOT|\(|^) *\(" for variable spaces between 'AND' and '(' for example. 
    logic_string = re.sub(r"\s", '', logic_string)
    
    # open parenthesis '(' must be followed by something other than 'AND' or 'OR' or ')' ; and it must follow 'AND' or 'OR' or 'NOT' or '(' (except at the beginning of the string)
    if re.search(r"\((AND|OR|\))", logic_string) or re.search(r"(?<!AND|OR|NOT|\(|^)\(", logic_string):
        return False
    
    return True

def has_valid_right_parens(logic_string: str):
# Taken from https://stackoverflow.com/questions/10964977/regular-expression-for-valid-boolean-expression/10964989#10964989

    # Remove whitespace
    logic_string = re.sub(r"\s", '', logic_string)

    # closing parenthesis ')' must be followed by 'AND' or 'OR' or ')' or string-end character '$' ; and it must follow something other than 'OR','AND', 'NOT' 
    if re.search(r"\)(?!(OR|AND|\)|$))", logic_string) or re.search(r"(AND|OR|NOT)\)", logic_string):
        return False
    
    return True

def has_balanced_parens(logic_string: str):
    depth = 0
    for character in logic_string:
        if character == '(':
            depth = depth + 1
        elif character == ')':
            depth = depth - 1
    
    if depth != 0:
        return False
    return True

def has_valid_and_or(logic_string: str):
    
    # Remove whitespace
    logic_string = re.sub(r"\s", '', logic_string)

    # 'AND' and 'OR' must preceed and follow something other than 'AND' or 'OR'.
    if re.search(r"(OR|AND)(OR|AND)", logic_string):
        return False
    return True

def has_valid_not(logic_string: str):

    # Remove whitespace
    logic_string = re.sub(r"\s", '', logic_string)

    # 'NOT' must come after 'AND' or 'OR' or '(' or the start of the string (^). 'NOT' must preceed a number or '('.
    if re.search(r"(?<!AND|OR|\(|^)NOT", logic_string) or re.search(r"NOT(?!\d+|\()", logic_string):
        return False
    return True

def has_valid_number_args(logic_string: str, num_args: int):

    # number groups cannot follow another number group
    if re.search(r"(\d+) +(\d+)", logic_string):
        return False
    
    # check that the number arguments match the number of conditions supplied
    args_list = re.findall(r"\d+",logic_string)
    int_args_list = set([int(arg) for arg in args_list]) #cast to int and remove duplicate values
    for arg in int_args_list:
        if arg < 1 or arg > num_args:
            return False

    # check for missing arg
    if sorted(int_args_list) != list(range(1,num_args+1)):
        return False

    return True

def is_valid_logic_string(logic_string: str, num_args: int):
    
    if not has_valid_tokens(logic_string):
        return False
    if not has_valid_left_parens(logic_string):
        return False
    if not has_valid_right_parens(logic_string):
        return False
    if not has_valid_and_or(logic_string):
        return False
    if not has_valid_not(logic_string):
        return False
    if not has_valid_number_args(logic_string, num_args):
        return False
    if not has_balanced_parens(logic_string):
        return False
    
    return True

def main():
    logic_string = "((1 AND NOT 2) OR (3 AND (4 OR 5)))"
    print(get_shunting_yard_stack(logic_string))
    logic_list = get_jsonlogic(logic_string)
    print(logic_list)
if __name__=="__main__":
    main()