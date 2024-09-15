import builtins
import hashlib
import importlib
import inspect
import pkgutil
import time
import uuid
from _ast import *
import ast
from os import listdir
from os.path import isfile, join, isdir
import sys, os

from backend.crawl.install import installHandler
from backend.crawl import type_inference, import_helper
from backend.crawl.nexus import Nexus, Package
from dotenv import load_dotenv

load_dotenv()
if os.getenv("RUNTIME_ENVIRONMENT") == "docker":
    INSTALLED = os.getenv("INSTALLED")
else:
    from backend.constants import INSTALLED


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


def get_arg_datatype_code(argument, source):
    """Return the string of the datatype annotate to target argument.

    :param argument: argument element in abstract syntax tree
    :param source: source code of whole abstract syntax tree
    :return: string of annotated datatype
    """
    if argument.annotation is not None:
        arg_source = ast.get_source_segment(source, argument)
        datatype = arg_source.split(": ")[1]
    else:
        datatype = None
    return datatype


def get_return_type(element, source, prefix, sub_module_name, dependent_class, type_inferencing_active):
    """Returns the return type of a function by using the source code

    :param element: FunctionDef in abstract syntax tree
    :param source: source code of whole abstract syntax tree
    :param prefix: full path of parent modules i.e. numpy.core
    :param sub_module_name: name of module that is analysed
    :param dependent_class: class of which a function is located in
    :param type_inferencing_active: boolean if type inferencing is active and infered types should be used
    :return: string of datatype
    """
    return_type = ast.get_source_segment(source, element.returns)
    if return_type:
        return_type = return_type.replace('"', '')
        return_type = return_type.replace(' ', '')
        return_type = return_type.replace('"', '')
        return_type = return_type.split("|")
        return [f"pt_{x}" for x in return_type]
    else:
        if type_inferencing_active:
            inferred_datatypes_function_dict = type_inference.get_inferred_datatypes_function(prefix + sub_module_name,
                                                                                              element.name,
                                                                                              dependent_class)
            if len(inferred_datatypes_function_dict.keys()) != 0:
                return_type = inferred_datatypes_function_dict["return"]
                if return_type != []:
                    return [f"pt_{x}" for x in return_type]
    return ["pt_Any"]


def get_function_args(element, source, dependent_class, prefix, sub_module_name, type_inferencing_active):
    """Returns a list of all arguments and their characteristics of one target function.

    :param element: FunctionDef in abstract syntax tree
    :param source: source code of whole abstract syntax tree
    :param prefix: full path of parent modules i.e. numpy.core
    :param sub_module_name: name of module that is analysed
    :param dependent_class: class of which a function is located in
    :param type_inferencing_active: boolean if type inferencing is active and infered types should be used
    :return: list of all arguments and their characteristics
    """
    args = []
    element_args = element.args
    if dependent_class is not None and "staticmethod" not in [ast.dump(x) for x in
                                                              element.decorator_list]:
        element_args.args = element_args.args[1:]
    if type_inferencing_active:
        inferred_datatypes_function_dict = type_inference.get_inferred_datatypes_function(prefix + sub_module_name,
                                                                                          element.name, dependent_class)

    def append_arg(arg, keyword_arg):
        """Inherit function to append argument characteristics to argument_list

        :param arg: argument element in abstract syntax tree
        :param keyword_arg: flag whether the argument is keyword-only
        """
        datatype = get_arg_datatype_code(arg, source)
        if datatype:
            datatype = datatype.replace("\n", "")
            datatype = datatype.replace(" ", "")
            datatype = datatype.replace('"', '')
            datatype = datatype.split("|")
            datatype = [f"pt_{x}" for x in datatype]
        else:
            if type_inferencing_active:
                if len(inferred_datatypes_function_dict) == 0:
                    datatype = ["pt_Any"]
                else:
                    datatype = [f"pt_{x}" for x in (inferred_datatypes_function_dict[arg.arg] + ["Any"])]
            else:
                datatype = ["pt_Any"]
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
        #args[default_index + i]["default_val"] = ast.get_source_segment(source, default_val)
        args[default_index + i]["has_default_val"] = True
    for arg in element_args.kwonlyargs:
        append_arg(arg, True)
    for i, default_val in enumerate(element_args.kw_defaults):
        if default_val:
            #args[len(element_args.args) + i]["default_val"] = ast.get_source_segment(source, default_val)
            args[len(element_args.args) + i]["has_default_val"] = True
    return args, default_index


