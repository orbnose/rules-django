from ..rule_manager import RuleManager

class Trafficlight():
    def __init__(self):
        self.color = 'green'
        self.counter = 0

def get_trafficlight_color(color: str):
    return color

def get_trafficlight_counter(tl: Trafficlight):
    return tl.counter

def set_color_to_green(tl: Trafficlight):
    tl.color = 'green'
    return tl

def set_color_to_yellow(tl: Trafficlight):
    tl.color = 'yellow'
    return tl

def set_color_to_red(tl: Trafficlight):
    tl.color = 'red'
    return tl

def increment_counter(tl: Trafficlight):
    tl.counter = tl.counter + 1
    return tl

def reset_counter(tl: Trafficlight):
    tl.counter = 0
    return tl


_tl_property_functions = {
    "trafficlight_color": [get_trafficlight_color],
    "trafficlight_counter" : [get_trafficlight_counter]
}
_tl_boolops = {
    "trafficlight_color" : ["=="],
    "trafficlight_counter" : ["==", ">"]
}
_tl_action_functions = {
    "trafficlight": [set_color_to_green, set_color_to_yellow, set_color_to_red, increment_counter, reset_counter]
}
_tl_context_types = ["trafficlight_color", "trafficlight_counter", "trafficlight"]

TrafficLightRuleManager = RuleManager(
    property_function_dict=_tl_property_functions,
    action_function_dict=_tl_action_functions,
    boolOperator_string_dict=_tl_boolops,
    context_types = _tl_context_types
)