import builtins
import copy
import hashlib
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
        datatype = "None"
    return datatype


def get_function_args(element, source):
    args = []
    element_args = element.args

    def append_arg(arg, keyword_arg):
        datatype = get_arg_datatype_code(arg, source)
        if datatype:
            datatype = datatype.replace("\n", "")
            datatype = datatype.replace(" ", "")
            datatype = datatype.split("|")
        if type(datatype) != list:
            datatype = [datatype]
        args.append({
            "name": arg.arg,
            "datatype": datatype,
            "keyword_arg": keyword_arg,
            "has_default_val": False,
            "default_val": "NODEFAULT"
        })

    for arg in element_args.args:
        append_arg(arg, False)
    if len(element_args.defaults) > 0:
        default_index = len(element_args.args) - len(element_args.defaults)
    else:
        default_index = None
    for i, default_val in enumerate(element_args.defaults):
        args[default_index + i]["default_val"] = ast.get_source_segment(source, default_val)
        args[default_index + i]["has_default_val"] = True
    for arg in element_args.kwonlyargs:
        append_arg(arg, True)
    for i, default_val in enumerate(element_args.kw_defaults):
        if default_val:
            args[len(element_args.args) + i]["default_val"] = ast.get_source_segment(source, default_val)
            args[len(element_args.args) + i]["has_default_val"] = True
    return args, default_index


def get_functions_from_ast(tree, source, prefix, sub_module_name, depended_class=None):
    index = []
    for element in tree.body:
        if type(element) == FunctionDef:
            # source_code = ast.get_source_segment(source, element)
            args, default_index = get_function_args(element, source)
            index_element = {
                "module": prefix + sub_module_name,
                "name": element.name,
                "dependend_class": depended_class,
                # "function_calls": get_function_calls(element),
                "arguments": args,
                "default_index": default_index
                # "source_code": source_code,
            }
            index_element["id"] = hashlib.md5(json.dumps(index_element).encode("utf-8")).hexdigest()
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
                except Exception as e:
                    print(sub_module_name, e)
                    pass
            elif ispkg:
                try:
                    importlib.import_module(prefix + sub_module_name)
                    index += get_module_index(prefix + sub_module_name)
                except Exception as e:
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
    package_name = "numpy"
    try:
        run.move_active(package_name)
    except FileNotFoundError:
        install(package_name)
        run.move_active(package_name)
    index = get_module_index(package_name)
    run.remove_active()

#fp = open('search_index.json', 'w')
#json.dump(index, fp)
