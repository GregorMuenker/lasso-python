import importlib
import shutil
import os
import sys
from argparse import ArgumentParser
import site
# from versionhandling import get_info


def move(package):
    folders = os.listdir(f"installed/{package}")
    print(f"Moving folders: {folders}")
    for folder in folders:
        # Copy package folder to user-specific site-packages
        if sys.prefix != sys.base_prefix:
            user_site_packages_path = site.getsitepackages()[0]
        else:
            user_site_packages_path = site.USER_SITE
        # print(user_site_packages_path)
        if not os.path.exists(user_site_packages_path):
            os.makedirs(user_site_packages_path)
        destination_path = os.path.join(user_site_packages_path, folder)
        # if os.path.exists(destination_path):
        #     distinfo = [item for item in os.listdir(f"installed/{package}") if item.startswith(package) and item.endswith(".dist-info")][0]
        #     _, installed_version, _ = get_info(f"{package}/{distinfo}", "installed")
        #     # TODO: Get version in site-packages
        #     # TODO: Compare versions and delete site-packages folder if different (simple)
        #     # TODO: Maybe bundle package folder with dist-info folder (?)

        # else:
        #     shutil.copytree(f"installed/{package}/{folder}", destination_path, dirs_exist_ok=True)
        shutil.copytree(f"installed/{package}/{folder}",
                        destination_path, dirs_exist_ok=True)

    return folders


def remove(folders):
    print(f"Deleting folders: {folders}")
    for folder in folders:
        # Copy package folder to site-package folder
        if sys.prefix != sys.base_prefix:
            user_site_packages_path = site.getsitepackages()[0]
        else:
            user_site_packages_path = site.USER_SITE
        # user_site_packages_path = site.USER_SITE
        if not os.path.exists(user_site_packages_path):
            os.makedirs(user_site_packages_path)
        destination_path = os.path.join(user_site_packages_path, folder)
        shutil.rmtree(destination_path)


def move_active(package):
    active_package_folder = "./active"
    print(f"Moving package {package} and depencies")
    shutil.copytree(f"installed/{package}", active_package_folder, dirs_exist_ok=True)
    if active_package_folder not in sys.path:
        sys.path.append(active_package_folder)

def remove_active():
    print(f"Removing active packages")
    active_package_folder = "./active"
    shutil.rmtree(active_package_folder)
    if active_package_folder in sys.path:
        sys.path.remove(active_package_folder)

def run(package, path, function, parameters):
    folders = move(package)
    module = importlib.import_module(path)
    func = getattr(module, function)
    result = func(*parameters)
    remove(folders)
    return result


if __name__ == "__main__":
    package = "urllib3"
    path = "urllib3.util.util"
    function = "to_bytes"

    # Prepare arguments for the function
    x = "café"
    encoding = "ascii"
    errors = "ignore"
    args = (x, encoding, errors)

    call = run(package, path, function, args)
    print(call)
