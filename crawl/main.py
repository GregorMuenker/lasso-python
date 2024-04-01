from process import unpack_all
from download import download
from remove import remove_except_python

if __name__ == '__main__':
    packages = ["numpy", "pandas"]
    for package in packages:
        download(package)
    unpack_all()
    remove_except_python("packages")
