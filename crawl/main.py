from process import unpack_all, remove_except_python
from download import download, get_all_packages

if __name__ == '__main__':
    # packages = ["pandas", "numpy"]
    packages = get_all_packages()
    packages = packages[-20:]
    for package in packages:
        download(package)
    unpack_all()
    # remove_except_python("packages")
