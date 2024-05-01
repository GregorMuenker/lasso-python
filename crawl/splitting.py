import builtins
from _ast import *
import ast
from os import listdir
from os.path import isfile, join, isdir

# TODO: Handle imported Classes

def get_function_calls(element):
    function_calls = []
    for node in ast.walk(element):
        if type(node) == Call:
            trace_node = node.func
            if type(trace_node) == Attribute:
                function_trace = trace_node.attr
                while True:
                    try:
                        trace_node = trace_node.value
                        function_trace = "{}.".format(trace_node.attr) + function_trace
                    except:
                        function_trace = "{}.".format(trace_node.id) + function_trace
                        break
                function_calls.append(function_trace)
            elif trace_node.id not in dir(builtins):
                function_calls.append(trace_node.id)
    return function_calls

def get_function_args(element):
    args = []
    for arg in element.args.args:
        args.append({
            "name": arg.arg,
            "datatype": arg.annotation
        })
    return args

def get_functions_from_ast(tree, source, prefix, sub_module_name, depended_class=None):
    index = []
    for element in tree.body:
        if type(element) == FunctionDef:
            source_code = ast.get_source_segment(source, element)
            index_element = {
                "module": prefix + sub_module_name,
                "type": "function",
                "name": element.name,
                "dependend_class": depended_class,
                "function_calls": get_function_calls(element),
                "arguments": get_function_args(element),
                "source_code": source_code,
                "ast": element,
            }
            index.append(index_element)
        elif type(element) == ClassDef:
            index += get_functions_from_ast(element, source, prefix, sub_module_name, depended_class=element.name)
    return index


def get_module_index(module_name, path):
    index = []
    prefix = module_name + "."
    for element in sorted(listdir(path)):
        if isfile(join(path, element)):
            sub_module_name = element.split(".py")[0]
            source = open(join(path, element), "r").read()
            tree = ast.parse(source)
            index += get_functions_from_ast(tree, source, prefix, sub_module_name)
        elif isdir(join(path, element)):
            index += get_module_index(prefix + element, join(path, element))
    return index


index = get_module_index("calculator", "./packages/calculator-0.0.1/calculator")
