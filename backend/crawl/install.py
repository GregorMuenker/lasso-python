import subprocess
import sys
import os
import shutil
from io import StringIO
from tokenize import generate_tokens
from packaging.version import Version
import json
import re
from urllib.request import urlopen
import requests


def get_all_packages():
    """Retrieves all package names from PyPi.

    Returns:
        list of strings: List of package names.
    """
    contents = urlopen('https://pypi.org/simple/').read().decode('utf-8')
    pattern = re.compile(r'>([^<]+)</a>')
    package_list = [match[1] for match in re.finditer(pattern, contents)]
    # print(package_list)
    print(f'Total of {len(package_list):,} packages\n')
    return package_list


def get_most_downloaded(download_count=False):
    """Retrieves 8000 most downloaded package names from PyPi.

    Args:
        download_count (bool, optional): _description_. Defaults to False.

    Returns:
        list of strings: List of package names.
    """
    url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
    response = urlopen(url)
    data_json = json.loads(response.read())
    # most = [(pkg["project"], pkg["download_count"]) for pkg in data_json["rows"]]
    if download_count:
        most = [(pkg["project"], pkg["download_count"])
                for pkg in data_json["rows"]]
    else:
        most = [pkg["project"] for pkg in data_json["rows"]]
    return most


def get_info(folder):
    """Gets information from METADATA file.

    Args:
        folder (string): Dist-info folder name with METADATA file.

    Returns:
        dictionary: Information from Metadata.
            name (string): Package name.
            version (string): Package version.
            dependencies (list of strings): List of package dependencies.
    """
    path = f"installed/{folder}/METADATA"
    file = open(path, "r", encoding="utf-8")
    dependencies = []
    for line in file:
        if line.startswith("Name: "):
            name = line.split(":")[1].strip()
        if line.startswith("Version: "):
            version = line.split(":")[1].strip()
        if line.startswith("Requires-Dist: "):
            dependencies.append(line.split(":")[1].strip())
    return {
        "name": name,
        "version": version,
        "dependencies": dependencies
    }


def tokenize(string):
    """Tokenizes a given string.

    Args:
        string (string): String.

    Returns:
        list of strings: List of tokens.
    """
    STRING = 1
    return list(
        token[STRING]
        for token in generate_tokens(StringIO(string).readline)
        if token[STRING]
    )


def reformat_dependency(dependency):
    """Splits given dependency into package name and its version requirements.

    Args:
        dependency (string): Dependency.

    Returns:
        project (string): Package name.
        tuples (list of tuple strings): List of tuples, which include an operator and a version.
    """
    result = {}
    if ";" in dependency:
        return False
    else:
        dep = dependency.split(",")
        project = get_package_name(dep[0])

        tuples = []
        for index, item in enumerate(dep):
            tokens = tokenize(item)
            if index == 0:
                tokens.pop(0)
            operator = tokens[0]
            version = "".join(tokens[1:])
            tuples.append((operator, version))
    return project, tuples


def check_dependency(project, requirements):
    """Checks if dependency is already fulfilled.

    Args:
        project (string): Package name.
        requirements (list of tuple strings): output of reformat_dependency.

    Returns:
        result (list of strings): List of local versions that satisfy the requirements.
    """
    local_versions = get_local_versions(project)
    result = []
    for local_version in local_versions:
        satisfy = True
        for operator, version in requirements:
            comparison = compare_versions(local_version, operator, version)
            if not comparison:
                satisfy = False
                break
        if satisfy:
            result.append(local_version)
    return result


def get_local_versions(project):
    """Provides a list of local version for a provided package.

    Args:
        project (string): Package name.

    Returns:
        versions (list of strings): List of locally installed versions.
    """
    folders = [folder for folder in os.listdir(
        "installed") if folder.startswith(project)]
    versions = []
    for folder in folders:
        dist_folder = [item for item in os.listdir(
            f"installed/{folder}") if item.endswith(".dist-info")][0]
        version = get_info(f"{folder}/{dist_folder}")["version"]
        versions.append(version)
    return versions


def compare_versions(left, operator, right):
    """Compares two versions with each other using a provided operator.

    Args:
        left (string): Version number.
        operator (string): Operator.
        right (string): Version number.

    Returns:
        boolean: Result of version comparison.
    """
    v1 = Version(left)
    v2 = Version(right)
    result = eval(f"v1 {operator} v2")
    return result


def get_package_name(string):
    """Retrieves package name from provided (dependency) string.

    Args:
        string (string): pip install command string.

    Returns:
        string: Package name.
    """
    match = re.match(r"^[a-zA-Z0-9_\-]+", string)
    if match:
        return match.group(0)
    else:
        print("No project name found!")
        return

def satisfy_condition(dependency):
    """Checks if dependency condition (after ";") is satisfied.

    Args:
        dependency (string): Dependency string.

    Returns:
        boolean: Result of check.
    """
    parts = dependency.split(";")
    if len(parts) > 1:
        dependency, condition = parts
        if "extra" in condition:
            return False
        elif "python_version" in condition:
            print(condition)
            print(tokenize(condition))
            _, operator, version = tokenize(condition.strip())
            return compare_versions(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", operator, version.strip('"'))
        else:
            return True #?
    else:
        return True

def get_latest_version(package_name):
    """Retrieves latest version of a given package from PyPi.

    Args:
        package_name (string): Package name.

    Returns:
        latest_version (string): Latest version.
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        latest_version = data["info"]["version"]
        return latest_version
    else:
        return None

class installHandler:
    def __init__(self):
        if not os.path.exists("index.json"):
            self.index = {}
        else:
            with open('index.json', 'r') as file:
                self.index = json.load(file)

    def install(self, package):
        """Installs Package and it's dependencies in "installed" folder.

        Args:
            package (str): Package name with or without version requirements.

        Returns:
            name (str): Name of the package.
            version (str): Version of the package.
        """

        name = get_package_name(package)
        if not name:
            return
        # FIXME: Check if latest version or version that satisfies the requirements is already installed!
        if not (local_versions := get_local_versions(name)):
            path = "installed/tmp"
            subprocess.check_call([sys.executable, "-m", "pip",
                                "install", package, "--no-deps", "-q", "-t", path])
            print(f"Installing {name}")
            local_path = f"tmp"
        else:
            print(f"{name} already installed!")
            path = f"installed/{name}-{local_versions[0]}"
            local_path = f"{name}-{local_versions[0]}"
        info = [get_info(f"{local_path}/{item}") for item in os.listdir(
            path) if item.endswith(".dist-info")][0]

        name, version, dependencies = info["name"], info["version"], info["dependencies"]
        destination = f"installed/{name}-{version}"
        shutil.move(path, destination)
        
        deps = []
        for dependency in dependencies:
            if satisfy_condition(dependency):
                dep_name, dep_version = self.install(dependency)
                print(dep_name, dep_version)
                deps.append((dep_name, dep_version))

        self.index[f"{name}:{version}"] = deps
        return name, version

    def dump_index(self):
        out_file = open("index.json", "w")
        json.dump(self.index, out_file)

if __name__ == "__main__":
    # installHandler = installHandler()
    # installHandler.install("pandas")
    # installHandler.dump_index()

    # dependency = "pysocks!=1.5.7,<2.0,>=1.5.6"
    # install(dependency)

    print(get_latest_version("pandas"))
