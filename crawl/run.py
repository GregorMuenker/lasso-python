import importlib
import shutil
import os
import sys
from argparse import ArgumentParser
import site

def move(package):
    folders = [pkg for pkg in os.listdir("installed") if pkg.startswith(package)]
    print(f"Moving folders: {folders}")
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
        shutil.copytree(f"installed/{folder}", destination_path, dirs_exist_ok=True)

def run(package, path, function, parameters):
    move(package)
    module = importlib.import_module(path)
    func = getattr(module, function)
    result = func(*parameters)
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
