import json
import os

active_folder = "active"
temp_folder = "temp"


def parse_file(module_path, module_name_with_prefix):
    inferred_datatypes_module = json.load(
        open(f"{temp_folder}/{module_path.replace('/', '_').replace('.py', '')}_INFERREDTYPES.json", "r"))
    os.remove(f"{temp_folder}/{module_path.replace('/', '_').replace('.py', '')}_INFERREDTYPES.json")
    for function_identifier, variable_list in inferred_datatypes_module.items():
        if function_identifier != "global@global":
            inferred_datatypes_module[function_identifier] = {x["name"]: x["type"] for x in variable_list}
            inferred_datatypes_module[function_identifier]["return"] = inferred_datatypes_module[
                function_identifier].pop(function_identifier.split("@")[0])
    json.dump(inferred_datatypes_module, open(f"{temp_folder}/{module_name_with_prefix}_INFERREDTYPES.json", "w"))


def infer_datatypes_module(module_path, package_path, module_name_with_prefix):
    global temp_folder
    os.system(f"hityper infer -s {module_path} -d {temp_folder} -p {package_path}")
    parse_file(module_path, module_name_with_prefix)
