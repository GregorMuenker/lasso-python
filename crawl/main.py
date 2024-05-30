from process import unpack_all, remove_except_python
from download import download, get_all_packages, get_most_downloaded
from versionhandling import create_table

if __name__ == '__main__':
    # packages = ["pandas", "numpy"]
    # packages = get_all_packages()
    packages = get_most_downloaded()
    packages = packages[:20]
    # for package in packages:
    #     download(package)
    # unpack_all()
    # remove_except_python("packages")
    create_table(packages)
