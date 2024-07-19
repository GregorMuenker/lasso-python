import sys
from crawl import install, run, splitting, upload_index


def index_package(name):
    install.install(name)
    run.move_active(name)
    index = splitting.get_module_index(name)
    upload_index.upload_index(index)
    run.remove_active()


if __name__ == "__main__":
    index_package("numpy")
