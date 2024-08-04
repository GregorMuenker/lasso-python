import importlib
import json
import os
import inference_engines.hityper

from crawl import run

active_folder = "active"
temp_folder = "temp"


def infer_datatypes_module(package_name, module_name_with_prefix, type_inference_engine):
    global temp_folder
    module_path = os.path.join(active_folder, module_name_with_prefix.replace(".", "/") + ".py")
    package_path = os.path.join(active_folder, package_name)
    if type_inference_engine == "HiTyper":
        inference_engines.hityper.infer_datatypes_module(module_path, package_path, module_name_with_prefix)


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


def clear_type_inferences():
    global temp_folder
    for x in [x for x in os.listdir(temp_folder) if "INFERREDTYPES" in x]:
        os.remove(os.path.join(temp_folder, x))


if __name__ == "__main__":
    package_name = "calculator-01"
    version_name = "1.0.0"
    run.move_active(f"{package_name}-{version_name}")
    infer_datatypes_module("calculator_01", "calculator_01.calculator_main", "HiTyper")
    inferred_datatypes_function_dict = get_inferred_datatypes_function("calculator_01.calculator_main", "addition",
                                                                       "Calculator")
    print(inferred_datatypes_function_dict)
    clear_type_inferences()
    run.remove_active()
