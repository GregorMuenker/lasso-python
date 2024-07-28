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
    """ (deprecated) Returns a list of function calls from the target function to load the function at runtime.

    :param element: FunctionDef element of target function in abstract syntax tree
    :return: list of function calls. Function calls are encoded as string elements.
    """
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
    """ (deprecated) Returns the pythonic datatype

    :param datatype: annotation element in abstract syntax tree of target argument
    :return: datatype
    """
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
    """Return the string of the datatype annotate to target argument.

    :param arg: argument element in abstract syntax tree
    :param source: source code of whole abstract syntax tree
    :return: string of annotated datatype
    """
    if arg.annotation is not None:
        arg_source = ast.get_source_segment(source, arg)
        datatype = arg_source.split(": ")[1]
    else:
        datatype = "Any"
    return datatype


def get_function_args(element, source, class_function):
    """Returns a list of all arguments and their characteristics of one target function.

    :param element: FunctionDef in abstract syntax tree
    :param source: source code of whole abstract syntax tree
    :return: list of all arguments and their characteristics
    """
    args = []
    element_args = element.args
    if class_function:
        element_args.args = element_args.args[1:]

    def append_arg(arg, keyword_arg):
        """Inherit function to append argument characteristics to argument_list

        :param arg: argument element in abstract syntax tree
        :param keyword_arg: flag whether the argument is keyword-only
        """
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
        function_source = ast.get_source_segment(source, element)
        args[default_index + i]["default_val"] = ast.get_source_segment(source, default_val)
        args[default_index + i]["has_default_val"] = True
    for arg in element_args.kwonlyargs:
        append_arg(arg, True)
    for i, default_val in enumerate(element_args.kw_defaults):
        if default_val:
            args[len(element_args.args) + i]["default_val"] = ast.get_source_segment(source, default_val)
            args[len(element_args.args) + i]["has_default_val"] = True
    return args, default_index


def get_return_type(element, source):
    """Returns the return type of a function by using the source code

    :param element: FunctionDef in abstract syntax tree
    :param source: source code of whole abstract syntax tree
    :return: string of datatype
    """
    return_type = ast.get_source_segment(source, element.returns)
    if return_type:
        return return_type
    else:
        return "Any"


def get_functions_from_ast(tree, source, prefix, sub_module_name, depended_class="None"):
    """Generates function characteristics based on an abstract syntax tree.

    :param tree: abstract syntax tree of the target module
    :param source: source code of the target module
    :param prefix: import path prefix of the target module
    :param sub_module_name: name of the target module
    :param depended_class: default = "None". When a function is identified to be part of a class this parameters has to
    be set for later querying.
    :return: list of all functions in the target module with their characteristics
    """
    index = []
    for element in tree.body:
        if type(element) == FunctionDef:
            # source_code = ast.get_source_segment(source, element)
            if depended_class != "None" and "staticmethod" in [ast.get_source_segment(source, x) for x in
                                                               element.decorator_list]:
                depended_class = "None"
            args, default_index = get_function_args(element, source, depended_class != "None")
            index_element = {
                "module": prefix + sub_module_name,
                "name": element.name,
                "dependend_class": depended_class,
                # "function_calls": get_function_calls(element),
                "arguments": args,
                "return_types": get_return_type(element, source),
                "default_index": default_index,
                "count_positional_args": len([x for x in args if not x["keyword_arg"]]),
                "count_positional_non_default_args": len(
                    [x for x in args if not x["has_default_val"] and not x["keyword_arg"]]),
                "count_kw_args": len([x for x in args if x["keyword_arg"]])
                # "source_code": source_code,
            }
            index_element["id"] = hashlib.md5(json.dumps(index_element).encode("utf-8")).hexdigest()
            index.append(index_element)
        elif type(element) == ClassDef:
            index += get_functions_from_ast(element, source, prefix, sub_module_name, depended_class=element.name)
    return index


#
def get_module_index(module_name, path=None):
    """Creates an list of all function within the given module. Each element consists of a dictonary of the functions
    characteristics.

    :param module_name: name of importable python module
    :param path: (optional) path to python module. When used, than the splitting is only file based, only for backup.
    :return: list of all functions with their characteristics
    """
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
                # Subject to change
                except ModuleNotFoundError:
                    path = f"./active/{(prefix + sub_module_name).replace('.', '/')}.py"
                    source = open(path, "r").read()
                    tree = ast.parse(source)
                    index += get_functions_from_ast(tree, source, prefix, sub_module_name)
                except OSError:
                    print(prefix + sub_module_name, "CPython Function")
                    pass
                except Exception as e:
                    print(prefix + sub_module_name, e)
                    pass
            elif ispkg:
                try:
                    importlib.import_module(prefix + sub_module_name)
                    index += get_module_index(prefix + sub_module_name)
                # Subject to change
                except ModuleNotFoundError:
                    index += get_module_index(prefix + sub_module_name,
                                              path=f"./active/{(prefix + sub_module_name).replace('.', '/')}")
                except Exception as e:
                    print(sub_module_name, e)
                    pass

        return index
    else:
        prefix = module_name + "."
        for element in sorted(listdir(path)):
            if isfile(join(path, element)) and ".py" in element[-3:] and "__init__" not in element:
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
        run.move_active(package_name)
    except FileNotFoundError:
        install(package_name)
        run.move_active(package_name)
    index = get_module_index(package_name)
    run.remove_active()

#fp = open('search_index.json', 'w')
#json.dump(index, fp)
