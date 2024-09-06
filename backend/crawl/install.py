import subprocess
import sys
import os
import shutil
from io import StringIO
from tokenize import generate_tokens, TokenError
from packaging.version import Version
import json
import re
from urllib.request import urlopen
import requests
from nexus import Nexus, Package
import git

repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from backend.constants import INSTALLED, INDEX

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
    path = f"{INSTALLED}/{folder}/METADATA"
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
    tokens = []
    try:
        for token in generate_tokens(StringIO(string).readline):
            if token[STRING]:
                tokens.append(token[STRING])
    except TokenError:
        pass
    return tokens


def reformat_dependency(dependency):
    """Splits given dependency into its version requirements.

    Args:
        dependency (string): Dependency.

    Returns:
        tuples (list of tuple strings): List of tuples, which include an operator and a version.
    """
    # Regex to extract the package name and version requirements
    match = re.match(r'^([^<>=!]+)(.*)', dependency)
    if not match:
        raise ValueError(f"Invalid dependency format: {dependency}")

    version_part = match.group(2).strip()

    # Regex to match each version constraint
    version_constraints = re.findall(r'([<>=!]+)\s*([\d\w.]+)', version_part)

    tuples = [(operator.strip(), version.strip())
              for operator, version in version_constraints]

    return tuples


def get_local_versions(project):
    """Provides a list of local version for a provided package.

    Args:
        project (string): Package name.

    Returns:
        versions (list of strings): List of locally installed versions.
    """
    pattern = rf"^{re.escape(project)}-\d+(\.\d+)*"
    folders = [folder for folder in os.listdir(
        INSTALLED) if re.match(pattern, folder)]
    versions = []
    for folder in folders:
        dist_folder = [item for item in os.listdir(
            f"{INSTALLED}/{folder}") if item.endswith(".dist-info")][0]
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
    #FIXME: Versions with trailing * not supported! e.g. !=3.1.* Clean fix?
    if "*" in right and operator == "!=":
        if right.strip("*") in left:
            return False
        else:
            return True
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
            return
        elif "python_version" in condition:
            _, operator, version = tokenize(condition.strip())
            version = version.strip("'")
            version = version.strip('"')
            if not check_python_version(operator, version):
                return
    return dependency

def check_python_version(operator, version):
    return compare_versions(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", operator, version)

def get_latest_version(package_name):
    """Retrieves latest version of a given package from PyPi that is supported by the local python version.

    Args:
        package_name (string): Package name.

    Returns:
        latest_version (string): Latest version.
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # latest_version = data["info"]["version"]
        releases = data["releases"]
        result = []
        for release, dists in releases.items():
            requires_python = [item["requires_python"] for item in dists]
            requires_python = list(dict.fromkeys(requires_python))
            if requires_python:
                requirement = requires_python[0]
                if requirement:
                    pattern = r"([<>=!]+)([^\,]+(\..)*)"
                    matches = re.finditer(pattern, requirement)
                    # requirement = requirement.split(",")
                    requirement = [(match.group(1), match.group(2)) for match in matches]
            else:
                requirement = None
            result.append((release, requirement))
        for release, requirement in sorted(result, key=lambda x: Version(x[0]), reverse=True):
            if not requirement:
                return release
            else:
                print(requirement)
                check = [check_python_version(operator, version) for operator, version in requirement]
                if all(check):
                    return release

    else:
        #TODO: What to do if information cannot be fetched?
        return None


class installHandler:
    def __new__(cls, nexus: Nexus):
        if nexus.check_status(nexus.nexus_host):
            return super(installHandler, cls).__new__(cls)
        else:
            print(f"Cannot reach Nexus server at {nexus.nexus_host}")
            return None
    
    def __init__(self, nexus: Nexus):
        self.nexus = nexus
        if not os.path.exists(INDEX):
            self.index = {}
        else:
            with open(INDEX, 'r') as file:
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
            # TODO: Exception or just print?
            raise BaseException("Could not identify package name.")

        requirements = reformat_dependency(package)
        satisfactory_versions = self.check_request(name, requirements)

        if not satisfactory_versions:
            path = f"{INSTALLED}/tmp"
            # TODO: What to do when installation fails?
            subprocess.check_call([sys.executable, "-m", "pip",
                                   "install", package, "--no-deps", "-q", "-t", path])
            print(f"Installing {name}")
            local_path = f"tmp"

            info = [get_info(f"{local_path}/{item}") for item in os.listdir(
                path) if item.endswith(".dist-info")][0]
            # name, version, dependencies = info["name"], info["version"], info["dependencies"]
            version, dependencies = info["version"], info["dependencies"]
            destination = f"{name}-{version}"
            shutil.move(path, f"{INSTALLED}/{destination}")

            pkg = Package(name, version, destination)
            pkg.compress()
            # TODO: What to do if upload fails?
            if not self.nexus.upload(pkg):
                pass
            
            deps = {}
            for dependency in dependencies:
                if short_dependency := satisfy_condition(dependency):
                    deps[get_package_name(dependency)] = {"requirements": short_dependency, "version": None}
            self.index[f"{name}:{version}"] = deps
            self.dump_index()
            
            # deps = []
            for dependency in dependencies:
                if short_dependency := satisfy_condition(dependency):
                    dep_name, dep_version = self.install(short_dependency)
                    # print(dep_name, dep_version)
                    # deps.append((dep_name, dep_version))
                    self.index[f"{name}:{version}"][dep_name]["version"] = dep_version

            # self.index[f"{name}:{version}"] = deps
        
        else:
            print(f"{name} already installed!")
            version = satisfactory_versions[0]
            #TODO: Check Index for missing dependencies? Maybe save requirements in index?

        self.dump_index()
        return name, version

    def check_request(self, project, requirements):
        """Checks if install request is already satisfied.

        Args:
            project (string): Package name.
            requirements (list of tuple strings): output of reformat_dependency.

        Returns:
            result (list of strings): List of local versions that satisfy the requirements.
        """
        # local_versions = get_local_versions(project)
        local_versions = self.nexus.get_versions(project)
        # print(local_versions)

        result = []

        if not requirements:
            latest = get_latest_version(project)
            print(latest)
            if latest in local_versions:
                result = [latest]
        else:
            for local_version in local_versions:
                satisfy = True
                for operator, version in requirements:
                    comparison = compare_versions(
                        local_version, operator, version)
                    if not comparison:
                        satisfy = False
                        break
                if satisfy:
                    result.append(local_version)
        return result

    def dump_index(self):
        out_file = open(INDEX, "w")
        json.dump(self.index, out_file)


if __name__ == "__main__":
    nexus = Nexus()
    packages = get_most_downloaded()
    installHandler = installHandler(nexus)
    for package in packages[:20]:
        installHandler.install(package)
    # installHandler.install("yarl")
    installHandler.dump_index()
    # print(get_latest_version("pandas"))
