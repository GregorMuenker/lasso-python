from process import unpack_all, remove_except_python
from download import download, get_all_packages, get_most_downloaded, create_table

if __name__ == '__main__':
    # packages = ["pandas", "numpy"]
    # packages = get_all_packages()
    packages = get_most_downloaded()
    packages = packages[:50]
    create_table(packages)
    # for package in packages:
    #     download(package)
    # unpack_all()
    # remove_except_python("packages")
