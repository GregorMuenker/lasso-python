import importlib
import json
import os
import hityper

from crawl import run

active_folder = "./active"
temp_folder = "temp"


def infer_datatypes_module(package_name, module_name_with_prefix):
    global temp_folder
    module_path = os.path.join(active_folder, module_name_with_prefix.replace(".", "/") + ".py")
    package_path = os.path.join(active_folder, package_name)
    print(os.system(f"hityper infer -s {module_path} -d {temp_folder} -p {package_path}"))


def get_inferred_datatypes_function(module_name_with_prefix, function_name, dependent_class):
    global temp_folder
    module_path = os.path.join(active_folder, module_name_with_prefix.replace(".", "/"))
    module_path = module_path.replace('/', '_') + '_INFERREDTYPES.json'
    if dependent_class is None:
        dependent_class = "global"
    inferred_datatypes_module = json.load(open(f"{temp_folder}/{module_path}", "r"))
    inferred_datatypes_function = inferred_datatypes_module[f"{function_name}@{dependent_class}"]
    inferred_datatypes_function_dict = {x["name"]: x["type"] for x in inferred_datatypes_function}
    inferred_datatypes_function_dict["return"] = inferred_datatypes_function_dict.pop(function_name)
    return inferred_datatypes_function_dict


def clear_type_inferences():
    global temp_folder
    for x in [x for x in os.listdir(temp_folder) if "INFERREDTYPES" in x]:
        os.remove(os.path.join(temp_folder, x))


if __name__ == "__main__":
    package_name = "urllib3"
    version_name = "2.2.2"
    run.move_active(f"{package_name}-{version_name}")
    infer_datatypes_module(package_name, "urllib3.connection")
    inferred_datatypes_function_dict = get_inferred_datatypes_function("urllib3.connection", "__init__", "HTTPConnection")
    print(inferred_datatypes_function_dict)
    clear_type_inferences()
    run.remove_active()
