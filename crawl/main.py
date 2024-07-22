from install import install, get_most_downloaded
from tqdm import tqdm


if __name__ == '__main__':
    # packages = ["pandas", "numpy", "python-dateutil"]
    packages = ["pandas"]
    # packages = get_all_packages()
    # packages = get_most_downloaded()
    # packages = packages[:20]
    # install(packages)
    print(packages)
    for package in tqdm(packages, desc="Installing Packages"):
        install(package)
