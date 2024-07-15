import subprocess
import sys
import os
import shutil
from io import StringIO
from tokenize import generate_tokens
from packaging.version import Version
import json
from collections import defaultdict
import re
from urllib.request import urlopen


def get_all_packages():
    contents = urlopen('https://pypi.org/simple/').read().decode('utf-8')
    pattern = re.compile(r'>([^<]+)</a>')
    package_list = [match[1] for match in re.finditer(pattern, contents)]
    # print(package_list)
    print(f'Total of {len(package_list):,} packages\n')
    return package_list


def get_most_downloaded(download_count=False):
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
    STRING = 1
    return list(
        token[STRING]
        for token in generate_tokens(StringIO(string).readline)
        if token[STRING]
    )


def reformat_dependency(dependency):
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
    v1 = Version(left)
    v2 = Version(right)
    result = eval(f"v1 {operator} v2")
    return result


def get_package_name(string):
    match = re.match(r"^[a-zA-Z0-9_\-]+", string)
    if match:
        return match.group(0)
    else:
        print("No project name found!")
        return


def install(package):
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
    # name = tokenize(package)[0]
    # FIXME: Check if latest version or version that satisfies the requirements is already installed!
    if not (local_version := get_local_versions(name)):
        path = "installed/tmp"
        subprocess.check_call([sys.executable, "-m", "pip",
                               "install", package, "--no-deps", "-q", "-t", path])
        print(f"Installing {name}")
        local_path = f"tmp"
    else:
        print(f"{name} already installed!")
        path = f"installed/{name}-{local_version[0]}"
        local_path = f"{name}-{local_version[0]}"
    info = [get_info(f"{local_path}/{item}") for item in os.listdir(
        path) if item.endswith(".dist-info")][0]

    name, version, dependencies = info["name"], info["version"], info["dependencies"]
    destination = f"installed/{name}-{version}"
    shutil.move(path, destination)

    if not os.path.exists("index.json"):
        index = {}
    else:
        with open('index.json', 'r') as file:
            index = json.load(file)
    
    deps = []
    # FIXME: Multiple Entries for same package (Different python versions)!
    for dependency in dependencies:
        if not ("extra" in dependency):
            dep_name = get_package_name(dependency)
            local_folders = [folder for folder in os.listdir(
                "installed") if folder.startswith(dep_name)]
            print(local_folders)
            if local_folders:
                print(f"Dependency {dep_name} already satisfied!")
                info = [get_info(f"{local_folders[0]}/{item}") for item in os.listdir(
                        f"installed/{local_folders[0]}") if item.endswith(".dist-info")][0]
                dep_name, dep_version = info["name"], info["version"]
            # project, requirements = reformat_dependency(dependency)
            # print(project, requirements)
            # if local_versions := check_dependency(project, requirements):
            #     dep_name, dep_version = project, local_versions[0]
            # else:
            #     # TODO: need to get version number back to insert into index
            #     dep_name, dep_version = install(dependency)
            else:
                dep_name, dep_version = install(dependency)
            print(dep_name, dep_version)
            deps.append((dep_name, dep_version))

    # index[(name, version)] = deps
    # FIXME: Dependencies of dependencies not in index.
    index[f"{name}:{version}"] = deps
    out_file = open("index.json", "w")
    json.dump(index, out_file)
    return name, version


if __name__ == "__main__":
    # install("python-dateutil")
    install('hypothesis>=6.46.1; extra == "test"')
    # dependency = "pysocks!=1.5.7,<2.0,>=1.5.6"
    # install(dependency)
