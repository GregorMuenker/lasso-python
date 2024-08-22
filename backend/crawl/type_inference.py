import importlib
import json
import os
import sys

from backend.constants import INSTALLED
from backend.crawl.inference_engines import hityper

active_folder = "active"
temp_folder = "temp"


def infer_datatypes_module(package_name, module_name_with_prefix, type_inference_engine):
    global temp_folder
    module_path = os.path.join(active_folder, module_name_with_prefix.replace(".", "/") + ".py")
    package_path = os.path.join(active_folder, package_name)
    if type_inference_engine == "HiTyper":
        hityper.infer_datatypes_module(module_path, package_path, module_name_with_prefix)


def get_inferred_datatypes_function(module_name_with_prefix, function_name, dependent_class):
    global temp_folder
    try:
        if dependent_class is None:
            dependent_class = "global"
        inferred_datatypes_module = json.load(open(f"{temp_folder}/{module_name_with_prefix}_INFERREDTYPES.json", "r"))
        return inferred_datatypes_module[f"{function_name}@{dependent_class}"]
    except KeyError:
        print(f"Datatypes of function {module_name_with_prefix}.{function_name} not inferred!")
        return {}
    except FileNotFoundError:
        return {}


def clear_type_inferences():
    global temp_folder
    for x in [x for x in os.listdir(temp_folder) if "INFERREDTYPES" in x]:
        os.remove(os.path.join(temp_folder, x))


if __name__ == "__main__":
    package_name = "calculator-01"
    version = "1.0.0"
    sys.path.insert(0, os.path.join(INSTALLED, f"{package_name}-{version}"))
    infer_datatypes_module("calculator_01", "calculator_01.calculator_main", "HiTyper")
    inferred_datatypes_function_dict = get_inferred_datatypes_function("calculator_01.calculator_main", "addition",
                                                                       "Calculator")
    print(inferred_datatypes_function_dict)
    #clear_type_inferences()
    sys.path.remove(os.path.join(INSTALLED, f"{package_name}-{version}"))
