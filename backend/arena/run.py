import importlib
import shutil
import os
import sys
from argparse import ArgumentParser
import site
import json
import git

repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from backend.constants import INSTALLED, INDEX

sys.path.insert(0, "runtime")

def move(package, version):
    """Moves package folder into runtime folder.

    Args:
        package (string): Package name.
        version (string): Package version.

    Returns:
        folders (list of strings): List of folder names.
    """
    # installed = "../crawl/installed"
    origin = [folder for folder in os.listdir(
        INSTALLED) if package in folder and version in folder]
    if origin:
        origin = origin[0]
    else:
        return
    folders = os.listdir(f"{INSTALLED}/{origin}")
    print(f"Moving folders: {folders}")
    for folder in folders:
        user_site_packages_path = "runtime"
        destination_path = os.path.join(
            os.getcwd(), user_site_packages_path, folder)
        print(destination_path)
        src = f"{INSTALLED}/{origin}/{folder}"
        if os.path.isdir(src):
            shutil.copytree(src,
                            destination_path)
        elif os.path.isfile(src):
            shutil.copy2(src, destination_path)

    with open(INDEX, 'r') as file:
        index = json.load(file)
    dependencies = index[f"{package}:{version}"]
    for dep_name, dep_version in dependencies:
        dep_folders = move(dep_name, dep_version)
        folders.extend(dep_folders)

    return folders


def remove(folders):
    """Removes package folders from runtime folder.

    Args:
        folders (list of strings): List of folder names.
    """
    print(f"Deleting folders: {folders}")
    for folder in folders:
        # Copy package folder to user-specific site-packages
        # user_site_packages_path = site.USER_SITE
        user_site_packages_path = "runtime"
        if not os.path.exists(user_site_packages_path):
            os.makedirs(user_site_packages_path)
        destination_path = os.path.join(user_site_packages_path, folder)
        if os.path.isdir(destination_path):
            shutil.rmtree(destination_path)
        elif os.path.isfile(destination_path):
            os.remove(destination_path)


def move_and_run(package, version, path, function, parameters):
    folders = move(package, version)
    result = run(path, function, parameters)
    remove(folders)
    return result


def run(path, function, parameters):
    module = importlib.import_module(path)
    func = getattr(module, function)
    result = func(*parameters)
    return result


if __name__ == "__main__":
    package = "urllib3"
    version = "2.2.2"
    path = "urllib3.util.util"
    function = "to_bytes"

    # Prepare arguments for the function
    x = "café"
    encoding = "ascii"
    errors = "ignore"
    args = (x, encoding, errors)

    call = move_and_run(package, version, path, function, args)
    print(call)

    # folders = move("six", "1.16.0")
    # remove(folders)
