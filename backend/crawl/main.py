from install import installHandler, get_most_downloaded
from nexus import Nexus, Package
from tqdm import tqdm


if __name__ == '__main__':
    nexus = Nexus()
    installHandler = installHandler(nexus)    
    
    packages = ["pandas"]
    # packages = get_all_packages()
    # packages = get_most_downloaded()
    # packages = packages[:20]
    # install(packages)
    
    print(packages)
    for package in tqdm(packages, desc="Installing Packages"):
        installHandler.install(package)
