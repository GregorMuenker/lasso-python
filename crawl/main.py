from process import unpack_all
from download import download

if __name__ == '__main__':
    packages = ["pandas", "numpy"]
    for package in packages:
        download(package)
    unpack_all()
