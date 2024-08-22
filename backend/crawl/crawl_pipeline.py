import sys
from backend.crawl import install, splitting, upload_index


def index_package(name):
    """This function provides a pipeline for the steps of crawling and splitting a package. At the last step the
    created index will be uploaded to the solr index.

    :param name: Name of requested pypi package
    """
    installHandler = install.installHandler()
    name, version = installHandler.install(name)
    installHandler.dump_index()
    run.move_active(f"{name}-{version}")
    index = splitting.get_module_index(name)
    upload_index.upload_index(index)
    run.remove_active()


if __name__ == "__main__":
    index_package("urllib3")
