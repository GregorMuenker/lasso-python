import subprocess
import sys
import os
import shutil
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet
import json
import re
from urllib.request import urlopen
import requests
import platform
import certifi
import ssl

import git
repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from dotenv import load_dotenv
load_dotenv()
if os.getenv("RUNTIME_ENVIRONMENT") == "docker":
    INSTALLED = os.getenv("INSTALLED")
    INDEX = os.getenv("INDEX")
else:
    from backend.constants import INSTALLED, INDEX
from backend.crawl.nexus import Nexus, Package
from backend.crawl.log import log_exception, log_dependencyexception, log_uploadexception

def get_all_packages():
    """Retrieves all package names from PyPi.

    Returns:
        list of strings: List of package names.
    """
    context = ssl.create_default_context(cafile=certifi.where())
    contents = urlopen('https://pypi.org/simple/', context=context).read().decode('utf-8')
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
    context = ssl.create_default_context(cafile=certifi.where())
    url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
    response = urlopen(url, context=context)
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
    with open(path, "r", encoding="utf-8") as file:
        # Initialize default values
        name = None
        version = None
        dependencies = []

        # Compile regex patterns
        name_pattern = re.compile(r"^Name:\s*(.+)$")
        version_pattern = re.compile(r"^Version:\s*(.+)$")
        requires_dist_pattern = re.compile(r"^Requires-Dist:\s*(.+)$")

        # Process each line in the file
        for line in file:
            # Match name
            name_match = name_pattern.match(line)
            if name_match and name is None:
                name = name_match.group(1).strip()

            # Match version
            version_match = version_pattern.match(line)
            if version_match and version is None:
                version = version_match.group(1).strip()

            # Match dependencies
            requires_dist_match = requires_dist_pattern.match(line)
            if requires_dist_match:
                dependencies.append(requires_dist_match.group(1).strip())

    return {
        "name": name,
        "version": version,
        "dependencies": dependencies
    }


def reformat_dependency(dependency):
    """Splits given dependency into its version requirements.

    Args:
        dependency (string): Dependency.

    Returns:
        tuples (list of tuple strings): List of tuples, which include an operator and a version.
    """
    # Regex to extract the package name and version requirements
    match = re.match(r'^([^<>=!~]+)(.*)', dependency)
    if not match:
        raise ValueError(f"Invalid dependency format: {dependency}")

    version_part = match.group(2).strip()

    # Regex to match each version constraint
    version_constraints = re.findall(r'([<>=!~]+)\s*([\d\w.]+)', version_part)

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
    if right.endswith(".") and operator == "!=":
        return not (right in left)
    specifier = SpecifierSet(operator+right)
    v1 = Version(left)
    return v1 in specifier


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

def check_environment(operator, reference, condition_type):
    """Checks dependency condition variables.

    Args:
        operator (str): Operator.
        reference (str): Reference value from condition.
        condition_type (str): Type of condition.

    Returns:
        boolean: Whether condition is satisfied or not.
    """
    if condition_type == "python_version":
        return check_python_version(operator, reference)
    elif condition_type == "os_name":
        value = os.name
    elif condition_type == "platform_system":
        value = platform.system()
    elif condition_type == "sys_platform":
        value = sys.platform

    return eval(f"value {operator} reference")

