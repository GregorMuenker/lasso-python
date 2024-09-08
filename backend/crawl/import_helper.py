import copy
import importlib
import json
import os
import shutil
import sys

from Levenshtein import distance

from backend.constants import INSTALLED, RUNTIME, INDEX


def get_import_name(package_name, version, runtime=False):
    if runtime:
        package_path = RUNTIME
    else:
        package_path = os.path.join(INSTALLED, f"{package_name}-{version}")
    folder_names = [[x, distance(package_name, x)] for x in os.listdir(package_path) if "dist-info" not in x]
    folder_names = sorted(folder_names, key=lambda x: x[1])
    package_name = folder_names[0][0].replace(".py", "")
    return package_name


def check_version_mismatch(package_name, version, runtime=False):
    package_name = get_import_name(package_name, version, runtime)
    module = importlib.import_module(package_name)
    if module.__version__ != version:
        print(f"Resolving {package_name} version mismatch: Target {version} - Imported {module.__version__}")
        del module
        keys = copy.deepcopy(list(sys.modules.keys()))
        for key in keys:
            if key.startswith(f"{package_name}."):
                del sys.modules[key]
        del sys.modules[package_name]
    importlib.import_module(package_name)


def get_dependencies(package_name, version):
    with open(INDEX, 'r') as file:
        index = json.load(file)
        return index[f"{package_name}:{version}"]


class ImportHelper:
    def __init__(self, runtime=False):
        self.runtime = runtime
        if self.runtime:
            sys.path.insert(0, RUNTIME)
        self.loaded_packages = []

    def pre_load_package(self, package_name, version):
        if not self.runtime:
            package_path = os.path.join(INSTALLED, f"{package_name}-{version}")
            sys.path.insert(0, package_path)
        check_version_mismatch(package_name, version, self.runtime)
        self.loaded_packages.append([package_name, version])

    def unload_package(self):
        if self.runtime:
            sys.path.remove(RUNTIME)
            shutil.rmtree(RUNTIME)
        else:
            for package_name, version in self.loaded_packages:
                package_path = os.path.join(INSTALLED, f"{package_name}-{version}")
                sys.path.remove(package_path)
                shutil.rmtree(package_path)
