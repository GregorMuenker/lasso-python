import sys
import git
repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from backend.crawl import install, splitting, upload_index, import_helper, type_inference
from backend.crawl.nexus import Nexus, Package
from pathlib import Path
import json
import os
import uuid
import subprocess

from dotenv import load_dotenv
load_dotenv()
if os.getenv("RUNTIME_ENVIRONMENT") == "docker":
    INSTALLED = os.getenv("INSTALLED")
    INDEX = os.getenv("INDEX")
else:
    from backend.constants import INSTALLED, INDEX


def parse_llm_code(llm_file):
    file = open(llm_file, 'r')
    tasks = json.load(file)

    code = ""
    for task in tasks:
        code += task["code"] + "\n\n"

    # Define the folder and file structure
    version_folder = "lasso-llm-0.0.1"
    subfolder = "lasso-llm"
    file_name = f"{Path(llm_file).stem}.py"

    # Full path creation
    full_path = os.path.join(INSTALLED, version_folder, subfolder)
    os.makedirs(full_path, exist_ok=True)

    # Full path to the file
    file_path = os.path.join(full_path, file_name)

    # Write the content of the `code` variable into the Python file
    with open(file_path, 'w') as file:
        file.write(code)

    # Create an __init__.py file to make the subfolder a package, including the version
    init_file_path = os.path.join(full_path, '__init__.py')
    with open(init_file_path, 'w') as init_file:
        init_file.write(f'"""lasso-llm package."""\n')
        init_file.write(f'__version__ = "0.0.1"\n')

    print(f"LLM code parsed and saved at: {file_path}")

    index = json.load(open(INDEX, "r"))
    index[f"lasso-llm:0.0.1"] = {}
    json.dump(index, open(INDEX, "w"))

    pkg = Package("lasso-llm", "0.0.1")
    pkg.compress()
    nexus = Nexus()
    nexus.upload(pkg)


def index_package(package_name, llm_file=None, type_inferencing_engine=None):
    """This function provides a pipeline for the steps of crawling and splitting a package. At the last step the
    created index will be uploaded to the solr index.

    Args:
        package_name(str): Name of requested pypi package
    """

    if package_name == "lasso-llm" and llm_file:
        parse_llm_code(llm_file)
        version = "0.0.1"
    else:
        nexus = Nexus()
        install_handler = install.installHandler(nexus)
        package_name, version, already_installed = install_handler.install(package_name)
        if already_installed:
            pkg = Package(package_name, version)
            nexus.download(pkg, runtime=False)
        install_handler.dump_index()
    imp_help = import_helper.ImportHelper()
    imp_help.pre_load_package(package_name, version)
    if type_inferencing_engine=="HiTyper":
        if len([x for x in imp_help.loaded_packages if x[0] == "numpy" or x[0] == "scipy"]) > 0:
            type_inferencing_engine = None
            print("numpy/scipy and any package with numpy/scipy as dependency can not be inferenced with HiTyper")
    package_name = import_helper.get_import_name(package_name, version)
    index = splitting.get_module_index(package_name, package_name, version, type_inferencing_engine=type_inferencing_engine)
    if type_inferencing_engine:
        type_inference.clear_type_inferences()
    upload_index.upload_index(index)

    # imp_help.unload_package()


if __name__ == "__main__":
    index_package("requests", type_inferencing_engine="HiTyper")
    # index_package("lasso-llm", llm_file="../evaluation/evaluation_sanitized-mbpp.json")

