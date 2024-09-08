import importlib
import json
import os
import sys

from backend.constants import INSTALLED, TYPE_INFERENCING_TEMP
from backend.crawl.inference_engines import hityper


def infer_datatypes_module(module_name_with_prefix, module_path, type_inference_engine):
    package_path = "/".join(module_path.split("/")[:-len(module_name_with_prefix.split("."))+1])
    if type_inference_engine == "HiTyper":
        hityper.infer_datatypes_module(module_path, package_path, module_name_with_prefix)


def get_inferred_datatypes_function(module_name_with_prefix, function_name, dependent_class):
    try:
        if dependent_class is None:
            dependent_class = "global"
        inferred_datatypes_module = json.load(open(f"{TYPE_INFERENCING_TEMP}/{module_name_with_prefix}_INFERREDTYPES.json", "r"))
        return inferred_datatypes_module[f"{function_name}@{dependent_class}"]
    except KeyError:
        print(f"Datatypes of function {module_name_with_prefix}.{function_name} not inferred!")
        return {}
    except FileNotFoundError:
        return {}


def clear_type_inferences():
    for x in [x for x in os.listdir(TYPE_INFERENCING_TEMP) if "INFERREDTYPES" in x]:
        os.remove(os.path.join(TYPE_INFERENCING_TEMP, x))


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