def check_python_version(operator, version):
    """Checks Python Version requirement.

    Args:
        operator (str): Operator.
        version (str): Version number.

    Returns:
        boolean: Whether local python version complies with requirement.
    """
    return compare_versions(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", operator, version)

def satisfy_condition(dependency):
    """Checks if dependency condition (after ";") is satisfied, including python_version, os_name, platform_system, and sys_platform.

    Args:
        dependency (string): Dependency string.

    Returns:
        string: The dependency name if conditions are satisfied, else None.
    """
    parts = dependency.split(";")
    if len(parts) > 1:
        dependency, condition = parts
        if "extra" in condition:
            return

        # Define regex to match conditions like python_version, os_name, platform_system, and sys_platform
        condition_pattern = r"(python_version|os_name|platform_system|sys_platform)\s*([<>=!]+)\s*['\"]?([^'\"]+)['\"]?"
        matches = re.finditer(condition_pattern, condition.strip())

        # Process each condition match
        for match in matches:
            condition_type, operator, value = match.groups()
            if not check_environment(operator, value, condition_type):
                return

    return dependency  # Return the dependency if no conditions fail


def get_latest_version(package_name):
    """Retrieves the latest version of a given package from PyPi that is supported by the local python version,
    while also filtering out yanked and pre-release versions.

    Args:
        package_name (string): Package name.

    Returns:
        latest_version (string): Latest version.
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        releases = data["releases"]
        result = []

        for release, dists in releases.items():
            # Filter out yanked versions by checking if any distribution is marked as yanked
            is_yanked = all(dist.get("yanked", False) for dist in dists)
            if is_yanked:
                continue  # Skip this release if it's yanked

            requires_python = [item.get("requires_python") for item in dists]
            requires_python = list(dict.fromkeys(requires_python))
            if requires_python and requires_python[0]:
                pattern = r"([<>=!~]+)([^\,]+(\..)*)"
                matches = re.finditer(pattern, requires_python[0])
                requirement = [(match.group(1), match.group(2)) for match in matches]
            else:
                requirement = None
            result.append((release, requirement))

        valid_versions = []
        skipped_versions = []  # To keep track of versions that were skipped

        # Check each release for version validity and Python requirements
        for release, requirement in result:
            try:
                valid_release = Version(release)  # Check if it's a valid PEP 440 version
                if valid_release.is_prerelease:
                    continue  # Skip pre-release versions
                valid_versions.append((valid_release, requirement))
            except InvalidVersion:
                skipped_versions.append(release)
                continue  # Skip invalid versions

        # Log or print any skipped versions
        if skipped_versions:
            print(f"Warning: Skipped invalid versions: {', '.join(skipped_versions)}")

        # Sort versions by release number, and return the highest valid one
        for release, requirement in sorted(valid_versions, key=lambda x: x[0], reverse=True):
            if not requirement:
                return str(release)
            else:
                check = [check_python_version(op, ver) for op, ver in requirement]
                if all(check):
                    return str(release)
    
    else:
        return None


class installHandler:
    def __new__(cls, nexus: Nexus):
        if nexus:
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
        requirements = reformat_dependency(package)
        satisfactory_versions = self.check_request(name, requirements)

        if not satisfactory_versions:
            path = f"{INSTALLED}/tmp"
            try:
                subprocess.check_call([sys.executable, "-m", "pip",
                                    "install", package, "--no-deps", "-q", "-t", path])
            except Exception as e:
                log_exception(name, "unknown", e)
                print("Installation failed!")
                return
            
            print(f"Installing {name}")
            local_path = f"tmp"

            info = [get_info(f"{local_path}/{item}") for item in os.listdir(
                path) if item.endswith(".dist-info")][0]
            # name, version, dependencies = info["name"], info["version"], info["dependencies"]
            version, dependencies = info["version"], info["dependencies"]
            destination = f"{name}-{version}"
            # shutil.move(path, f"{INSTALLED}/{destination}")
            shutil.copytree(path, f"{INSTALLED}/{destination}", dirs_exist_ok=True)
            shutil.rmtree(path)


            pkg = Package(name, version)
            pkg.compress()
            if not self.nexus.upload(pkg):
                #TODO: Log exception
                print(f"Could not upload artifact {name} {version}")
                return
            
            deps = {}
            for dependency in dependencies:
                if short_dependency := satisfy_condition(dependency):
                    deps[get_package_name(dependency)] = {"requirements": short_dependency, "version": None}
            self.index[f"{name}:{version}"] = deps
            self.dump_index()
            
            for dependency in dependencies:
                if short_dependency := satisfy_condition(dependency):
                    try:
                        dep_name, dep_version, _ = self.install(short_dependency)
                        # print(dep_name, dep_version)
                        self.index[f"{name}:{version}"][dep_name]["version"] = dep_version
                        self.dump_index()
                    except:
                        # TODO: Log exception
                        print(f"Could not install dependency {dependency} of package {name} {version}!")
            already_installed = False
        else:
            print(f"{name} already installed!")
            version = satisfactory_versions[0]
            # Checking if all dependencies are installed.
            for dep_name, dep_dict in self.index[f"{name}:{version}"].items():
                if not dep_dict["version"]:
                    try:
                        _, dep_version, _  = self.install(dep_dict["requirements"])
                        self.index[f"{name}:{version}"][dep_name]["version"] = dep_version
                        self.dump_index()
                    except:
                        # TODO: Log exception
                        print(f"Could not install dependency {dependency}!")
            already_installed = True

        self.dump_index()
        return name, version, already_installed

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
            # print(latest)
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
    # packages = get_most_downloaded()
    installHandler = installHandler(nexus)
    # for package in packages[:1]:
    #     installHandler.install(package)
    installHandler.install("numpy")
    # package = Package("boto3", "1.35.15")
    # nexus.download(package)

