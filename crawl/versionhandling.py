from pypi_simple import PyPISimple, tqdm_progress_factory
import pandas as pd
from tqdm import tqdm
from packaging.version import Version
from packaging.metadata import parse_email
from io import StringIO
from tokenize import generate_tokens
import os
import json
import site

from download import get_latest_tar


def create_table(package_list):
    with PyPISimple() as client:
        info = []
        for package in tqdm(package_list, desc="Updating Info Table"):
            page = client.get_project_page(package)
            if page.packages:
                pkg = get_latest_tar(page)
                if pkg:
                    if pkg.project and pkg.version:
                        project = pkg.project
                        version = pkg.version
                    else:
                        split = pkg.filename.split("-")
                        project = "-".join(split[:-1])
                        version = split[-1][:-7]
                    package = {"project": project, "version": version}
                    if pkg.requires_python:
                        package["requires_python"] = pkg.requires_python
                    # package["requires_dist"] = None
                    # if pkg.has_metadata:
                    #     src = client.get_package_metadata(pkg)
                    #     md, _ = parse_email(src)
                    #     package["requires_dist"] = md.get("requires_dist")
                    packages = os.listdir("packages")
                    match = [item for item in packages if item.startswith(project)]
                    if match:
                        latest = match[-1]
                        package["local_version"] = latest.split("-")[-1]
                        _, _, package["local_requires_dist"] = get_info(latest)
                        remain = check_dependencies(package["local_requires_dist"])
                        if not remain:
                            package["can_run"] = True
                            package["remain"] = None
                        else:
                            package["can_run"] = False
                            package["remain"] = remain
                    info.append(package)
        df = pd.DataFrame(info)
        if os.path.exists("info.csv"):
            new = df["project"].tolist()
            old = pd.read_csv("info.csv", sep=";")
            difference = old[~old["project"].isin(new)]
            df = pd.concat([df, difference], ignore_index=True)
            # df = pd.merge(df, old)
        df.to_csv("info.csv", sep=";", index=False)


def group_dependencies():
    info = pd.read_csv("info.csv", sep=";")  # TODO: Class instead?
    remain = info[info["can_run"] == False]["remain"].to_list()
    print(remain)
    # TODO: Merge Dictionaries
    # Simple Approach
    merged = {}
    for dict in remain:
        print(type(dict))
        # FIXME: str to dict
        for project, requirements in dict.items():
            if project in merged:
                merged[project].append(requirements)
            else:
                merged[project] = requirements
    return merged


def get_info(folder, type="local"):
    if type == "installed":
        path = f"installed/{folder}/METADATA"
    elif type == "site":
        path = f"{site.USER_SITE}/{folder}/METADATA"
    elif type == "local":
        path = f"packages/{folder}/PKG-INFO"
    file = open(path, "r", encoding="utf-8")
    dependencies = []
    for line in file:
        if line.startswith("Name: "):
            name = line.split(":")[1].strip()
        if line.startswith("Version: "):
            version = line.split(":")[1].strip()
        if line.startswith("Requires-Dist: "):
            dependencies.append(line.split(":")[1].strip())
    return name, version, dependencies  # TODO: return dict?


def get_local_versions(project):
    folders = [folder for folder in os.listdir("packages") if folder.startswith(project)]
    versions = []
    for folder in folders:
        _, version, _ = get_info(folder)
        versions.append(version)
    return versions


def check_dependencies(dependencies):
    remain = {}
    dependencies = reformat_dependencies(dependencies)
    for project, requirements in dependencies.items():
        project, versions = check_dependency(project, requirements)
        versions = [key for key, value in versions.items() if value]
        if not versions:
            remain[project] = requirements
    return remain


def check_dependency(project, requirements):
    local_versions = get_local_versions(project)
    result = {}
    for local_version in local_versions:
        result[local_version] = True
        for operator, version in requirements:
            comparison = compare_versions(local_version, operator, version)
            if not comparison:
                result[local_version] = False
                break
    return project, result


def tokenize(string):
    STRING = 1
    return list(
        token[STRING]
        for token in generate_tokens(StringIO(string).readline)
        if token[STRING]
    )


def reformat_dependencies(dependencies):
    result = {}
    for dep in dependencies:
        if ";" in dep:
            pass
        else:
            dep = dep.split(",")
            project = tokenize(dep[0])[0]

            tuples = []
            for index, item in enumerate(dep):
                tokens = tokenize(item)
                if index == 0:
                    tokens.pop(0)
                operator = tokens[0]
                version = "".join(tokens[1:])
                tuples.append((operator, version))
            result[project] = tuples
    return result


def compare_versions(left, operator, right):
    v1 = Version(left)
    v2 = Version(right)
    result = eval(f"v1 {operator} v2")
    return result


if __name__ == '__main__':
    # dependency = {'project': 'botocore', 'requirements': [('<', '1.34.70'), ('>=', '1.34.41')]}
    # print(check_dependency(dependency))
    # dependencies = ['botocore<1.34.70,>=1.34.41', 'aiohttp<4.0.0,>=3.7.4.post0', 'wrapt<2.0.0,>=1.10.10',
    #                 'aioitertools<1.0.0,>=0.5.1', 'awscli<1.32.70,>=1.32.41; extra == "awscli"',
    #                 'boto3<1.34.70,>=1.34.41; extra == "boto3"']
    # print(check_dependencies(dependencies))
    # print(group_dependencies())
    print(get_info("urllib3/urllib3-2.2.2.dist-info", "installed"))
