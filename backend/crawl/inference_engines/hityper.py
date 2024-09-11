import json
import os
import subprocess
from dotenv import load_dotenv
load_dotenv()
if os.getenv("RUNTIME_ENVIRONMENT") == "docker":
    TYPE_INFERENCING_TEMP = os.getenv("TYPE_INFERENCING_TEMP")
else:
    from backend.constants import TYPE_INFERENCING_TEMP


def parse_file(module_path, module_name_with_prefix):
    try:
        inferred_datatypes_module = json.load(
            open(f"{TYPE_INFERENCING_TEMP}/{module_path.replace('/', '_').replace('.py', '')}_INFERREDTYPES.json", "r"))
        os.remove(f"{TYPE_INFERENCING_TEMP}/{module_path.replace('/', '_').replace('.py', '')}_INFERREDTYPES.json")
        for function_identifier, variable_list in inferred_datatypes_module.items():
            if function_identifier != "global@global":
                inferred_datatypes_module[function_identifier] = {x["name"]: x["type"] for x in variable_list}
                inferred_datatypes_module[function_identifier]["return"] = inferred_datatypes_module[
                    function_identifier].pop(function_identifier.split("@")[0])
        json.dump(inferred_datatypes_module, open(f"{TYPE_INFERENCING_TEMP}/{module_name_with_prefix}_INFERREDTYPES.json", "w"))
    except FileNotFoundError:
        pass


def infer_datatypes_module(module_path, package_path, module_name_with_prefix):
    #subprocess.run(f"hityper infer -s {module_path} -d {temp_folder} -p {package_path}", shell=True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
    subprocess.run(f"hityper infer -s {module_path} -d {TYPE_INFERENCING_TEMP} -p {package_path}", shell=True)
    parse_file(module_path, module_name_with_prefix)
