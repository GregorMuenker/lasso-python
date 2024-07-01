# from process import unpack_all, remove_except_python
from download import download, get_all_packages, get_most_downloaded
# from versionhandling import create_table
from install import install
from tqdm import tqdm


if __name__ == '__main__':
    # packages = ["pandas", "numpy"]
    # packages = get_all_packages()s
    packages = get_most_downloaded()
    # packages = packages[:20]
    install(packages[15])
    # print(packages)
    # for package in tqdm(packages, desc="Installing Packages"):
    #     # download(package)
    #     print(f"Installing {package}")
    #     install(package)
    # unpack_all()
    # remove_except_python("packages")
    # create_table(packages)
