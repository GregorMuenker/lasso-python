import os
import sys

from backend.constants import INSTALLED
from backend.crawl import install, splitting, upload_index


def index_package(package_name):
    """This function provides a pipeline for the steps of crawling and splitting a package. At the last step the
    created index will be uploaded to the solr index.

    :param name: Name of requested pypi package
    """
    installHandler = install.installHandler()
    package_name, version = installHandler.install(package_name)
    installHandler.dump_index()
    sys.path.insert(0, os.path.join(INSTALLED, f"{package_name}-{version}"))
    index = splitting.get_module_index(package_name)
    upload_index.upload_index(index)
    sys.path.remove(os.path.join(INSTALLED, f"{package_name}-{version}"))


if __name__ == "__main__":
    index_package("urllib3")
