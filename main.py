import sys
from crawl import install, run, splitting, upload_index


def index_package(name):
    install.install(name)
    folders = run.move(name)
    index = splitting.get_module_index(name)
    run.remove(folders)
    upload_index.upload_index(index)


if __name__ == "__main__":
    index_package("numpy")
