import builtins
import copy
import importlib
import inspect
import pickle
import pkgutil
from _ast import *
import ast
from os import listdir
from os.path import isfile, join, isdir
import json

from crawl import run
from crawl.install import install


# TODO: Handle imported Classes
# TODO: Check if function calls are further needed


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
            elif hasattr(trace_node, 'id') and trace_node.id not in dir(builtins):
                function_calls.append(trace_node.id)
    return function_calls

def get_arg_datatype(datatype):
    if type(datatype) is Name:
        datatype = [datatype.id]
    elif type(datatype) is Attribute:
        datatype = ["{}.{}".format(datatype.attr, datatype.value.id)]
    elif type(datatype) is BinOp:
        datatype = get_arg_datatype(datatype.left) + get_arg_datatype(datatype.right)
    elif type(datatype) is Constant and datatype.value is None:
        datatype = [None]
    elif datatype is not None and type(datatype) is not str:
        print(datatype)
        datatype = [None]
    return datatype

def get_arg_datatype_code(arg, source):
    if arg.annotation is not None:
        arg_source = ast.get_source_segment(source, arg)
        datatype = arg_source.split(": ")[1]
    else:
        datatype = None
    return datatype

def get_function_args(element, source):
    args = []
    for arg in element.args.args:
        datatype = get_arg_datatype_code(arg, source)
        args.append({
            "name": arg.arg,
            "datatype": datatype,
            "keyword-arg": False
        })
    for arg in element.args.kwonlyargs:
        datatype = get_arg_datatype_code(arg, source)
        args.append({
            "name": arg.arg,
            "datatype": datatype,
            "keyword-arg": False
        })
    return args

def get_functions_from_ast(tree, source, prefix, sub_module_name, depended_class=None):
    index = []
    for element in tree.body:
        if type(element) == FunctionDef:
            # source_code = ast.get_source_segment(source, element)
            index_element = {
                "module": prefix + sub_module_name,
                "name": element.name,
                "dependend_class": depended_class,
                # "function_calls": get_function_calls(element),
                "arguments": get_function_args(element, source),
                # "source_code": source_code,
            }
            index.append(index_element)
        elif type(element) == ClassDef:
            index += get_functions_from_ast(element, source, prefix, sub_module_name, depended_class=element.name)
    return index


def get_module_index(module_name, path=None):
    if "array_api" in module_name:
        return []
    elif "test" in module_name:
        return []
    index = []
    if path is None:
        # try:
        module = importlib.import_module(module_name)
        # except ImportError as e:
        #     if type(e) == ModuleNotFoundError:
        #         missing_pkg = [e.name]
        #     else:
        #         missing_pkg = [x.split(":")[0] for x in e.args[0].split("\n")[1:]]
        #     print(missing_pkg)
        #     for pkg in missing_pkg:
        #         install(pkg)
        #         run.move(pkg)
        #     module = importlib.import_module(module_name)
        prefix = module_name + "."
        for importer, sub_module_name, ispkg in pkgutil.iter_modules(module.__path__):
            if not ispkg and sub_module_name[0] != "_" and "test" not in sub_module_name:
            #if not ispkg and sub_module_name[0] != "_":
                try:
                    sub_module = importlib.import_module(prefix + sub_module_name)
                    source = inspect.getsource(sub_module)
                    tree = ast.parse(source)
                    index += get_functions_from_ast(tree, source, prefix, sub_module_name)
                except ModuleNotFoundError as e:
                    print(sub_module_name, e)
                    pass
                except OSError as e:
                    print(sub_module_name, e)
                    pass
            elif ispkg:
                try:
                    importlib.import_module(prefix + sub_module_name)
                    index += get_module_index(prefix + sub_module_name)
                except ModuleNotFoundError as e:
                    print(sub_module_name, e)
                    pass
                except OSError as e:
                    print(sub_module_name, e)
                    pass

        return index
    else:
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

# index = get_module_index("calculator", "test_packages/calculator-0.0.1/calculator")
if __name__ == "__main__":
    package_name = "urllib3"
    try:
        folders = run.move(package_name)
    except FileNotFoundError:
        install(package_name)
        folders = run.move(package_name)
    index = get_module_index(package_name)
    run.remove(folders)

#fp = open('search_index.json', 'w')
#json.dump(index, fp)
