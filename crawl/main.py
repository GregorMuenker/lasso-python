from process import unpack_all
from download import download, get_all_packages
from remove import remove_except_python

if __name__ == '__main__':
    # packages = ["pandas", "numpy"]
    packages = get_all_packages()
    packages = packages[-5:]
    for package in packages:
        download(package)
    unpack_all()
    remove_except_python("packages")