def get_functions_from_ast(tree, source, prefix, sub_module_name, path, depended_class=None,
                           type_inferencing_engine=None):
    """Generates function characteristics based on an abstract syntax tree.


    :param tree: abstract syntax tree of the target module
    :param source: source code of the target module
    :param prefix: import path prefix of the target module
    :param sub_module_name: name of the target module
    :param depended_class: default = "None". When a function is identified to be part of a class this parameters has to
    be set for later querying.
    :param type_inferencing_engine: declares the engine used by the type inferencing toolkit. Supported: HiTyper
    :return: list of all functions in the target module with their characteristics
    """
    type_inferencing_active = False
    if type_inferencing_engine:
        type_inference.infer_datatypes_module(prefix + sub_module_name,
                                              module_path=path, type_inference_engine=type_inferencing_engine)
        type_inferencing_active = True
    index = []
    for element in tree.body:
        if type(element) == FunctionDef:
            # source_code = ast.get_source_segment(source, element)
            args, default_index = get_function_args(element, source, depended_class, prefix, sub_module_name,
                                                    type_inferencing_active)
            method_signature_params_ordered = [f"{x['name']}_({','.join(x['datatype'])})" for x in args]
            method_signature_params_ordered_nodefault = [f"{x['name']}_({','.join(x['datatype'])})" for x in args if
                                                         not x["has_default_val"]]
            method_signature_params_ordered_kwargs = [f"{x['name']}" for x in args if x["keyword_arg"]]
            #method_signature_params_ordered_default_values = [f"{x['name']}_{x['default_val']}" for x in args]
            return_types = get_return_type(element, source, prefix, sub_module_name, depended_class,
                                type_inferencing_active)
            method_signature_return_types = ",".join(return_types)
            index_element = {"packagename": prefix + sub_module_name, "method": element.name, "name": depended_class,
                             "methodSignatureParamsOrdered": "|".join(
                                 [str(len(method_signature_params_ordered))] + method_signature_params_ordered),
                             "methodSignatureParamsOrderedNodefault": "|".join(
                                 [str(len(
                                     method_signature_params_ordered_nodefault))] + method_signature_params_ordered_nodefault),
                             "methodSignatureParamsOrderedKwargs": "|".join(method_signature_params_ordered_kwargs),
                             "methodSignatureReturnTypes": method_signature_return_types, "lang": "python",
                             "decorators": [ast.get_source_segment(source, x) for x in element.decorator_list],
                             "id": str(uuid.uuid4())}
            #index_element["id"] = hashlib.md5((str(index_element["packagename"]) + str(index_element["method"]) + str(index_element["name"])).encode("utf-8")).hexdigest()
            index.append(index_element)
        elif type(element) == ClassDef:
            index += get_functions_from_ast(element, source, prefix, sub_module_name, path=path,
                                            depended_class=element.name)
    return index


#
def get_module_index(module_name, package_name, nexus_package_name, version, path=None, type_inferencing_engine=None, skip_missing_dependencies=False):
    """Creates an list of all function within the given module. Each element consists of a dictonary of the functions
    characteristics.

    :param module_name: name of importable python module
    :param path: (optional) path to python module. When used, than the splitting is only file based, only for backup.
    :param type_inferencing_engine: declares the engine used by the type inferencing toolkit. Supported: HiTyper
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
                    module_path = sub_module.__file__
                    source = inspect.getsource(sub_module)
                    tree = ast.parse(source)
                    index += get_functions_from_ast(tree, source, prefix, sub_module_name, module_path,
                                                    type_inferencing_engine=type_inferencing_engine)
                # Subject to change
                except (ModuleNotFoundError, ImportError):
                    if not skip_missing_dependencies:
                        module_path = f"{os.path.join(INSTALLED, f'{nexus_package_name}-{version}')}/{(prefix + sub_module_name).replace('.', '/')}.py"
                        source = open(module_path, "r").read()
                        tree = ast.parse(source)
                        index += get_functions_from_ast(tree, source, prefix, sub_module_name, module_path,
                                                        type_inferencing_engine=type_inferencing_engine)
                except OSError as e:
                    if str(e) == "source code not available":
                        print(prefix + sub_module_name, "CPython Function")
                    else:
                        print(prefix + sub_module_name, f"OSError: {str(e)}")
                    pass
                #except Exception as e:
                #   print(prefix + sub_module_name, e)
                #  pass
            elif ispkg:
                try:
                    importlib.import_module(prefix + sub_module_name)
                    index += get_module_index(prefix + sub_module_name, package_name, nexus_package_name, version,
                                              type_inferencing_engine=type_inferencing_engine)
                # Subject to change
                except (ModuleNotFoundError, ImportError):
                    if not skip_missing_dependencies:
                        index += get_module_index(prefix + sub_module_name, package_name, nexus_package_name, version,
                                                  path=f"{os.path.join(INSTALLED, f'{package_name}-{version}')}/{(prefix + sub_module_name).replace('.', '/')}",
                                                  type_inferencing_engine=type_inferencing_engine)
                #except Exception as e:
                #   print(sub_module_name, e)
                #  pass
    else:
        prefix = module_name + "."
        for element in sorted(listdir(path)):
            if isfile(join(path, element)) and ".py" in element[-3:] and "__init__" not in element:
                sub_module_name = element.split(".py")[0]
                source = open(join(path, element), "r").read()
                tree = ast.parse(source)
                index += get_functions_from_ast(tree, source, prefix, sub_module_name, path, type_inferencing_engine)
            elif isdir(join(path, element)):
                index += get_module_index(prefix + element, package_name, version, join(path, element))
    if "." not in package_name:
        index = [{"artifactId": nexus_package_name, "version": version} | entry for entry in index]
    print(f"{module_name} indexed")
    return index


# index = get_module_index("calculator", "test_packages/calculator-0.0.1/calculator")
if __name__ == "__main__":
    package_name = "numpy==1.26.4"
    nexus = Nexus()
    installHandler = installHandler(nexus)
    nexus_package_name, version, already_installed = installHandler.install(package_name)
    if already_installed:
        pkg = Package(package_name, version)
        nexus.download(pkg, runtime=False)
    installHandler.dump_index()
    imp_help = import_helper.ImportHelper()
    imp_help.pre_load_package(nexus_package_name, version)
    dependencies = installHandler.index[f"{package_name}:{version}"]
    for dep_name in dependencies:
        dep_version = dependencies[dep_name]['version']
        imp_help.pre_load_package(dep_name, dep_version)
    package_name = import_helper.get_import_name(package_name, version)
    start = time.time()
    # index = get_module_index(package_name, package_name, version, type_inferencing_engine="HiTyper")
    index = get_module_index(package_name, package_name, nexus_package_name, version)
    type_inference.clear_type_inferences()
    imp_help.unload_package()
    print(f"Splitting {package_name} needed {round(time.time() - start, 2)} seconds")

#fp = open('search_index.json', 'w')
#json.dump(index, fp)
