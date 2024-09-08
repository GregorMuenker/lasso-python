import copy
import importlib
import os
import sys

import git
import sys

repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from backend.constants import INSTALLED
from backend.crawl import install, splitting, upload_index, import_helper
from backend.crawl.nexus import Nexus, Package


def index_package(package_name):
    """This function provides a pipeline for the steps of crawling and splitting a package. At the last step the
    created index will be uploaded to the solr index.

    :param name: Name of requested pypi package
    """
    nexus = Nexus()
    install_handler = install.installHandler(nexus)
    package_name, version, already_installed = install_handler.install(package_name)
    if already_installed:
        pkg = Package(package_name, version, f"{package_name}-{version}.tar.gz", f"{package_name}/{version}")
        nexus.download(pkg, runtime=False)
    install_handler.dump_index()
    imp_help = import_helper.ImportHelper()
    imp_help.pre_load_package(package_name, version)
    dependencies = install_handler.index[f"{package_name}:{version}"]
    for dep_name in dependencies:
        dep_version = dependencies[dep_name]['version']
        imp_help.pre_load_package(dep_name, dep_version)
    package_name = import_helper.get_import_name(package_name, version)
    index = splitting.get_module_index(package_name, package_name, version)
    upload_index.upload_index(index)
    #imp_help.unload_package()

if __name__ == "__main__":
    index_package("numpy==2.0.2")
